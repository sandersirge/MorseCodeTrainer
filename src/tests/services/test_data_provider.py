"""Tests for data_provider service."""
import pytest
from types import MappingProxyType
from src.main.python.services.data_provider import (
    create_translation_resources,
    create_test_session,
    create_flashcard_resources,
    load_letter_cards,
    load_number_cards,
    load_symbol_cards,
    load_flashcard_audio_map,
    TranslationResources,
    FlashcardResources,
)
from src.main.python.model.translation_session import TranslationSession
from src.main.python.model.test_session import TestSession
from src.main.python.model.flashcard_session import FlashcardSession


class TestCreateTranslationResources:
    """Tests for create_translation_resources function."""

    def test_returns_translation_resources(self):
        resources = create_translation_resources()
        assert isinstance(resources, TranslationResources)

    def test_morse_to_text_is_translation_session(self):
        resources = create_translation_resources()
        assert isinstance(resources.morse_to_text, TranslationSession)

    def test_text_to_morse_is_translation_session(self):
        resources = create_translation_resources()
        assert isinstance(resources.text_to_morse, TranslationSession)

    def test_sessions_have_content(self):
        resources = create_translation_resources()
        assert resources.morse_to_text.total > 0
        assert resources.text_to_morse.total > 0

    def test_audio_map_is_immutable(self):
        resources = create_translation_resources()
        assert isinstance(resources.audio_map, MappingProxyType)


class TestCreateTestSession:
    """Tests for create_test_session function."""

    def test_returns_test_session(self):
        session = create_test_session()
        assert isinstance(session, TestSession)

    def test_session_has_questions(self):
        session = create_test_session()
        assert session.total_questions > 0

    def test_session_has_20_questions(self):
        session = create_test_session()
        assert session.total_questions == 20


class TestCreateFlashcardResources:
    """Tests for create_flashcard_resources function."""

    def test_returns_flashcard_resources(self):
        resources = create_flashcard_resources()
        assert isinstance(resources, FlashcardResources)

    def test_sessions_immutable_mapping(self):
        resources = create_flashcard_resources()
        assert isinstance(resources.sessions, MappingProxyType)

    def test_has_expected_categories(self):
        resources = create_flashcard_resources()
        assert "tähed" in resources.sessions
        assert "numbrid" in resources.sessions
        assert "märgid" in resources.sessions

    def test_sessions_are_flashcard_sessions(self):
        resources = create_flashcard_resources()
        for session in resources.sessions.values():
            assert isinstance(session, FlashcardSession)

    def test_audio_map_has_content(self):
        resources = create_flashcard_resources()
        assert len(resources.audio_map) > 0


class TestLoadLetterCards:
    """Tests for load_letter_cards function."""

    def test_returns_tuple(self):
        cards = load_letter_cards()
        assert isinstance(cards, tuple)

    def test_cards_are_tuples(self):
        cards = load_letter_cards()
        for card in cards:
            assert isinstance(card, tuple)
            assert len(card) == 2

    def test_has_expected_count(self):
        cards = load_letter_cards()
        # Should have Estonian alphabet letters
        assert len(cards) >= 26


class TestLoadNumberCards:
    """Tests for load_number_cards function."""

    def test_returns_tuple(self):
        cards = load_number_cards()
        assert isinstance(cards, tuple)

    def test_has_10_digits(self):
        cards = load_number_cards()
        assert len(cards) == 10


class TestLoadSymbolCards:
    """Tests for load_symbol_cards function."""

    def test_returns_tuple(self):
        cards = load_symbol_cards()
        assert isinstance(cards, tuple)

    def test_has_symbols(self):
        cards = load_symbol_cards()
        assert len(cards) > 0


class TestLoadFlashcardAudioMap:
    """Tests for load_flashcard_audio_map function."""

    def test_returns_mapping(self):
        audio_map = load_flashcard_audio_map()
        assert hasattr(audio_map, "__getitem__")

    def test_has_content(self):
        audio_map = load_flashcard_audio_map()
        assert len(audio_map) > 0

    def test_values_are_paths(self):
        audio_map = load_flashcard_audio_map()
        for path in audio_map.values():
            assert isinstance(path, str)
            assert path.endswith(".wav")


class TestLruCaching:
    """Tests for lru_cache behavior on static data."""

    def test_repeated_calls_return_same_data(self):
        cards1 = load_letter_cards()
        cards2 = load_letter_cards()
        assert cards1 is cards2  # Same object due to caching

    def test_resources_share_cached_data(self):
        # Multiple resource creations should use the same cached static data
        audio1 = load_flashcard_audio_map()
        audio2 = load_flashcard_audio_map()
        assert audio1 is audio2
