from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from ..controllers.test_controller import TestPresenter
from ..model.test_session import TestSummary
from .test_menu_screen import TestMenuScreen
from .test_review_screen import TestReviewScreen
from .test_runner_screen import TestRunnerScreen


class TestView:
    """Facade delegating timed test flows to specialised screens."""

    def __init__(
        self,
        root: ctk.CTk,
        clear_screen: Callable[[], None],
        on_home: Callable[[], None],
        pygame_module,
        presenter: TestPresenter,
    ) -> None:
        self.root = root
        self.clear_screen = clear_screen
        self.on_home = on_home
        self.pygame = pygame_module

        self.runner_screen = TestRunnerScreen(
            root,
            clear_screen,
            presenter,
            pygame_module,
            on_review=self._show_review,
            on_exit_to_menu=self.show_menu,
        )
        self.review_screen = TestReviewScreen(
            root,
            clear_screen,
            on_back_to_results=self._return_to_results,
        )
        self.menu_screen = TestMenuScreen(
            root,
            clear_screen,
            presenter,
            on_home,
            self._start_test_run,
        )

    def reset_state(self) -> None:
        self.runner_screen.reset()
        self.review_screen.reset()

    def show_menu(self) -> None:
        self.pygame.mixer.music.stop()
        self.reset_state()
        self.menu_screen.show()

    def _start_test_run(self) -> None:
        self.runner_screen.begin()

    def _show_review(self, summary: TestSummary) -> None:
        self.review_screen.show(summary)

    def _return_to_results(self, summary: TestSummary) -> None:
        self.runner_screen.show_results(summary)
