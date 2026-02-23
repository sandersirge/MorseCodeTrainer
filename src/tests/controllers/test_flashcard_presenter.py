"""Tests for FlashcardPresenter controller."""
import pytest
from unittest.mock import Mock
from src.main.python.controllers.flashcard_controller import FlashcardPresenter, FlashcardState
from src.main.python.model.flashcard_session import FlashcardSession, Flashcard


@pytest.fixture
def mock_sessions():
    """Create mock flashcard sessions."""
    letters = Mock(spec=FlashcardSession)
    letters.is_empty.return_value = False
    letters.current.return_value = Flashcard(front="A", back=".-")
    letters.progress_percentage.return_value = 0.0
    letters.is_first.return_value = True
    letters.is_last.return_value = False
    
    numbers = Mock(spec=FlashcardSession)
    numbers.is_empty.return_value = False
    numbers.current.return_value = Flashcard(front="1", back=".----")
    numbers.progress_percentage.return_value = 0.0
    numbers.is_first.return_value = True
    numbers.is_last.return_value = False
    
    return {"letters": letters, "numbers": numbers}


@pytest.fixture
def audio_map():
    """Create sample audio map."""
    return {"A": "/audio/a.wav", "1": "/audio/1.wav"}


@pytest.fixture
def presenter(mock_sessions, audio_map):
    """Create a FlashcardPresenter with mock sessions."""
    return FlashcardPresenter(mock_sessions, audio_map)


class TestFlashcardPresenterInit:
    """Tests for FlashcardPresenter initialization."""

    def test_init_stores_sessions(self, presenter, mock_sessions):
        assert "letters" in presenter._sessions
        assert "numbers" in presenter._sessions

    def test_init_stores_audio_map(self, presenter):
        assert "A" in presenter._audio_map


class TestFlashcardPresenterStart:
    """Tests for start method."""

    def test_start_valid_category_returns_state(self, presenter, mock_sessions):
        state = presenter.start("letters")
        assert isinstance(state, FlashcardState)
        assert state.category == "letters"

    def test_start_resets_session(self, presenter, mock_sessions):
        presenter.start("letters")
        mock_sessions["letters"].reset.assert_called_once()

    def test_start_nonexistent_category_returns_none(self, presenter):
        result = presenter.start("nonexistent")
        assert result is None

    def test_start_empty_session_returns_none(self, presenter, mock_sessions):
        mock_sessions["letters"].is_empty.return_value = True
        result = presenter.start("letters")
        assert result is None

    def test_start_sets_active_category(self, presenter, mock_sessions):
        presenter.start("letters")
        assert presenter._active_category == "letters"

    def test_start_resets_showing_back(self, presenter, mock_sessions):
        presenter._showing_back = True
        presenter.start("letters")
        assert presenter._showing_back is False


class TestFlashcardPresenterToggle:
    """Tests for toggle method."""

    def test_toggle_flips_card(self, presenter, mock_sessions):
        presenter.start("letters")
        assert presenter._showing_back is False
        presenter.toggle()
        assert presenter._showing_back is True

    def test_toggle_returns_state_with_back_shown(self, presenter, mock_sessions):
        presenter.start("letters")
        state = presenter.toggle()
        assert state.is_back_side is True
        assert state.display_text == ".-"

    def test_toggle_without_category_raises(self, presenter):
        with pytest.raises(RuntimeError, match="not initialised"):
            presenter.toggle()


class TestFlashcardPresenterNavigation:
    """Tests for navigation methods."""

    def test_next_advances_session(self, presenter, mock_sessions):
        presenter.start("letters")
        mock_sessions["letters"].is_last.return_value = False
        mock_sessions["letters"].move_next.return_value = True
        mock_sessions["letters"].current.return_value = Flashcard(front="B", back="-...")
        
        state = presenter.next()
        mock_sessions["letters"].move_next.assert_called_once()
        assert state is not None

    def test_next_on_last_returns_none(self, presenter, mock_sessions):
        presenter.start("letters")
        mock_sessions["letters"].is_last.return_value = True
        result = presenter.next()
        assert result is None

    def test_next_resets_showing_back(self, presenter, mock_sessions):
        presenter.start("letters")
        presenter._showing_back = True
        mock_sessions["letters"].is_last.return_value = False
        presenter.next()
        assert presenter._showing_back is False

    def test_previous_moves_back(self, presenter, mock_sessions):
        presenter.start("letters")
        mock_sessions["letters"].move_previous.return_value = True
        state = presenter.previous()
        mock_sessions["letters"].move_previous.assert_called_once()
        assert isinstance(state, FlashcardState)

    def test_previous_resets_showing_back_on_success(self, presenter, mock_sessions):
        presenter.start("letters")
        presenter._showing_back = True
        mock_sessions["letters"].move_previous.return_value = True
        presenter.previous()
        assert presenter._showing_back is False

    def test_previous_keeps_showing_back_on_failure(self, presenter, mock_sessions):
        presenter.start("letters")
        presenter._showing_back = True
        mock_sessions["letters"].move_previous.return_value = False
        presenter.previous()
        # When move_previous returns False, showing_back is NOT reset
        assert presenter._showing_back is True


class TestFlashcardPresenterCurrentState:
    """Tests for current_state method."""

    def test_current_state_returns_state(self, presenter, mock_sessions):
        presenter.start("letters")
        state = presenter.current_state()
        assert isinstance(state, FlashcardState)

    def test_current_state_without_category_raises(self, presenter):
        with pytest.raises(RuntimeError, match="not initialised"):
            presenter.current_state()


class TestFlashcardPresenterReset:
    """Tests for reset method."""

    def test_reset_resets_all_sessions(self, presenter, mock_sessions):
        presenter.reset()
        mock_sessions["letters"].reset.assert_called_once()
        mock_sessions["numbers"].reset.assert_called_once()

    def test_reset_clears_active_category(self, presenter, mock_sessions):
        presenter.start("letters")
        presenter.reset()
        assert presenter._active_category is None

    def test_reset_clears_showing_back(self, presenter, mock_sessions):
        presenter._showing_back = True
        presenter.reset()
        assert presenter._showing_back is False


class TestFlashcardState:
    """Tests for FlashcardState dataclass."""

    def test_state_contains_audio_path(self, presenter, mock_sessions):
        presenter.start("letters")
        state = presenter.current_state()
        assert state.audio_path == "/audio/a.wav"

    def test_show_audio_button_false_when_front(self, presenter, mock_sessions):
        presenter.start("letters")
        state = presenter.current_state()
        assert state.show_audio_button is False

    def test_show_audio_button_true_when_back_with_audio(self, presenter, mock_sessions):
        presenter.start("letters")
        presenter.toggle()
        state = presenter.current_state()
        assert state.show_audio_button is True

    def test_next_label_on_last(self, presenter, mock_sessions):
        presenter.start("letters")
        mock_sessions["letters"].is_last.return_value = True
        state = presenter.current_state()
        assert state.next_label == "Lõpeta treening"

    def test_next_label_not_on_last(self, presenter, mock_sessions):
        presenter.start("letters")
        mock_sessions["letters"].is_last.return_value = False
        state = presenter.current_state()
        assert state.next_label == "Liigu edasi"
