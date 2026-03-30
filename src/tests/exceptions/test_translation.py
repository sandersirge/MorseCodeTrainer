"""Tests for exceptions.translation — TranslationError hierarchy."""

from __future__ import annotations

import pytest

from src.main.python.exceptions.base import ErrorCode, MorseTrainerError
from src.main.python.exceptions.translation import (
	EmptyInputError,
	TranslationError,
	UnsupportedCharacterError,
	UnsupportedMorseSymbolError,
)


class TestTranslationErrorHierarchy:
	def test_translation_error_is_morse_trainer_error(self) -> None:
		err = EmptyInputError()
		assert isinstance(err, MorseTrainerError)

	def test_unsupported_character_is_translation_error(self) -> None:
		err = UnsupportedCharacterError("ñ")
		assert isinstance(err, TranslationError)

	def test_unsupported_morse_symbol_is_translation_error(self) -> None:
		err = UnsupportedMorseSymbolError("...---")
		assert isinstance(err, TranslationError)

	def test_empty_input_is_translation_error(self) -> None:
		err = EmptyInputError()
		assert isinstance(err, TranslationError)


class TestUnsupportedCharacterError:
	def test_stores_character(self) -> None:
		err = UnsupportedCharacterError("ñ")
		assert err.character == "ñ"

	def test_message_contains_character(self) -> None:
		err = UnsupportedCharacterError("ñ")
		assert "ñ" in str(err)

	def test_code(self) -> None:
		err = UnsupportedCharacterError("x")
		assert err.code is ErrorCode.UNSUPPORTED_CHARACTER

	def test_auto_user_message_contains_character(self) -> None:
		err = UnsupportedCharacterError("€")
		assert "€" in err.user_message

	def test_custom_user_message(self) -> None:
		err = UnsupportedCharacterError("€", user_message="Kohandatud")
		assert err.user_message == "Kohandatud"

	@pytest.mark.parametrize("char", ["ñ", "€", "😀", "\t", "Ω"])
	def test_various_unsupported_chars(self, char: str) -> None:
		err = UnsupportedCharacterError(char)
		assert err.character == char
		assert char in str(err)


class TestUnsupportedMorseSymbolError:
	def test_stores_symbol(self) -> None:
		err = UnsupportedMorseSymbolError("...---")
		assert err.symbol == "...---"

	def test_message_contains_symbol(self) -> None:
		err = UnsupportedMorseSymbolError("...---")
		assert "...---" in str(err)

	def test_code(self) -> None:
		err = UnsupportedMorseSymbolError("??")
		assert err.code is ErrorCode.UNSUPPORTED_MORSE_SYMBOL

	def test_auto_user_message_contains_symbol(self) -> None:
		err = UnsupportedMorseSymbolError("...---")
		assert "...---" in err.user_message

	def test_custom_user_message(self) -> None:
		err = UnsupportedMorseSymbolError("??", user_message="Tundmatu")
		assert err.user_message == "Tundmatu"


class TestEmptyInputError:
	def test_code(self) -> None:
		err = EmptyInputError()
		assert err.code is ErrorCode.EMPTY_INPUT

	def test_message_mentions_empty(self) -> None:
		err = EmptyInputError()
		assert "empty" in str(err).lower()

	def test_user_message_from_registry(self) -> None:
		err = EmptyInputError()
		assert len(err.user_message) > 0

	def test_custom_user_message(self) -> None:
		err = EmptyInputError("Tühi sisend")
		assert err.user_message == "Tühi sisend"

	def test_can_be_raised_and_caught(self) -> None:
		with pytest.raises(TranslationError):
			raise EmptyInputError()
