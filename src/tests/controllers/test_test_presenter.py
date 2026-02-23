"""Tests for TestPresenter controller."""
import pytest
from unittest.mock import Mock, PropertyMock
from src.main.python.controllers.test_controller import TestPresenter, TestQuestionState
from src.main.python.model.test_session import TestSession, TestSummary, TestResponse


@pytest.fixture
def mock_session():
    """Create a mock TestSession."""
    session = Mock(spec=TestSession)
    session.total_questions = 3
    session.answered_count = 0
    session.current_prompt.return_value = "HELLO"
    session.current_answer.return_value = ""
    session.current_position.return_value = 0
    session.has_next_question.return_value = True
    session.has_previous_question.return_value = False
    return session


@pytest.fixture
def presenter(mock_session):
    """Create a TestPresenter with mock session."""
    return TestPresenter(mock_session)


class TestTestPresenterInit:
    """Tests for TestPresenter initialization."""

    def test_init_stores_session(self, presenter, mock_session):
        assert presenter._session is mock_session

    def test_total_questions_delegates(self, presenter, mock_session):
        mock_session.total_questions = 5
        assert presenter.total_questions() == 5

    def test_answered_count_delegates(self, presenter, mock_session):
        mock_session.answered_count = 2
        assert presenter.answered_count() == 2


class TestTestPresenterActivePrompt:
    """Tests for active prompt handling."""

    def test_has_active_prompt_true(self, presenter, mock_session):
        mock_session.current_prompt.return_value = "HELLO"
        assert presenter.has_active_prompt()

    def test_has_active_prompt_false(self, presenter, mock_session):
        mock_session.current_prompt.return_value = None
        assert not presenter.has_active_prompt()


class TestTestPresenterCurrentState:
    """Tests for current_state method."""

    def test_returns_test_question_state(self, presenter):
        state = presenter.current_state()
        assert isinstance(state, TestQuestionState)

    def test_state_includes_prompt(self, presenter, mock_session):
        mock_session.current_prompt.return_value = "TEST"
        state = presenter.current_state()
        assert state.prompt == "TEST"

    def test_state_progress_calculation(self, presenter, mock_session):
        mock_session.total_questions = 10
        mock_session.answered_count = 5
        state = presenter.current_state()
        assert state.progress_value == 50.0

    def test_current_state_without_prompt_raises(self, presenter, mock_session):
        mock_session.current_prompt.return_value = None
        with pytest.raises(RuntimeError, match="No active prompt"):
            presenter.current_state()


class TestTestPresenterRecordAnswer:
    """Tests for recording answers."""

    def test_record_answer_calls_session(self, presenter, mock_session):
        presenter.record_answer("my answer", 5.0)
        mock_session.record_response.assert_called_once_with("my answer", 5.0)

    def test_record_answer_clears_summary_cache(self, presenter, mock_session):
        presenter._summary = Mock()
        presenter.record_answer("answer", 1.0)
        assert presenter._summary is None

    def test_record_answer_without_prompt_raises(self, presenter, mock_session):
        mock_session.current_prompt.return_value = None
        with pytest.raises(RuntimeError, match="without an active prompt"):
            presenter.record_answer("answer", 1.0)


class TestTestPresenterNavigation:
    """Tests for navigation methods."""

    def test_move_next_calls_session(self, presenter, mock_session):
        mock_session.next_question.return_value = "WORLD"
        state = presenter.move_next()
        mock_session.next_question.assert_called_once()
        assert isinstance(state, TestQuestionState)

    def test_move_previous_calls_session(self, presenter, mock_session):
        mock_session.previous_question.return_value = "HELLO"
        state = presenter.move_previous()
        mock_session.previous_question.assert_called_once()

    def test_can_move_next_delegates(self, presenter, mock_session):
        mock_session.has_next_question.return_value = True
        assert presenter.can_move_next()
        mock_session.has_next_question.return_value = False
        assert not presenter.can_move_next()

    def test_can_move_previous_delegates(self, presenter, mock_session):
        mock_session.has_previous_question.return_value = True
        assert presenter.can_move_previous()


class TestTestPresenterAllAnswered:
    """Tests for all_answered state."""

    def test_all_answered_delegates(self, presenter, mock_session):
        mock_session.all_answered.return_value = True
        assert presenter.all_answered()
        mock_session.all_answered.return_value = False
        assert not presenter.all_answered()


class TestTestPresenterSummary:
    """Tests for summary generation."""

    def test_summary_returns_test_summary(self, presenter, mock_session):
        mock_summary = Mock(spec=TestSummary)
        mock_session.summary.return_value = mock_summary
        result = presenter.summary()
        assert result is mock_summary

    def test_summary_is_cached(self, presenter, mock_session):
        mock_summary = Mock(spec=TestSummary)
        mock_session.summary.return_value = mock_summary
        presenter.summary()
        presenter.summary()
        # Should only call session.summary() once due to caching
        mock_session.summary.assert_called_once()

    def test_responses_uses_summary(self, presenter, mock_session):
        mock_responses = [Mock(spec=TestResponse)]
        mock_summary = Mock(spec=TestSummary)
        mock_summary.responses = mock_responses
        mock_session.summary.return_value = mock_summary
        result = presenter.responses()
        assert result is mock_responses


class TestTestPresenterReset:
    """Tests for reset method."""

    def test_reset_calls_session_reset(self, presenter, mock_session):
        presenter.reset()
        mock_session.reset.assert_called_once()

    def test_reset_clears_summary_cache(self, presenter, mock_session):
        presenter._summary = Mock()
        presenter.reset()
        assert presenter._summary is None


class TestTestQuestionState:
    """Tests for TestQuestionState dataclass."""

    def test_state_is_frozen(self):
        state = TestQuestionState(
            prompt="A",
            answered=1,
            total=3,
            progress_value=33.3,
            progress_step=33.3,
            progress_text="33.3% läbitud",
            question_number=1,
            existing_answer="",
            has_previous=False,
            has_next=True,
        )
        with pytest.raises(AttributeError):
            state.prompt = "B"
