"""Property-based tests for morse_translator using Hypothesis.

These tests verify behavioural invariants that must hold for
*any* valid input — not just hand-picked examples.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from src.main.python.resources.morse_data import (
	LETTER_MORSE_PAIRS,
	NUMBER_SYMBOL_MORSE_PAIRS,
)
from src.main.python.utils.morse_translator import convert_morse_to_text, convert_text_to_morse

# ---------------------------------------------------------------------------
# Build alphabets from the actual data tables so the tests stay in sync
# with whatever characters are defined in morse_data.py.
# ---------------------------------------------------------------------------
_LETTERS = [letter for letter, _ in LETTER_MORSE_PAIRS]
_DIGITS = [char for char, _ in NUMBER_SYMBOL_MORSE_PAIRS if char.isdigit()]
_SYMBOLS = [char for char, _ in NUMBER_SYMBOL_MORSE_PAIRS if not char.isdigit()]
_ALL_SUPPORTED = _LETTERS + [letter.upper() for letter in _LETTERS] + _DIGITS + _SYMBOLS

# Hypothesis strategy: non-empty strings built from supported characters only
_supported_char = st.sampled_from(_ALL_SUPPORTED)
_supported_word = st.text(alphabet=_ALL_SUPPORTED, min_size=1, max_size=12)
_supported_sentence = st.lists(_supported_word, min_size=1, max_size=6).map(" ".join)


class TestEncodeDecodeRoundTrip:
	"""Invariant: encode(text) → decode → text (case-normalised)."""

	@given(_supported_char)
	@settings(max_examples=len(_ALL_SUPPORTED))
	def test_single_char_round_trip(self, char: str) -> None:
		"""Any supported character survives a encode→decode round-trip."""
		encoded = convert_text_to_morse(char)
		decoded = convert_morse_to_text(encoded)
		assert decoded.lower() == char.lower()

	@given(_supported_word)
	@settings(max_examples=200)
	def test_word_round_trip_case_insensitive(self, word: str) -> None:
		"""Any word composed of supported characters survives encode→decode."""
		encoded = convert_text_to_morse(word)
		decoded = convert_morse_to_text(encoded)
		assert decoded.lower() == word.lower()

	@given(_supported_sentence)
	@settings(max_examples=100)
	def test_sentence_round_trip_word_count(self, sentence: str) -> None:
		"""Word count is preserved through the encode→decode cycle.

		Words are separated by triple spaces in Morse; decoding reconstructs
		the same number of whitespace-delimited tokens.
		"""
		original_words = sentence.split()
		encoded = convert_text_to_morse(sentence)
		decoded = convert_morse_to_text(encoded)
		decoded_words = decoded.split()
		assert len(decoded_words) == len(original_words)


class TestEncodeProperties:
	"""Invariants about the encoded output format."""

	@given(_supported_word)
	@settings(max_examples=200)
	def test_encoded_contains_only_morse_chars(self, word: str) -> None:
		"""Morse output contains only dots, dashes, and spaces."""
		encoded = convert_text_to_morse(word)
		for ch in encoded:
			assert ch in (".", "-", " "), f"Unexpected character {ch!r} in {encoded!r}"

	@given(_supported_word)
	@settings(max_examples=200)
	def test_encoded_does_not_start_or_end_with_space(self, word: str) -> None:
		"""Morse encoding of a single word has no leading/trailing whitespace."""
		encoded = convert_text_to_morse(word)
		assert encoded == encoded.strip()

	@given(st.lists(_supported_word, min_size=2, max_size=5).map(" ".join))
	@settings(max_examples=100)
	def test_multi_word_encoded_uses_triple_space_separator(self, sentence: str) -> None:
		"""Words in the input produce triple-space separation in Morse output."""
		words = sentence.split()
		if len(words) < 2:
			return
		encoded = convert_text_to_morse(sentence)
		assert "   " in encoded


class TestDecodeProperties:
	"""Invariants about the decoded output format."""

	@given(_supported_word)
	@settings(max_examples=200)
	def test_decoded_single_word_is_title_cased_first_char(self, word: str) -> None:
		"""The first decoded character of a word is uppercase (or a digit/symbol)."""
		encoded = convert_text_to_morse(word)
		decoded = convert_morse_to_text(encoded)
		if decoded and decoded[0].isalpha():
			assert decoded[0].isupper()
