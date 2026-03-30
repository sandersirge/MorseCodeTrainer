"""Tests for exceptions.validation — ValidationError hierarchy."""

from __future__ import annotations

import pytest

from src.main.python.exceptions.base import ErrorCode, MorseTrainerError
from src.main.python.exceptions.validation import (
	InvalidModeError,
	MismatchedDataError,
	ValidationError,
)


class TestValidationErrorHierarchy:
	def test_validation_error_is_morse_trainer_error(self) -> None:
		err = MismatchedDataError()
		assert isinstance(err, MorseTrainerError)

	def test_invalid_mode_is_validation_error(self) -> None:
		err = InvalidModeError("fast")
		assert isinstance(err, ValidationError)

	def test_mismatched_data_is_validation_error(self) -> None:
		err = MismatchedDataError()
		assert isinstance(err, ValidationError)


class TestInvalidModeError:
	def test_stores_mode(self) -> None:
		err = InvalidModeError("turbo")
		assert err.mode == "turbo"

	def test_message_contains_mode(self) -> None:
		err = InvalidModeError("turbo")
		assert "turbo" in str(err)

	def test_code(self) -> None:
		err = InvalidModeError("fast")
		assert err.code is ErrorCode.INVALID_MODE

	def test_user_message_from_registry(self) -> None:
		err = InvalidModeError("slow")
		assert len(err.user_message) > 0

	def test_custom_user_message(self) -> None:
		err = InvalidModeError("slow", user_message="Vale režiim")
		assert err.user_message == "Vale režiim"

	def test_can_be_caught_as_morse_trainer_error(self) -> None:
		with pytest.raises(MorseTrainerError):
			raise InvalidModeError("invalid")

	@pytest.mark.parametrize("mode", ["fast", "slow", "turbo", "text", "morse", ""])
	def test_various_modes(self, mode: str) -> None:
		err = InvalidModeError(mode)
		assert err.mode == mode


class TestMismatchedDataError:
	def test_default_message_mentions_mismatch(self) -> None:
		err = MismatchedDataError()
		lower = str(err).lower()
		assert "mismatch" in lower or "data" in lower

	def test_custom_message(self) -> None:
		err = MismatchedDataError("prompts and answers differ")
		assert "prompts and answers differ" in str(err)

	def test_code(self) -> None:
		err = MismatchedDataError()
		assert err.code is ErrorCode.MISMATCHED_DATA

	def test_user_message_from_registry(self) -> None:
		err = MismatchedDataError()
		assert len(err.user_message) > 0

	def test_custom_user_message(self) -> None:
		err = MismatchedDataError(user_message="Andmed ei klapi")
		assert err.user_message == "Andmed ei klapi"

	def test_can_be_raised_and_caught_as_validation_error(self) -> None:
		with pytest.raises(ValidationError):
			raise MismatchedDataError()
