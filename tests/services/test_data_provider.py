"""Tests for data_provider service."""

from types import MappingProxyType

from morsetrainer.model.flashcard_session import FlashcardSession
from morsetrainer.model.test_session import TestSession, is_morse
from morsetrainer.model.translation_session import TranslationSession
from morsetrainer.services.data_provider import (
	FlashcardResources,
	TranslationResources,
	create_flashcard_resources,
	create_test_session,
	create_translation_resources,
	load_letter_cards,
	load_number_cards,
	load_symbol_cards,
)
from morsetrainer.utils.morse_translator import (
	convert_morse_to_text,
	convert_text_to_morse,
	normalize_morse,
)


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

	def test_letters_include_z_caron(self):
		assert ("Ž ž", "--..-") in load_letter_cards()


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


class TestExerciseMorseIsGenerated:
	"""Morse in exercises is generated from text, so it always decodes back."""

	def test_translation_pairs_decode_to_their_text(self):
		resources = create_translation_resources()
		session = resources.morse_to_text
		for morse, text in zip(session.prompts, session.answers):
			assert convert_morse_to_text(morse) == " ".join(text.upper().split())

	def test_text_to_morse_answers_match(self):
		session = create_translation_resources().text_to_morse
		for text, morse in zip(session.prompts, session.answers):
			assert normalize_morse(morse) == convert_text_to_morse(text)

	def test_test_session_morse_decodes(self):
		session = create_test_session()
		for prompt, answer in zip(session._prompts, session._answers):
			morse, text = (answer, prompt) if is_morse(answer) else (prompt, answer)
			assert convert_morse_to_text(morse) == " ".join(text.upper().split())

	def test_display_morse_breaks_lines_only_between_words(self):
		# Lines may only be split between words, so every line is whole words
		# and only a single word may exceed the target width.
		for morse in create_translation_resources().morse_to_text.prompts:
			for line in morse.split("\n"):
				assert line == line.strip()
				assert len(line) <= 44 or "   " not in line


class TestLruCaching:
	"""Tests for lru_cache behavior on static data."""

	def test_repeated_calls_return_same_data(self):
		cards1 = load_letter_cards()
		cards2 = load_letter_cards()
		assert cards1 is cards2  # Same object due to caching

	def test_resources_share_cached_data(self):
		# Multiple resource creations should use the same cached static data
		symbols1 = load_symbol_cards()
		symbols2 = load_symbol_cards()
		assert symbols1 is symbols2
