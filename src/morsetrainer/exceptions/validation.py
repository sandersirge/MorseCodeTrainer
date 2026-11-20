"""Validation-related exceptions."""

from __future__ import annotations

from .base import ErrorCode, MorseTrainerError


class ValidationError(MorseTrainerError):
	"""Base class for validation-related errors."""


class InvalidModeError(ValidationError):
	"""Raised when an unsupported mode is specified."""

	def __init__(
		self,
		mode: str,
		*,
		user_message: str | None = None,
	) -> None:
		self.mode = mode
		super().__init__(
			f"Unsupported mode: {mode}",
			code=ErrorCode.INVALID_MODE,
			user_message=user_message,
		)


class MismatchedDataError(ValidationError):
	"""Raised when data collections have mismatched sizes."""

	def __init__(
		self,
		message: str = "Data collections have mismatched sizes",
		*,
		user_message: str | None = None,
	) -> None:
		super().__init__(
			message,
			code=ErrorCode.MISMATCHED_DATA,
			user_message=user_message,
		)


__all__ = [
	"ValidationError",
	"InvalidModeError",
	"MismatchedDataError",
]
