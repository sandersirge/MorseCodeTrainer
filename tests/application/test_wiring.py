"""Integration tests for application wiring and DI bootstrap."""

from unittest.mock import MagicMock

import pytest

from morsetrainer.application import AppDependencies, Application


@pytest.fixture
def mock_root():
	"""Minimal mock standing in for ctk.CTk."""
	root = MagicMock()
	root.winfo_children.return_value = []
	return root


@pytest.fixture(autouse=True)
def no_real_window(monkeypatch):
	"""Window sizing/scaling needs a real Tk screen; replace it here."""
	monkeypatch.setattr("morsetrainer.application.MainWindow", MagicMock())


@pytest.fixture
def deps(mock_root):
	"""Build real presenters wired to real sessions, but with a mock root and player."""
	from morsetrainer.controllers.flashcard_controller import FlashcardPresenter
	from morsetrainer.controllers.test_controller import TestPresenter
	from morsetrainer.controllers.translation_controller import TranslationPresenter
	from morsetrainer.controllers.translation_sandbox_controller import (
		TranslationSandboxPresenter,
	)
	from morsetrainer.services import (
		create_flashcard_resources,
		create_test_session,
		create_translation_resources,
	)

	tr = create_translation_resources()
	fr = create_flashcard_resources()

	return AppDependencies(
		root=mock_root,
		audio_player=MagicMock(),
		flashcard_presenter=FlashcardPresenter(sessions=fr.sessions),
		translation_presenter=TranslationPresenter(
			morse_session=tr.morse_to_text,
			text_session=tr.text_to_morse,
		),
		test_presenter=TestPresenter(create_test_session()),
		sandbox_presenter=TranslationSandboxPresenter(),
	)


@pytest.fixture
def app(deps):
	return Application(
		deps.root,
		audio_player=deps.audio_player,
		flashcard_presenter=deps.flashcard_presenter,
		translation_presenter=deps.translation_presenter,
		test_presenter=deps.test_presenter,
		sandbox_presenter=deps.sandbox_presenter,
	)


class TestApplicationWiring:
	"""Verify that Application is fully wired."""

	def test_build_application_returns_application(self, app):
		assert isinstance(app, Application)

	def test_presenters_are_assigned(self, app, deps):
		assert app.flashcard_presenter is deps.flashcard_presenter
		assert app.translation_presenter is deps.translation_presenter
		assert app.test_presenter is deps.test_presenter
		assert app.translation_sandbox_presenter is deps.sandbox_presenter

	def test_window_is_set_up_with_title(self, app):
		app.window.setup.assert_called_once()

	def test_closing_window_shuts_down_audio(self, app, deps, mock_root):
		mock_root.protocol.assert_called_once_with("WM_DELETE_WINDOW", app.quit)
		app.quit()
		deps.audio_player.shutdown.assert_called_once()
		mock_root.destroy.assert_called_once()

	def test_views_initially_none(self, app):
		assert app.home_view is None
		assert app.flashcard_view is None
		assert app.translation_view is None
		assert app.test_view is None
		assert app.translation_sandbox_view is None
		assert app.introduction_view is None

	def test_attach_views_sets_all_views(self, app):
		views = {
			"home_view": MagicMock(),
			"introduction_view": MagicMock(),
			"flashcard_view": MagicMock(),
			"translation_view": MagicMock(),
			"translation_sandbox_view": MagicMock(),
			"test_view": MagicMock(),
		}
		app.attach_views(view_stack=MagicMock(), **views)

		assert app.home_view is views["home_view"]
		assert app.introduction_view is views["introduction_view"]
		assert app.flashcard_view is views["flashcard_view"]
		assert app.translation_view is views["translation_view"]
		assert app.translation_sandbox_view is views["translation_sandbox_view"]
		assert app.test_view is views["test_view"]

	def test_clear_screen_destroys_children(self, app, mock_root):
		child1 = MagicMock()
		child2 = MagicMock()
		mock_root.winfo_children.return_value = [child1, child2]
		app.clear_screen()
		child1.destroy.assert_called_once()
		child2.destroy.assert_called_once()

	def test_show_home_calls_home_show(self, app):
		app.home_view = MagicMock()
		app.show_home()
		app.home_view.show.assert_called_once()

	def test_show_home_without_home_view_is_noop(self, app):
		app.home_view = None
		app.show_home()  # No crash, no view shown – just resets state

	def test_show_introduction_calls_introduction_show(self, app):
		app.introduction_view = MagicMock()
		app.show_introduction()
		app.introduction_view.show.assert_called_once()

	def test_show_translation_stops_audio(self, app, deps):
		app.translation_view = MagicMock()
		app.show_translation()
		deps.audio_player.stop.assert_called()
		app.translation_view.show_menu.assert_called_once()

	def test_reset_flashcard_state_calls_view_reset(self, app):
		app.flashcard_view = MagicMock()
		app.reset_flashcard_state()
		app.flashcard_view.reset_state.assert_called_once()

	def test_reset_test_state_calls_view_reset(self, app):
		app.test_view = MagicMock()
		app.reset_test_state()
		app.test_view.reset_state.assert_called_once()
