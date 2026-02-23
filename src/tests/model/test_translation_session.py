"""Tests for TranslationSession model."""
import pytest
from src.main.python.model.translation_session import TranslationSession


class TestTranslationSessionInit:
    """Tests for TranslationSession initialization."""

    def test_init_with_matching_lengths(self):
        session = TranslationSession(
            prompts=["HELLO", "WORLD"],
            answers=[".... . .-.. .-.. ---", ".-- --- .-. .-.. -.."]
        )
        assert session.total == 2

    def test_init_mismatched_lengths_raises(self):
        with pytest.raises(ValueError, match="equal numbers"):
            TranslationSession(prompts=["HELLO"], answers=["a", "b"])

    def test_init_empty_lists(self):
        session = TranslationSession(prompts=[], answers=[])
        assert session.total == 0

    def test_init_invalid_index_raises(self):
        with pytest.raises(ValueError, match="index must point"):
            TranslationSession(prompts=["A"], answers=[".-"], index=5)

    def test_init_negative_index_raises(self):
        with pytest.raises(ValueError, match="index must point"):
            TranslationSession(prompts=["A"], answers=[".-"], index=-1)


class TestTranslationSessionEmpty:
    """Tests for empty TranslationSession behavior."""

    def test_total_is_zero(self):
        session = TranslationSession(prompts=[], answers=[])
        assert session.total == 0

    def test_current_prompt_raises(self):
        session = TranslationSession(prompts=[], answers=[])
        with pytest.raises(IndexError, match="No prompts"):
            session.current_prompt()

    def test_current_answer_raises(self):
        session = TranslationSession(prompts=[], answers=[])
        with pytest.raises(IndexError, match="No answers"):
            session.current_answer()

    def test_is_last_true(self):
        session = TranslationSession(prompts=[], answers=[])
        assert session.is_last()

    def test_is_first_true(self):
        session = TranslationSession(prompts=[], answers=[])
        assert session.is_first()


class TestTranslationSessionNavigation:
    """Tests for TranslationSession navigation."""

    def test_current_prompt(self, translation_session):
        assert translation_session.current_prompt() == "HELLO"

    def test_current_answer(self, translation_session):
        assert translation_session.current_answer() == ".... . .-.. .-.. ---"

    def test_move_next_success(self, translation_session):
        assert translation_session.move_next() is True
        assert translation_session.current_prompt() == "WORLD"

    def test_move_next_on_last_fails(self, translation_session):
        translation_session.move_next()  # WORLD
        translation_session.move_next()  # TEST
        assert translation_session.move_next() is False

    def test_move_previous_success(self, translation_session):
        translation_session.move_next()
        assert translation_session.move_previous() is True
        assert translation_session.current_prompt() == "HELLO"

    def test_move_previous_on_first_fails(self, translation_session):
        assert translation_session.move_previous() is False

    def test_is_first_true_at_start(self, translation_session):
        assert translation_session.is_first()

    def test_is_first_false_after_move(self, translation_session):
        translation_session.move_next()
        assert not translation_session.is_first()

    def test_is_last_false_at_start(self, translation_session):
        assert not translation_session.is_last()

    def test_is_last_true_at_end(self, translation_session):
        translation_session.move_next()
        translation_session.move_next()
        assert translation_session.is_last()

    def test_reset_returns_to_start(self, translation_session):
        translation_session.move_next()
        translation_session.move_next()
        translation_session.reset()
        assert translation_session.is_first()
        assert translation_session.current_prompt() == "HELLO"


class TestTranslationSessionSingleItem:
    """Tests for single-item session edge cases."""

    def test_single_item_is_both_first_and_last(self):
        session = TranslationSession(prompts=["A"], answers=[".-"])
        assert session.is_first()
        assert session.is_last()

    def test_single_item_cannot_navigate(self):
        session = TranslationSession(prompts=["A"], answers=[".-"])
        assert session.move_next() is False
        assert session.move_previous() is False
