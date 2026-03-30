"""Session-related exceptions."""

from __future__ import annotations

from .base import ErrorCode, MorseTrainerError


class SessionError(MorseTrainerError):
	"""Base class for session-related errors."""


class SessionNotInitializedError(SessionError):
	"""Raised when attempting to use a session that hasn't been started."""

	def __init__(
		self,
		message: str = "Session not initialized",
		*,
		user_message: str | None = None,
	) -> None:
		super().__init__(
			message,
			code=ErrorCode.SESSION_NOT_INITIALIZED,
			user_message=user_message,
		)


class SessionInvalidStateError(SessionError):
	"""Raised when a session is in an invalid state for the requested operation."""

	def __init__(
		self,
		message: str = "Session in invalid state",
		*,
		user_message: str | None = None,
	) -> None:
		super().__init__(
			message,
			code=ErrorCode.SESSION_INVALID_STATE,
			user_message=user_message,
		)


__all__ = [
	"SessionError",
	"SessionNotInitializedError",
	"SessionInvalidStateError",
]
