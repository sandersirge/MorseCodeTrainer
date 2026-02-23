from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import customtkinter as ctk

from .controllers.flashcard_controller import FlashcardPresenter
from .controllers.test_controller import TestPresenter
from .controllers.translation_controller import TranslationPresenter
from .controllers.translation_sandbox_controller import TranslationSandboxPresenter
from .services import FlashcardResources, TranslationResources
from .services import create_flashcard_resources, create_test_session, create_translation_resources, pygame
from .views.flashcard_view import FlashcardView
from .views.home_view import HomeView, IntroductionView
from .views.test_view import TestView
from .views.translation_sandbox_view import TranslationSandboxView
from .views.translation_view import TranslationView


class Application:
    """Coordinates UI screens and shared presenters for the program."""

    def __init__(
        self,
        root: ctk.CTk,
        *,
        pygame_module,
        flashcard_presenter: FlashcardPresenter,
        translation_presenter: TranslationPresenter,
        test_presenter: TestPresenter,
        sandbox_presenter: TranslationSandboxPresenter,
    ) -> None:
        self.root = root
        self.pygame = pygame_module
        self.flashcard_presenter = flashcard_presenter
        self.translation_presenter = translation_presenter
        self.test_presenter = test_presenter
        self.translation_sandbox_presenter = sandbox_presenter
        self.home_view: HomeView | None = None
        self.introduction_view: IntroductionView | None = None
        self.flashcard_view: FlashcardView | None = None
        self.translation_view: TranslationView | None = None
        self.translation_sandbox_view: TranslationSandboxView | None = None
        self.test_view: TestView | None = None

        self.root.title("Morsekoodi õppimisprogramm")
        self.root.geometry("1920x1080")
        self.root.configure(fg_color="#FFFDD0")

    # Wiring -----------------------------------------------------------------

    def attach_views(
        self,
        *,
        home_view: HomeView,
        introduction_view: IntroductionView,
        flashcard_view: FlashcardView,
        translation_view: TranslationView,
        translation_sandbox_view: TranslationSandboxView,
        test_view: TestView,
    ) -> None:
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
        self.avalehekülg()
        self.root.mainloop()

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

    def avalehekülg(self) -> None:
        self.reset_flashcard_state()
        self.reset_translation_state()
        self.reset_test_state()
        if self.home_view is None:
            self.clear_screen()
            return
        self.home_view.show()

    def tutvustus(self) -> None:
        self.reset_flashcard_state()
        self.reset_translation_state()
        self.reset_test_state()
        if self.introduction_view is None:
            self.clear_screen()
            return
        self.introduction_view.show()

    def režiim1(self) -> None:
        if self.flashcard_view is not None:
            self.flashcard_view.show_menu()

    def režiim2(self) -> None:
        self.pygame.mixer.music.stop()
        self.reset_translation_state()
        if self.translation_view is not None:
            self.translation_view.show_menu()

    def translation_sandbox(self) -> None:
        self.pygame.mixer.music.stop()
        if self.translation_sandbox_view is None:
            self.clear_screen()
            return
        self.translation_sandbox_view.show()

    def test(self) -> None:
        if self.test_view is None:
            return
        self.test_view.show_menu()


class RootFactory(Protocol):
    def __call__(self) -> ctk.CTk:
        ...


@dataclass(frozen=True)
class AppDependencies:
    root: ctk.CTk
    pygame_module: Any
    flashcard_presenter: FlashcardPresenter
    translation_presenter: TranslationPresenter
    test_presenter: TestPresenter
    sandbox_presenter: TranslationSandboxPresenter


def build_application(*, root_factory: RootFactory | None = None) -> Application:
    deps = _build_dependencies(root_factory=root_factory)
    app = Application(
        deps.root,
        pygame_module=deps.pygame_module,
        flashcard_presenter=deps.flashcard_presenter,
        translation_presenter=deps.translation_presenter,
        test_presenter=deps.test_presenter,
        sandbox_presenter=deps.sandbox_presenter,
    )

    views = _build_views(app, deps)
    app.attach_views(**views)
    return app


def _build_dependencies(*, root_factory: RootFactory | None = None) -> AppDependencies:
    root_creator = root_factory or ctk.CTk
    root = root_creator()
    pygame.mixer.init()

    translation_resources: TranslationResources = create_translation_resources()
    translation_presenter = TranslationPresenter(
        morse_session=translation_resources.morse_to_text,
        text_session=translation_resources.text_to_morse,
        audio_map=translation_resources.audio_map,
    )

    sandbox_presenter = TranslationSandboxPresenter()
    test_presenter = TestPresenter(create_test_session())

    flashcard_resources: FlashcardResources = create_flashcard_resources()
    flashcard_presenter = FlashcardPresenter(
        sessions=flashcard_resources.sessions,
        audio_map=flashcard_resources.audio_map,
    )

    return AppDependencies(
        root=root,
        pygame_module=pygame,
        flashcard_presenter=flashcard_presenter,
        translation_presenter=translation_presenter,
        test_presenter=test_presenter,
        sandbox_presenter=sandbox_presenter,
    )


def _build_views(app: Application, deps: AppDependencies) -> dict[str, object]:
    flashcard_view = FlashcardView(
        root=deps.root,
        clear_screen=app.clear_screen,
        on_home=app.avalehekülg,
        pygame_module=deps.pygame_module,
        presenter=deps.flashcard_presenter,
    )

    translation_view = TranslationView(
        root=deps.root,
        clear_screen=app.clear_screen,
        on_home=app.avalehekülg,
        on_reset=app.reset_translation_state,
        pygame_module=deps.pygame_module,
        presenter=deps.translation_presenter,
    )

    translation_sandbox_view = TranslationSandboxView(
        root=deps.root,
        clear_screen=app.clear_screen,
        on_home=app.avalehekülg,
        pygame_module=deps.pygame_module,
        presenter=deps.sandbox_presenter,
    )

    test_view = TestView(
        root=deps.root,
        clear_screen=app.clear_screen,
        on_home=app.avalehekülg,
        pygame_module=deps.pygame_module,
        presenter=deps.test_presenter,
    )

    home_view = HomeView(
        root=deps.root,
        clear_screen=app.clear_screen,
        on_tutvustus=app.tutvustus,
        on_flashcards=app.režiim1,
        on_translation=app.režiim2,
        on_translation_sandbox=app.translation_sandbox,
        on_test=app.test,
        on_exit=deps.root.destroy,
    )

    introduction_view = IntroductionView(
        root=deps.root,
        clear_screen=app.clear_screen,
        on_back=app.avalehekülg,
    )

    return {
        "home_view": home_view,
        "introduction_view": introduction_view,
        "flashcard_view": flashcard_view,
        "translation_view": translation_view,
        "translation_sandbox_view": translation_sandbox_view,
        "test_view": test_view,
    }