"""Tests for FlashcardSession model."""
import pytest
from src.main.python.model.flashcard_session import Flashcard, FlashcardSession


class TestFlashcard:
    """Tests for the Flashcard dataclass."""

    def test_flashcard_creation(self):
        card = Flashcard(front="A", back=".-")
        assert card.front == "A"
        assert card.back == ".-"

    def test_flashcard_is_frozen(self):
        card = Flashcard(front="A", back=".-")
        with pytest.raises(AttributeError):
            card.front = "B"


class TestFlashcardSessionInit:
    """Tests for FlashcardSession initialization."""

    def test_init_with_flashcard_objects(self):
        cards = [Flashcard(front="A", back=".-"), Flashcard(front="B", back="-...")]
        session = FlashcardSession(cards)
        assert session.total == 2

    def test_init_with_tuples(self):
        cards = [("A", ".-"), ("B", "-...")]
        session = FlashcardSession(cards)
        assert session.total == 2
        assert session.current().front == "A"

    def test_init_empty(self):
        session = FlashcardSession()
        assert session.is_empty()
        assert session.total == 0


class TestFlashcardSessionEmpty:
    """Tests for empty FlashcardSession behavior."""

    def test_is_empty_true(self, empty_flashcard_session):
        assert empty_flashcard_session.is_empty()

    def test_current_raises_on_empty(self, empty_flashcard_session):
        with pytest.raises(IndexError, match="no cards"):
            empty_flashcard_session.current()

    def test_is_first_on_empty(self, empty_flashcard_session):
        assert empty_flashcard_session.is_first()

    def test_is_last_on_empty(self, empty_flashcard_session):
        assert empty_flashcard_session.is_last()

    def test_progress_percentage_empty(self, empty_flashcard_session):
        assert empty_flashcard_session.progress_percentage() == 0.0


class TestFlashcardSessionNavigation:
    """Tests for FlashcardSession navigation methods."""

    def test_current_returns_first_card(self, flashcard_session):
        assert flashcard_session.current().front == "A"

    def test_move_next_success(self, flashcard_session):
        assert flashcard_session.move_next() is True
        assert flashcard_session.current().front == "B"

    def test_move_next_on_last_fails(self, flashcard_session):
        flashcard_session.move_next()  # B
        flashcard_session.move_next()  # C
        assert flashcard_session.move_next() is False

    def test_move_previous_success(self, flashcard_session):
        flashcard_session.move_next()
        assert flashcard_session.move_previous() is True
        assert flashcard_session.current().front == "A"

    def test_move_previous_on_first_fails(self, flashcard_session):
        assert flashcard_session.move_previous() is False

    def test_is_first_true_at_start(self, flashcard_session):
        assert flashcard_session.is_first()

    def test_is_first_false_after_move(self, flashcard_session):
        flashcard_session.move_next()
        assert not flashcard_session.is_first()

    def test_is_last_false_at_start(self, flashcard_session):
        assert not flashcard_session.is_last()

    def test_is_last_true_at_end(self, flashcard_session):
        flashcard_session.move_next()
        flashcard_session.move_next()
        assert flashcard_session.is_last()

    def test_reset_returns_to_start(self, flashcard_session):
        flashcard_session.move_next()
        flashcard_session.move_next()
        flashcard_session.reset()
        assert flashcard_session.is_first()
        assert flashcard_session.current().front == "A"


class TestFlashcardSessionProgress:
    """Tests for progress percentage calculation."""

    def test_progress_at_start(self, flashcard_session):
        assert flashcard_session.progress_percentage() == 0.0

    def test_progress_at_middle(self, flashcard_session):
        flashcard_session.move_next()  # index 1 of 3 cards
        assert flashcard_session.progress_percentage() == 50.0

    def test_progress_at_end(self, flashcard_session):
        flashcard_session.move_next()
        flashcard_session.move_next()  # index 2 of 3 cards
        assert flashcard_session.progress_percentage() == 100.0

    def test_progress_single_card(self):
        session = FlashcardSession([Flashcard(front="A", back=".-")])
        assert session.progress_percentage() == 0.0


class TestFlashcardSessionAddCards:
    """Tests for adding cards to a session."""

    def test_add_cards_as_tuples(self, empty_flashcard_session):
        empty_flashcard_session.add_cards([("X", "-..-"), ("Y", "-.--")])
        assert empty_flashcard_session.total == 2

    def test_add_cards_as_flashcards(self, empty_flashcard_session):
        empty_flashcard_session.add_cards([Flashcard("X", "-..-")])
        assert empty_flashcard_session.total == 1

    def test_add_cards_to_existing(self, flashcard_session):
        flashcard_session.add_cards([("D", "-..")])
        assert flashcard_session.total == 4
