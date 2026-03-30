"""Tests for exceptions.session — SessionError hierarchy."""

from __future__ import annotations

import pytest

from src.main.python.exceptions.base import ErrorCode, MorseTrainerError
from src.main.python.exceptions.session import (
	SessionError,
	SessionInvalidStateError,
	SessionNotInitializedError,
)


class TestSessionErrorHierarchy:
	def test_session_error_is_morse_trainer_error(self) -> None:
		err = SessionNotInitializedError()
		assert isinstance(err, MorseTrainerError)

	def test_session_not_initialized_is_session_error(self) -> None:
		err = SessionNotInitializedError()
		assert isinstance(err, SessionError)

	def test_session_invalid_state_is_session_error(self) -> None:
		err = SessionInvalidStateError()
		assert isinstance(err, SessionError)


class TestSessionNotInitializedError:
	def test_default_message(self) -> None:
		err = SessionNotInitializedError()
		assert "not initialized" in str(err).lower()

	def test_default_code(self) -> None:
		err = SessionNotInitializedError()
		assert err.code is ErrorCode.SESSION_NOT_INITIALIZED

	def test_custom_message(self) -> None:
		err = SessionNotInitializedError("custom msg")
		assert "custom msg" in str(err)

	def test_custom_user_message(self) -> None:
		err = SessionNotInitializedError(user_message="Kohandatud")
		assert err.user_message == "Kohandatud"

	def test_user_message_fallback_to_registry(self) -> None:
		err = SessionNotInitializedError()
		assert len(err.user_message) > 0

	def test_can_be_raised_and_caught_as_session_error(self) -> None:
		with pytest.raises(SessionError):
			raise SessionNotInitializedError()


class TestSessionInvalidStateError:
	def test_default_message(self) -> None:
		err = SessionInvalidStateError()
		assert "invalid state" in str(err).lower()

	def test_default_code(self) -> None:
		err = SessionInvalidStateError()
		assert err.code is ErrorCode.SESSION_INVALID_STATE

	def test_custom_message(self) -> None:
		err = SessionInvalidStateError("session has ended")
		assert "session has ended" in str(err)

	def test_custom_user_message(self) -> None:
		err = SessionInvalidStateError(user_message="Vale olek")
		assert err.user_message == "Vale olek"

	def test_can_be_caught_as_morse_trainer_error(self) -> None:
		with pytest.raises(MorseTrainerError):
			raise SessionInvalidStateError()
