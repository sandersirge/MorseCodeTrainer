from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol

import customtkinter as ctk

from .controllers.flashcard_controller import FlashcardPresenter
from .controllers.keyer_controller import KeyerPresenter
from .controllers.koch_controller import KochPresenter
from .controllers.test_controller import TestPresenter
from .controllers.translation_controller import TranslationPresenter
from .controllers.translation_sandbox_controller import TranslationSandboxPresenter
from .model.training import word_drill
from .navigator import Navigator
from .resources.word_list import WORDS_ET
from .services import (
	AudioPlayer,
	AudioSettingsStore,
	create_flashcard_resources,
	create_test_session,
	create_translation_resources,
	pygame,
)
from .services.progress_store import ProgressStore
from .strings import t
from .view_stack import ViewStack
from .views.flashcard_view import FlashcardView
from .views.home_view import HomeView, IntroductionView
from .views.keyer_view import KeyerView
from .views.koch_view import KochView
from .views.test_view import TestView
from .views.translation_sandbox_view import TranslationSandboxView
from .views.translation_view import TranslationView
from .views.window import MainWindow

APP_TITLE = t("app.morsekoodi_oppimisprogramm")


class Application:
	"""Coordinates UI screens and shared presenters for the program."""

	def __init__(
		self,
		root: ctk.CTk,
		*,
		audio_player: AudioPlayer,
		flashcard_presenter: FlashcardPresenter,
		translation_presenter: TranslationPresenter,
		test_presenter: TestPresenter,
		sandbox_presenter: TranslationSandboxPresenter,
		koch_presenter: KochPresenter | None = None,
		keyer_presenter: KeyerPresenter | None = None,
	) -> None:
		self.root = root
		self.koch_presenter = koch_presenter
		self.keyer_presenter = keyer_presenter
		self.koch_view: KochView | None = None
		self.keyer_view: KeyerView | None = None
		self.audio = audio_player
		self.flashcard_presenter = flashcard_presenter
		self.translation_presenter = translation_presenter
		self.test_presenter = test_presenter
		self.translation_sandbox_presenter = sandbox_presenter
		self.view_stack: ViewStack | None = None
		self.home_view: HomeView | None = None
		self.introduction_view: IntroductionView | None = None
		self.flashcard_view: FlashcardView | None = None
		self.translation_view: TranslationView | None = None
		self.translation_sandbox_view: TranslationSandboxView | None = None
		self.test_view: TestView | None = None

		self.window = MainWindow(root)
		self.window.setup(APP_TITLE)
		self.root.protocol("WM_DELETE_WINDOW", self.quit)

	# Wiring -----------------------------------------------------------------

	def attach_views(
		self,
		*,
		view_stack: ViewStack,
		home_view: HomeView,
		introduction_view: IntroductionView,
		flashcard_view: FlashcardView,
		translation_view: TranslationView,
		translation_sandbox_view: TranslationSandboxView,
		test_view: TestView,
		koch_view: KochView | None = None,
		keyer_view: KeyerView | None = None,
	) -> None:
		self.view_stack = view_stack
		self.koch_view = koch_view
		self.keyer_view = keyer_view
		self.home_view = home_view
		self.introduction_view = introduction_view
		self.flashcard_view = flashcard_view
		self.translation_view = translation_view
		self.translation_sandbox_view = translation_sandbox_view
		self.test_view = test_view
		self.reset_flashcard_state()
		self.reset_translation_state()
		self.reset_test_state()

	def run(self) -> None:
		self.show_home()
		self.root.mainloop()

	def quit(self) -> None:
		"""Close the audio device before the window, on every platform."""
		self.audio.shutdown()
		self.root.destroy()

	# Shared helpers ---------------------------------------------------------

	def clear_screen(self) -> None:
		for element in self.root.winfo_children():
			element.destroy()

	def reset_flashcard_state(self) -> None:
		if self.flashcard_view is not None:
			self.flashcard_view.reset_state()

	def reset_translation_state(self) -> None:
		self.translation_presenter.reset()
		if self.translation_view is not None:
			self.translation_view.reset_ui()

	def reset_test_state(self) -> None:
		if self.test_view is not None:
			self.test_view.reset_state()

	def _reset_all(self) -> None:
		self.reset_flashcard_state()
		self.reset_translation_state()
		self.reset_test_state()

	# Navigation targets -----------------------------------------------------

	def show_home(self) -> None:
		self._reset_all()
		if self.home_view is None:
			return
		if self.view_stack is not None:
			self.view_stack.show("home")
		self.home_view.show()

	def show_introduction(self) -> None:
		self._reset_all()
		if self.introduction_view is None:
			return
		if self.view_stack is not None:
			self.view_stack.show("introduction")
		self.introduction_view.show()

	def show_flashcards(self) -> None:
		if self.flashcard_view is None:
			return
		if self.view_stack is not None:
			self.view_stack.show("flashcard")
		self.flashcard_view.show_menu()

	def show_translation(self) -> None:
		self.audio.stop()
		self.reset_translation_state()
		if self.translation_view is None:
			return
		if self.view_stack is not None:
			self.view_stack.show("translation")
		self.translation_view.show_menu()

	def show_translation_sandbox(self) -> None:
		self.audio.stop()
		if self.translation_sandbox_view is None:
			return
		if self.view_stack is not None:
			self.view_stack.show("sandbox")
		self.translation_sandbox_view.show()

	def show_koch(self) -> None:
		if self.koch_view is None:
			return
		if self.view_stack is not None:
			self.view_stack.show("koch")
		self.koch_view.show()

	def show_keyer(self) -> None:
		if self.keyer_view is None:
			return
		if self.view_stack is not None:
			self.view_stack.show("keyer")
		self.keyer_view.show()

	def show_test(self) -> None:
		if self.test_view is None:
			return
		if self.view_stack is not None:
			self.view_stack.show("test")
		self.test_view.show_menu()


class RootFactory(Protocol):
	def __call__(self) -> ctk.CTk: ...


@dataclass(frozen=True)
class AppDependencies:
	root: ctk.CTk
	audio_player: AudioPlayer
	flashcard_presenter: FlashcardPresenter
	translation_presenter: TranslationPresenter
	test_presenter: TestPresenter
	sandbox_presenter: TranslationSandboxPresenter
	koch_presenter: KochPresenter | None = None
	keyer_presenter: KeyerPresenter | None = None


def build_application(
	*, root_factory: RootFactory | None = None, pygame_module=None
) -> Application:
	deps = _build_dependencies(root_factory=root_factory, pygame_module=pygame_module)
	app = Application(
		deps.root,
		audio_player=deps.audio_player,
		flashcard_presenter=deps.flashcard_presenter,
		translation_presenter=deps.translation_presenter,
		test_presenter=deps.test_presenter,
		sandbox_presenter=deps.sandbox_presenter,
		koch_presenter=deps.koch_presenter,
		keyer_presenter=deps.keyer_presenter,
	)

	nav = Navigator(
		home=app.show_home,
		introduction=app.show_introduction,
		flashcards=app.show_flashcards,
		translation=app.show_translation,
		translation_sandbox=app.show_translation_sandbox,
		test=app.show_test,
		exit=app.quit,
		reset_translation=app.reset_translation_state,
		koch=app.show_koch,
		keyer=app.show_keyer,
	)

	view_stack = ViewStack(deps.root)
	views = _build_views(nav, deps, view_stack)
	app.attach_views(view_stack=view_stack, **views)
	return app


def _build_dependencies(
	*, root_factory: RootFactory | None = None, pygame_module=None
) -> AppDependencies:
	root_creator = root_factory or ctk.CTk
	root = root_creator()

	# Saved progress also remembers the audio settings between runs.
	progress = ProgressStore()
	settings_store = AudioSettingsStore(progress.audio_settings())
	settings_store.subscribe(progress.save_audio_settings)
	audio_player = AudioPlayer(pygame_module or pygame, settings_store)
	audio_player.start()

	translation_resources = create_translation_resources()
	flashcard_resources = create_flashcard_resources()

	return AppDependencies(
		root=root,
		audio_player=audio_player,
		flashcard_presenter=FlashcardPresenter(
			sessions=flashcard_resources.sessions, progress=progress
		),
		translation_presenter=TranslationPresenter(
			morse_session=translation_resources.morse_to_text,
			text_session=translation_resources.text_to_morse,
			drill_factory=lambda: word_drill(WORDS_ET, progress.weakness, random.Random()),
			progress=progress,
		),
		test_presenter=TestPresenter(create_test_session()),
		sandbox_presenter=TranslationSandboxPresenter(settings_store),
		koch_presenter=KochPresenter(progress),
		keyer_presenter=KeyerPresenter(settings_store, WORDS_ET, progress),
	)


def _build_views(nav: Navigator, deps: AppDependencies, view_stack: ViewStack) -> dict[str, object]:
	audio = deps.audio_player
	return {
		"flashcard_view": FlashcardView(
			root=view_stack.register("flashcard"),
			nav=nav,
			audio_player=audio,
			presenter=deps.flashcard_presenter,
		),
		"translation_view": TranslationView(
			root=view_stack.register("translation"),
			nav=nav,
			audio_player=audio,
			presenter=deps.translation_presenter,
		),
		"translation_sandbox_view": TranslationSandboxView(
			root=view_stack.register("sandbox"),
			nav=nav,
			audio_player=audio,
			presenter=deps.sandbox_presenter,
		),
		"test_view": TestView(
			root=view_stack.register("test"),
			nav=nav,
			audio_player=audio,
			presenter=deps.test_presenter,
		),
		"koch_view": KochView(
			root=view_stack.register("koch"),
			nav=nav,
			audio_player=audio,
			presenter=deps.koch_presenter,
		)
		if deps.koch_presenter
		else None,
		"keyer_view": KeyerView(
			root=view_stack.register("keyer"),
			nav=nav,
			audio_player=audio,
			presenter=deps.keyer_presenter,
		)
		if deps.keyer_presenter
		else None,
		"home_view": HomeView(root=view_stack.register("home"), nav=nav),
		"introduction_view": IntroductionView(root=view_stack.register("introduction"), nav=nav),
	}
