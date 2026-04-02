"""Integration tests for application wiring and DI bootstrap."""

from unittest.mock import MagicMock

import pytest

from src.main.python.application import AppDependencies, Application


@pytest.fixture
def mock_root():
	"""Minimal mock standing in for ctk.CTk."""
	root = MagicMock()
	root.winfo_children.return_value = []
	return root


@pytest.fixture
def mock_pygame():
	"""Minimal mock for the pygame module."""
	pg = MagicMock()
	pg.mixer.music = MagicMock()
	return pg


@pytest.fixture
def deps(mock_root, mock_pygame):
	"""Build real presenters wired to real sessions, but with a mock root."""
	from src.main.python.controllers.flashcard_controller import FlashcardPresenter
	from src.main.python.controllers.test_controller import TestPresenter
	from src.main.python.controllers.translation_controller import TranslationPresenter
	from src.main.python.controllers.translation_sandbox_controller import (
		TranslationSandboxPresenter,
	)
	from src.main.python.services import (
		AudioCache,
		create_flashcard_resources,
		create_test_session,
		create_translation_resources,
	)

	tr = create_translation_resources()
	fr = create_flashcard_resources()
	audio_cache = AudioCache(static_map=fr.audio_map)

	return AppDependencies(
		root=mock_root,
		pygame_module=mock_pygame,
		flashcard_presenter=FlashcardPresenter(sessions=fr.sessions, audio_cache=audio_cache),
		translation_presenter=TranslationPresenter(
			morse_session=tr.morse_to_text,
			text_session=tr.text_to_morse,
			audio_cache=audio_cache,
		),
		test_presenter=TestPresenter(create_test_session()),
		sandbox_presenter=TranslationSandboxPresenter(),
	)


class TestApplicationWiring:
	"""Verify that build_application() produces a fully-wired Application."""

	def test_build_application_returns_application(self, deps):
		app = Application(
			deps.root,
			pygame_module=deps.pygame_module,
			flashcard_presenter=deps.flashcard_presenter,
			translation_presenter=deps.translation_presenter,
			test_presenter=deps.test_presenter,
			sandbox_presenter=deps.sandbox_presenter,
		)
		assert isinstance(app, Application)

	def test_presenters_are_assigned(self, deps):
		app = Application(
			deps.root,
			pygame_module=deps.pygame_module,
			flashcard_presenter=deps.flashcard_presenter,
			translation_presenter=deps.translation_presenter,
			test_presenter=deps.test_presenter,
			sandbox_presenter=deps.sandbox_presenter,
		)
		assert app.flashcard_presenter is deps.flashcard_presenter
		assert app.translation_presenter is deps.translation_presenter
		assert app.test_presenter is deps.test_presenter
		assert app.translation_sandbox_presenter is deps.sandbox_presenter

	def test_views_initially_none(self, deps):
		app = Application(
			deps.root,
			pygame_module=deps.pygame_module,
			flashcard_presenter=deps.flashcard_presenter,
			translation_presenter=deps.translation_presenter,
			test_presenter=deps.test_presenter,
			sandbox_presenter=deps.sandbox_presenter,
		)
		assert app.home_view is None
		assert app.flashcard_view is None
		assert app.translation_view is None
		assert app.test_view is None
		assert app.translation_sandbox_view is None
		assert app.introduction_view is None

	def test_attach_views_sets_all_views(self, deps):
		app = Application(
			deps.root,
			pygame_module=deps.pygame_module,
			flashcard_presenter=deps.flashcard_presenter,
			translation_presenter=deps.translation_presenter,
			test_presenter=deps.test_presenter,
			sandbox_presenter=deps.sandbox_presenter,
		)
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

	def test_clear_screen_destroys_children(self, deps, mock_root):
		child1 = MagicMock()
		child2 = MagicMock()
		mock_root.winfo_children.return_value = [child1, child2]

		app = Application(
			deps.root,
			pygame_module=deps.pygame_module,
			flashcard_presenter=deps.flashcard_presenter,
			translation_presenter=deps.translation_presenter,
			test_presenter=deps.test_presenter,
			sandbox_presenter=deps.sandbox_presenter,
		)
		app.clear_screen()

		child1.destroy.assert_called_once()
		child2.destroy.assert_called_once()

	def test_avalehekülg_calls_home_show(self, deps):
		app = Application(
			deps.root,
			pygame_module=deps.pygame_module,
			flashcard_presenter=deps.flashcard_presenter,
			translation_presenter=deps.translation_presenter,
			test_presenter=deps.test_presenter,
			sandbox_presenter=deps.sandbox_presenter,
		)
		mock_home = MagicMock()
		app.home_view = mock_home
		app.avalehekülg()
		mock_home.show.assert_called_once()

	def test_avalehekülg_without_home_view_is_noop(self, deps, mock_root):
		app = Application(
			deps.root,
			pygame_module=deps.pygame_module,
			flashcard_presenter=deps.flashcard_presenter,
			translation_presenter=deps.translation_presenter,
			test_presenter=deps.test_presenter,
			sandbox_presenter=deps.sandbox_presenter,
		)
		app.home_view = None
		app.avalehekülg()
		# No crash, no view shown – just resets state

	def test_tutvustus_calls_introduction_show(self, deps):
		app = Application(
			deps.root,
			pygame_module=deps.pygame_module,
			flashcard_presenter=deps.flashcard_presenter,
			translation_presenter=deps.translation_presenter,
			test_presenter=deps.test_presenter,
			sandbox_presenter=deps.sandbox_presenter,
		)
		mock_intro = MagicMock()
		app.introduction_view = mock_intro
		app.tutvustus()
		mock_intro.show.assert_called_once()

	def test_reset_flashcard_state_calls_view_reset(self, deps):
		app = Application(
			deps.root,
			pygame_module=deps.pygame_module,
			flashcard_presenter=deps.flashcard_presenter,
			translation_presenter=deps.translation_presenter,
			test_presenter=deps.test_presenter,
			sandbox_presenter=deps.sandbox_presenter,
		)
		mock_view = MagicMock()
		app.flashcard_view = mock_view
		app.reset_flashcard_state()
		mock_view.reset_state.assert_called_once()

	def test_reset_test_state_calls_view_reset(self, deps):
		app = Application(
			deps.root,
			pygame_module=deps.pygame_module,
			flashcard_presenter=deps.flashcard_presenter,
			translation_presenter=deps.translation_presenter,
			test_presenter=deps.test_presenter,
			sandbox_presenter=deps.sandbox_presenter,
		)
		mock_view = MagicMock()
		app.test_view = mock_view
		app.reset_test_state()
		mock_view.reset_state.assert_called_once()
