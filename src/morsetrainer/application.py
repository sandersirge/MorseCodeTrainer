from __future__ import annotations

import random
from collections.abc import Generator
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
from .views.hub_view import HubOption, HubView
from .views.keyer_view import KeyerView
from .views.koch_view import KochView
from .views.test_view import TestView
from .views.translation_sandbox_view import TranslationSandboxView
from .views.translation_view import TranslationView
from .views.window import MainWindow

APP_TITLE = t("app.morsekoodi_oppimisprogramm")

# Depth in the menu tree decides the slide direction of screen changes.
SCREEN_DEPTHS = {
	"home": 0,
	"introduction": 1,
	"learn_hub": 1,
	"practice_hub": 1,
	"test": 1,
	"sandbox": 1,
	"flashcard": 2,
	"koch": 2,
	"translation": 2,
	"keyer": 2,
}


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
		window: MainWindow | None = None,
	) -> None:
		self.root = root
		self.audio = audio_player
		self.flashcard_presenter = flashcard_presenter
		self.translation_presenter = translation_presenter
		self.test_presenter = test_presenter
		self.translation_sandbox_presenter = sandbox_presenter
		self.koch_presenter = koch_presenter
		self.keyer_presenter = keyer_presenter
		self.view_stack: ViewStack | None = None
		self.home_view: HomeView | None = None
		self.introduction_view: IntroductionView | None = None
		self.flashcard_view: FlashcardView | None = None
		self.translation_view: TranslationView | None = None
		self.translation_sandbox_view: TranslationSandboxView | None = None
		self.test_view: TestView | None = None
		self.koch_view: KochView | None = None
		self.keyer_view: KeyerView | None = None
		self.learn_hub: HubView | None = None
		self.practice_hub: HubView | None = None

		if window is None:
			window = MainWindow(root)
			window.setup(APP_TITLE)
		self.window = window
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
		learn_hub: HubView | None = None,
		practice_hub: HubView | None = None,
	) -> None:
		self.view_stack = view_stack
		self.home_view = home_view
		self.introduction_view = introduction_view
		self.flashcard_view = flashcard_view
		self.translation_view = translation_view
		self.translation_sandbox_view = translation_sandbox_view
		self.test_view = test_view
		self.koch_view = koch_view
		self.keyer_view = keyer_view
		self.learn_hub = learn_hub
		self.practice_hub = practice_hub
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

	def _switch(self, name: str, build, *, animated: bool = True) -> None:
		"""Build the screen first, then slide it in.

		Building CTk widgets takes a moment; doing it before the slide starts
		keeps the whole 200 ms of motion visible instead of eating into it.
		"""
		if build is None:
			return
		build()
		if self.view_stack is not None:
			self.view_stack.show(name, animated=animated)

	@staticmethod
	def _builder(view, method: str):
		return getattr(view, method) if view is not None else None

	# Navigation targets -----------------------------------------------------

	def show_home(self, animated: bool = True) -> None:
		self.audio.stop()
		self._reset_all()
		self._switch("home", self._builder(self.home_view, "show"), animated=animated)

	def show_introduction(self) -> None:
		self._reset_all()
		self._switch("introduction", self._builder(self.introduction_view, "show"))

	def show_learn_hub(self) -> None:
		self.audio.stop()
		self._reset_all()
		self._switch("learn_hub", self._builder(self.learn_hub, "show"))

	def show_practice_hub(self) -> None:
		self.audio.stop()
		self._reset_all()
		self._switch("practice_hub", self._builder(self.practice_hub, "show"))

	def show_flashcards(self) -> None:
		self._switch("flashcard", self._builder(self.flashcard_view, "show_menu"))

	def show_translation(self) -> None:
		self.audio.stop()
		self.reset_translation_state()
		self._switch("translation", self._builder(self.translation_view, "show_menu"))

	def show_translation_sandbox(self) -> None:
		self.audio.stop()
		self._switch("sandbox", self._builder(self.translation_sandbox_view, "show"))

	def show_koch(self) -> None:
		self._switch("koch", self._builder(self.koch_view, "show"))

	def show_keyer(self) -> None:
		self._switch("keyer", self._builder(self.keyer_view, "show"))

	def show_test(self) -> None:
		self._switch("test", self._builder(self.test_view, "show_menu"))


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


BuildSteps = Generator[tuple[str, float], None, Application]


def build_steps(
	*,
	root: ctk.CTk | None = None,
	root_factory: RootFactory | None = None,
	pygame_module=None,
	window: MainWindow | None = None,
) -> BuildSteps:
	"""Build the app in stages, yielding (status text, progress 0..1) after each.

	The loading screen runs these one at a time so it can repaint in between;
	``build_application`` simply runs them all.
	"""
	if root is None:
		root = (root_factory or ctk.CTk)()

	yield t("splash.audio"), 0.1
	# Saved progress also remembers the audio settings between runs.
	progress = ProgressStore()
	settings_store = AudioSettingsStore(progress.audio_settings())
	settings_store.subscribe(progress.save_audio_settings)
	audio_player = AudioPlayer(pygame_module or pygame, settings_store)
	audio_player.start()

	yield t("splash.data"), 0.3
	translation_resources = create_translation_resources()
	flashcard_resources = create_flashcard_resources()
	deps = AppDependencies(
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
	app = Application(
		root,
		audio_player=deps.audio_player,
		flashcard_presenter=deps.flashcard_presenter,
		translation_presenter=deps.translation_presenter,
		test_presenter=deps.test_presenter,
		sandbox_presenter=deps.sandbox_presenter,
		koch_presenter=deps.koch_presenter,
		keyer_presenter=deps.keyer_presenter,
		window=window,
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
		learn_hub=app.show_learn_hub,
		practice_hub=app.show_practice_hub,
	)

	yield t("splash.screens"), 0.55
	view_stack = ViewStack(root)
	views = _build_views(nav, deps, view_stack)

	yield t("splash.ready"), 0.9
	app.attach_views(view_stack=view_stack, **views)
	return app


def build_application(
	*, root_factory: RootFactory | None = None, pygame_module=None
) -> Application:
	"""Build everything at once (no loading screen)."""
	steps = build_steps(root_factory=root_factory, pygame_module=pygame_module)
	while True:
		try:
			next(steps)
		except StopIteration as finished:
			return finished.value


def launch() -> None:
	"""Start the app with a loading screen, then fade/slide to the home screen."""
	from .views.splash import SplashScreen, fade_in_window
	from .views.theme import set_appearance_mode, system_appearance_mode

	root = ctk.CTk()
	mode = system_appearance_mode()
	ctk.set_appearance_mode(mode)
	set_appearance_mode(mode)
	window = MainWindow(root)
	window.setup(APP_TITLE)
	splash = SplashScreen(root)
	steps = build_steps(root=root, window=window)

	def advance() -> None:
		try:
			status, fraction = next(steps)
		except StopIteration as finished:
			app: Application = finished.value
			splash.update(t("splash.ready"), 1.0)
			app.show_home(animated=False)
			splash.finish()
			return
		splash.update(status, fraction)
		# A short pause lets Tk repaint the loading screen between stages.
		root.after(30, advance)

	fade_in_window(root)
	root.after(80, advance)
	root.mainloop()


def _build_views(nav: Navigator, deps: AppDependencies, view_stack: ViewStack) -> dict[str, object]:
	audio = deps.audio_player

	def frame(name: str):
		return view_stack.register(name, depth=SCREEN_DEPTHS.get(name, 1))

	return {
		"flashcard_view": FlashcardView(
			root=frame("flashcard"),
			nav=nav,
			audio_player=audio,
			presenter=deps.flashcard_presenter,
		),
		"translation_view": TranslationView(
			root=frame("translation"),
			nav=nav,
			audio_player=audio,
			presenter=deps.translation_presenter,
		),
		"translation_sandbox_view": TranslationSandboxView(
			root=frame("sandbox"),
			nav=nav,
			audio_player=audio,
			presenter=deps.sandbox_presenter,
		),
		"test_view": TestView(
			root=frame("test"),
			nav=nav,
			audio_player=audio,
			presenter=deps.test_presenter,
		),
		"koch_view": KochView(
			root=frame("koch"), nav=nav, audio_player=audio, presenter=deps.koch_presenter
		)
		if deps.koch_presenter
		else None,
		"keyer_view": KeyerView(
			root=frame("keyer"), nav=nav, audio_player=audio, presenter=deps.keyer_presenter
		)
		if deps.keyer_presenter
		else None,
		"learn_hub": HubView(
			frame("learn_hub"),
			title=t("hub.learn_title"),
			subtitle=t("hub.learn_subtitle"),
			options=[
				HubOption(t("home.ope_cards"), t("hub.cards_description"), nav.flashcards, "A  ·—"),
				HubOption(t("home.koch"), t("hub.koch_description"), nav.koch, "♪ ·—·"),
			],
			back=nav.home,
		),
		"practice_hub": HubView(
			frame("practice_hub"),
			title=t("hub.practice_title"),
			subtitle=t("hub.practice_subtitle"),
			options=[
				HubOption(
					t("home.translation"),
					t("hub.translation_description"),
					nav.translation,
					"A ⇄ ·—",
				),
				HubOption(t("home.keyer"), t("hub.keyer_description"), nav.keyer, "⌨ —·—"),
			],
			back=nav.home,
		),
		"home_view": HomeView(root=frame("home"), nav=nav),
		"introduction_view": IntroductionView(root=frame("introduction"), nav=nav),
	}
