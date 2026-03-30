"""Base exception class, error codes, and user-message helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ErrorCode(Enum):
	"""Programmatic error codes for handling specific error types."""

	# Session errors (1xx)
	SESSION_NOT_INITIALIZED = 100
	SESSION_INVALID_STATE = 101
	SESSION_INDEX_OUT_OF_BOUNDS = 102

	# Translation errors (2xx)
	UNSUPPORTED_CHARACTER = 200
	UNSUPPORTED_MORSE_SYMBOL = 201
	EMPTY_INPUT = 202
	TRANSLATION_FAILED = 203

	# Audio errors (3xx)
	NO_AUDIO_CONTENT = 300
	AUDIO_SYNTHESIS_FAILED = 301
	AUDIO_SAVE_FAILED = 302
	AUDIO_PLAYBACK_FAILED = 303

	# Validation errors (4xx)
	INVALID_MODE = 400
	INVALID_CONFIGURATION = 401
	MISMATCHED_DATA = 402

	# Resource errors (5xx)
	RESOURCE_NOT_FOUND = 500
	RESOURCE_LOAD_FAILED = 501


@dataclass(frozen=True)
class ErrorMessage:
	"""Holds both technical and user-facing error messages."""

	technical: str
	user_facing: str


# Estonian user-facing messages for common errors
_ERROR_MESSAGES: dict[ErrorCode, str] = {
	# Session errors
	ErrorCode.SESSION_NOT_INITIALIZED: "Seanss pole käivitatud. Palun alusta uuesti.",
	ErrorCode.SESSION_INVALID_STATE: "Seanss on vigases olekus. Palun alusta uuesti.",
	ErrorCode.SESSION_INDEX_OUT_OF_BOUNDS: "Oled jõudnud harjutuse lõppu.",
	# Translation errors
	ErrorCode.UNSUPPORTED_CHARACTER: "Sisend sisaldab tähemärki, mida ei saa morsekoodiks teisendada.",
	ErrorCode.UNSUPPORTED_MORSE_SYMBOL: "Sisend sisaldab morsekoodi, mida ei tunta.",
	ErrorCode.EMPTY_INPUT: "Palun sisesta tekst enne tõlkimist.",
	ErrorCode.TRANSLATION_FAILED: "Tõlkimine ebaõnnestus. Kontrolli sisendit.",
	# Audio errors
	ErrorCode.NO_AUDIO_CONTENT: "Heli esitamiseks puudub morsekoodi sisu.",
	ErrorCode.AUDIO_SYNTHESIS_FAILED: "Helifaili loomine ebaõnnestus.",
	ErrorCode.AUDIO_SAVE_FAILED: "Helifaili salvestamine ebaõnnestus.",
	ErrorCode.AUDIO_PLAYBACK_FAILED: "Heli esitamine ebaõnnestus.",
	# Validation errors
	ErrorCode.INVALID_MODE: "Valitud režiim pole toetatud.",
	ErrorCode.INVALID_CONFIGURATION: "Seadistus on vigane.",
	ErrorCode.MISMATCHED_DATA: "Andmed ei ühti. Kontrolli sisendit.",
	# Resource errors
	ErrorCode.RESOURCE_NOT_FOUND: "Vajalikku ressurssi ei leitud.",
	ErrorCode.RESOURCE_LOAD_FAILED: "Ressursi laadimine ebaõnnestus.",
}


class MorseTrainerError(Exception):
	"""Base exception for all Morse Trainer application errors.

	Provides structured error handling with error codes and user-facing messages.
	"""

	def __init__(
		self,
		message: str,
		*,
		code: ErrorCode,
		user_message: str | None = None,
		cause: Exception | None = None,
	) -> None:
		super().__init__(message)
		self.code = code
		self._user_message = user_message
		self.cause = cause

	@property
	def user_message(self) -> str:
		"""Return the user-facing message in Estonian."""
		if self._user_message:
			return self._user_message
		return _ERROR_MESSAGES.get(self.code, str(self))

	def __str__(self) -> str:
		return f"[{self.code.name}] {super().__str__()}"


def get_user_message(error: Exception) -> str:
	"""Extract a user-facing message from any exception.

	For MorseTrainerError instances, returns the structured user_message.
	For other exceptions, returns a generic Estonian error message.
	"""
	if isinstance(error, MorseTrainerError):
		return error.user_message
	return f"Tekkis viga: {error}"


__all__ = [
	"ErrorCode",
	"ErrorMessage",
	"MorseTrainerError",
	"get_user_message",
]
