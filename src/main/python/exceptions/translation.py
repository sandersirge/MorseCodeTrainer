"""Translation-related exceptions."""

from __future__ import annotations

from .base import ErrorCode, MorseTrainerError


class TranslationError(MorseTrainerError):
	"""Base class for translation-related errors."""


class UnsupportedCharacterError(TranslationError):
	"""Raised when input contains a character that cannot be converted to Morse."""

	def __init__(
		self,
		character: str,
		*,
		user_message: str | None = None,
	) -> None:
		self.character = character
		super().__init__(
			f"Unsupported character '{character}' in input",
			code=ErrorCode.UNSUPPORTED_CHARACTER,
			user_message=user_message or f"Tähemärk '{character}' pole toetatud.",
		)


class UnsupportedMorseSymbolError(TranslationError):
	"""Raised when input contains a Morse symbol that cannot be decoded."""

	def __init__(
		self,
		symbol: str,
		*,
		user_message: str | None = None,
	) -> None:
		self.symbol = symbol
		super().__init__(
			f"Unsupported Morse symbol '{symbol}' in input",
			code=ErrorCode.UNSUPPORTED_MORSE_SYMBOL,
			user_message=user_message or f"Morsekood '{symbol}' pole tuntud.",
		)


class EmptyInputError(TranslationError):
	"""Raised when translation is attempted with empty input."""

	def __init__(
		self,
		user_message: str | None = None,
	) -> None:
		super().__init__(
			"Empty input provided for translation",
			code=ErrorCode.EMPTY_INPUT,
			user_message=user_message,
		)


__all__ = [
	"TranslationError",
	"UnsupportedCharacterError",
	"UnsupportedMorseSymbolError",
	"EmptyInputError",
]
