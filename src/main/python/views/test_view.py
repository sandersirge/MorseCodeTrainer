from __future__ import annotations

import customtkinter as ctk

from ..controllers.protocols import TestPresenterProtocol
from ..model.test_session import TestSummary
from ..navigator import Navigator
from .test_menu_screen import TestMenuScreen
from .test_review_screen import TestReviewScreen
from .test_runner_screen import TestRunnerScreen


class TestView:
	"""Facade delegating timed test flows to specialised screens."""

	def __init__(
		self,
		root: ctk.CTk,
		nav: Navigator,
		pygame_module,
		presenter: TestPresenterProtocol,
	) -> None:
		self.root = root
		self.nav = nav
		self.pygame = pygame_module

		self.runner_screen = TestRunnerScreen(
			root,
			self._clear_content,
			presenter,
			pygame_module,
			on_review=self._show_review,
			on_exit_to_menu=self.show_menu,
		)
		self.review_screen = TestReviewScreen(
			root,
			self._clear_content,
			on_back_to_results=self._return_to_results,
		)
		self.menu_screen = TestMenuScreen(
			root,
			self._clear_content,
			presenter,
			nav.home,
			self._start_test_run,
		)

	def _clear_content(self) -> None:
		"""Destroy this view's children without touching other views."""
		for w in self.root.winfo_children():
			w.destroy()

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
