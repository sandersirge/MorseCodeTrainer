"""Tests for exceptions.audio — AudioError hierarchy."""

from __future__ import annotations

import pytest

from src.main.python.exceptions.audio import (
	AudioError,
	AudioSaveError,
	AudioSynthesisError,
	NoAudioContentError,
)
from src.main.python.exceptions.base import ErrorCode, MorseTrainerError


class TestAudioErrorHierarchy:
	def test_audio_error_is_morse_trainer_error(self) -> None:
		err = NoAudioContentError()
		assert isinstance(err, MorseTrainerError)

	def test_no_audio_content_is_audio_error(self) -> None:
		err = NoAudioContentError()
		assert isinstance(err, AudioError)

	def test_audio_synthesis_is_audio_error(self) -> None:
		err = AudioSynthesisError()
		assert isinstance(err, AudioError)

	def test_audio_save_is_audio_error(self) -> None:
		err = AudioSaveError()
		assert isinstance(err, AudioError)


class TestNoAudioContentError:
	def test_code(self) -> None:
		err = NoAudioContentError()
		assert err.code is ErrorCode.NO_AUDIO_CONTENT

	def test_user_message_from_registry(self) -> None:
		err = NoAudioContentError()
		assert len(err.user_message) > 0

	def test_custom_user_message(self) -> None:
		err = NoAudioContentError("Kohandatud")
		assert err.user_message == "Kohandatud"

	def test_no_cause_by_default(self) -> None:
		err = NoAudioContentError()
		assert err.cause is None

	def test_can_be_raised_and_caught_as_audio_error(self) -> None:
		with pytest.raises(AudioError):
			raise NoAudioContentError()


class TestAudioSynthesisError:
	def test_default_message(self) -> None:
		err = AudioSynthesisError()
		assert "synthesis" in str(err).lower() or "failed" in str(err).lower()

	def test_custom_message(self) -> None:
		err = AudioSynthesisError("codec error")
		assert "codec error" in str(err)

	def test_code(self) -> None:
		err = AudioSynthesisError()
		assert err.code is ErrorCode.AUDIO_SYNTHESIS_FAILED

	def test_cause_stored(self) -> None:
		original = OSError("no wav")
		err = AudioSynthesisError(cause=original)
		assert err.cause is original

	def test_custom_user_message(self) -> None:
		err = AudioSynthesisError(user_message="Heli viga")
		assert err.user_message == "Heli viga"


class TestAudioSaveError:
	def test_default_message(self) -> None:
		err = AudioSaveError()
		assert "save" in str(err).lower() or "failed" in str(err).lower()

	def test_custom_message(self) -> None:
		err = AudioSaveError("disk full")
		assert "disk full" in str(err)

	def test_code(self) -> None:
		err = AudioSaveError()
		assert err.code is ErrorCode.AUDIO_SAVE_FAILED

	def test_cause_stored(self) -> None:
		original = PermissionError("denied")
		err = AudioSaveError(cause=original)
		assert err.cause is original

	def test_custom_user_message(self) -> None:
		err = AudioSaveError(user_message="Salvestus ebaõnnestus")
		assert err.user_message == "Salvestus ebaõnnestus"

	@pytest.mark.parametrize("msg", ["disk full", "permission denied", "path not found"])
	def test_various_messages(self, msg: str) -> None:
		err = AudioSaveError(msg)
		assert msg in str(err)
