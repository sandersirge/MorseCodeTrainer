"""Typed exceptions for the Morse Code Trainer application.

This package provides a structured exception hierarchy with Estonian user-facing
messages and error codes for programmatic handling.

Sub-modules:
    base        — ErrorCode, ErrorMessage, MorseTrainerError, get_user_message
    session     — SessionError, SessionNotInitializedError, SessionInvalidStateError
    translation — TranslationError, UnsupportedCharacterError, UnsupportedMorseSymbolError, EmptyInputError
    audio       — AudioError, NoAudioContentError, AudioSynthesisError, AudioSaveError
    validation  — ValidationError, InvalidModeError, MismatchedDataError

All names are re-exported from this package so existing
``from ..exceptions import X`` imports continue to work unchanged.
"""

from __future__ import annotations

from .audio import AudioError, AudioSaveError, AudioSynthesisError, NoAudioContentError
from .base import ErrorCode, ErrorMessage, MorseTrainerError, get_user_message
from .session import SessionError, SessionInvalidStateError, SessionNotInitializedError
from .translation import (
	EmptyInputError,
	TranslationError,
	UnsupportedCharacterError,
	UnsupportedMorseSymbolError,
)
from .validation import InvalidModeError, MismatchedDataError, ValidationError

__all__ = [
	# Enums and dataclasses
	"ErrorCode",
	"ErrorMessage",
	# Base exception
	"MorseTrainerError",
	# Session exceptions
	"SessionError",
	"SessionNotInitializedError",
	"SessionInvalidStateError",
	# Translation exceptions
	"TranslationError",
	"UnsupportedCharacterError",
	"UnsupportedMorseSymbolError",
	"EmptyInputError",
	# Audio exceptions
	"AudioError",
	"NoAudioContentError",
	"AudioSynthesisError",
	"AudioSaveError",
	# Validation exceptions
	"ValidationError",
	"InvalidModeError",
	"MismatchedDataError",
	# Helpers
	"get_user_message",
]
