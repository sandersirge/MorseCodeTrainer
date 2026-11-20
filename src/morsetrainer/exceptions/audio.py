"""Audio-related exceptions."""

from __future__ import annotations

from .base import ErrorCode, MorseTrainerError


class AudioError(MorseTrainerError):
	"""Base class for audio-related errors."""


class NoAudioContentError(AudioError):
	"""Raised when audio operations are attempted without Morse content."""

	def __init__(
		self,
		user_message: str | None = None,
	) -> None:
		super().__init__(
			"No Morse content available for audio synthesis",
			code=ErrorCode.NO_AUDIO_CONTENT,
			user_message=user_message,
		)


class AudioSynthesisError(AudioError):
	"""Raised when audio synthesis fails."""

	def __init__(
		self,
		message: str = "Audio synthesis failed",
		*,
		user_message: str | None = None,
		cause: Exception | None = None,
	) -> None:
		super().__init__(
			message,
			code=ErrorCode.AUDIO_SYNTHESIS_FAILED,
			user_message=user_message,
			cause=cause,
		)


class AudioSaveError(AudioError):
	"""Raised when saving an audio file fails."""

	def __init__(
		self,
		message: str = "Failed to save audio file",
		*,
		user_message: str | None = None,
		cause: Exception | None = None,
	) -> None:
		super().__init__(
			message,
			code=ErrorCode.AUDIO_SAVE_FAILED,
			user_message=user_message,
			cause=cause,
		)


__all__ = [
	"AudioError",
	"NoAudioContentError",
	"AudioSynthesisError",
	"AudioSaveError",
]
