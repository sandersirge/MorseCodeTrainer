"""Base exception class, error codes, and user-message helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..strings import t


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
	ErrorCode.SESSION_NOT_INITIALIZED: t("error.seanss_pole_kaivitatud_palun"),
	ErrorCode.SESSION_INVALID_STATE: t("error.seanss_on_vigases_olekus"),
	ErrorCode.SESSION_INDEX_OUT_OF_BOUNDS: t("error.oled_joudnud_harjutuse_loppu"),
	# Translation errors
	ErrorCode.UNSUPPORTED_CHARACTER: t("error.sisend_sisaldab_tahemarki_mida"),
	ErrorCode.UNSUPPORTED_MORSE_SYMBOL: t("error.sisend_sisaldab_morsekoodi_mida"),
	ErrorCode.EMPTY_INPUT: t("error.palun_sisesta_tekst_enne"),
	ErrorCode.TRANSLATION_FAILED: t("error.tolkimine_ebaonnestus_kontrolli_sisendit"),
	# Audio errors
	ErrorCode.NO_AUDIO_CONTENT: t("error.heli_esitamiseks_puudub_morsekoodi"),
	ErrorCode.AUDIO_SYNTHESIS_FAILED: t("error.helifaili_loomine_ebaonnestus"),
	ErrorCode.AUDIO_SAVE_FAILED: t("error.helifaili_salvestamine_ebaonnestus"),
	ErrorCode.AUDIO_PLAYBACK_FAILED: t("error.heli_esitamine_ebaonnestus"),
	# Validation errors
	ErrorCode.INVALID_MODE: t("error.valitud_reziim_pole_toetatud"),
	ErrorCode.INVALID_CONFIGURATION: t("error.seadistus_on_vigane"),
	ErrorCode.MISMATCHED_DATA: t("error.andmed_ei_uhti_kontrolli"),
	# Resource errors
	ErrorCode.RESOURCE_NOT_FOUND: t("error.vajalikku_ressurssi_ei_leitud"),
	ErrorCode.RESOURCE_LOAD_FAILED: t("error.ressursi_laadimine_ebaonnestus"),
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
	return t("error.generic", details=error)


__all__ = [
	"ErrorCode",
	"ErrorMessage",
	"MorseTrainerError",
	"get_user_message",
]
