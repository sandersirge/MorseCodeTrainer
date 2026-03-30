"""Tests for exceptions.base — ErrorCode, MorseTrainerError, get_user_message."""

from __future__ import annotations

import pytest

from src.main.python.exceptions.base import (
	ErrorCode,
	ErrorMessage,
	MorseTrainerError,
	get_user_message,
)


class TestErrorCode:
	def test_session_codes_are_1xx(self) -> None:
		assert ErrorCode.SESSION_NOT_INITIALIZED.value == 100
		assert ErrorCode.SESSION_INVALID_STATE.value == 101
		assert ErrorCode.SESSION_INDEX_OUT_OF_BOUNDS.value == 102

	def test_translation_codes_are_2xx(self) -> None:
		assert ErrorCode.UNSUPPORTED_CHARACTER.value == 200
		assert ErrorCode.UNSUPPORTED_MORSE_SYMBOL.value == 201
		assert ErrorCode.EMPTY_INPUT.value == 202
		assert ErrorCode.TRANSLATION_FAILED.value == 203

	def test_audio_codes_are_3xx(self) -> None:
		assert ErrorCode.NO_AUDIO_CONTENT.value == 300
		assert ErrorCode.AUDIO_SYNTHESIS_FAILED.value == 301
		assert ErrorCode.AUDIO_SAVE_FAILED.value == 302
		assert ErrorCode.AUDIO_PLAYBACK_FAILED.value == 303

	def test_validation_codes_are_4xx(self) -> None:
		assert ErrorCode.INVALID_MODE.value == 400
		assert ErrorCode.INVALID_CONFIGURATION.value == 401
		assert ErrorCode.MISMATCHED_DATA.value == 402

	def test_resource_codes_are_5xx(self) -> None:
		assert ErrorCode.RESOURCE_NOT_FOUND.value == 500
		assert ErrorCode.RESOURCE_LOAD_FAILED.value == 501

	def test_all_codes_are_unique(self) -> None:
		values = [code.value for code in ErrorCode]
		assert len(values) == len(set(values))


class TestErrorMessage:
	def test_fields_stored(self) -> None:
		msg = ErrorMessage(technical="tech detail", user_facing="user detail")
		assert msg.technical == "tech detail"
		assert msg.user_facing == "user detail"

	def test_frozen(self) -> None:
		msg = ErrorMessage(technical="t", user_facing="u")
		with pytest.raises(Exception):
			msg.technical = "changed"  # type: ignore[misc]


class TestMorseTrainerError:
	def test_str_format_includes_code_name(self) -> None:
		err = MorseTrainerError("something broke", code=ErrorCode.EMPTY_INPUT)
		assert str(err) == "[EMPTY_INPUT] something broke"

	def test_str_format_includes_code_name_session(self) -> None:
		err = MorseTrainerError("bad state", code=ErrorCode.SESSION_INVALID_STATE)
		assert str(err) == "[SESSION_INVALID_STATE] bad state"

	def test_code_attribute(self) -> None:
		err = MorseTrainerError("msg", code=ErrorCode.INVALID_MODE)
		assert err.code is ErrorCode.INVALID_MODE

	def test_user_message_from_registry_when_none(self) -> None:
		err = MorseTrainerError("msg", code=ErrorCode.EMPTY_INPUT)
		assert err.user_message  # must be non-empty Estonian string
		assert len(err.user_message) > 0

	def test_explicit_user_message_overrides_registry(self) -> None:
		err = MorseTrainerError("msg", code=ErrorCode.EMPTY_INPUT, user_message="Oma sõnum")
		assert err.user_message == "Oma sõnum"

	def test_cause_attribute_defaults_to_none(self) -> None:
		err = MorseTrainerError("msg", code=ErrorCode.AUDIO_SAVE_FAILED)
		assert err.cause is None

	def test_cause_attribute_stored(self) -> None:
		original = ValueError("original")
		err = MorseTrainerError("wrapped", code=ErrorCode.AUDIO_SAVE_FAILED, cause=original)
		assert err.cause is original

	def test_is_exception(self) -> None:
		err = MorseTrainerError("msg", code=ErrorCode.RESOURCE_NOT_FOUND)
		assert isinstance(err, Exception)

	def test_can_be_raised_and_caught(self) -> None:
		with pytest.raises(MorseTrainerError) as exc_info:
			raise MorseTrainerError("test raise", code=ErrorCode.RESOURCE_LOAD_FAILED)
		assert exc_info.value.code is ErrorCode.RESOURCE_LOAD_FAILED


class TestGetUserMessage:
	def test_returns_user_message_for_morse_error(self) -> None:
		err = MorseTrainerError("msg", code=ErrorCode.EMPTY_INPUT, user_message="Kohandatud")
		assert get_user_message(err) == "Kohandatud"

	def test_returns_registry_message_for_morse_error_without_custom(self) -> None:
		err = MorseTrainerError("msg", code=ErrorCode.EMPTY_INPUT)
		result = get_user_message(err)
		assert len(result) > 0
		assert "Tekkis viga:" not in result  # should NOT fall through to generic

	def test_generic_message_for_plain_exception(self) -> None:
		err = ValueError("plain error")
		assert get_user_message(err) == "Tekkis viga: plain error"

	def test_generic_message_for_runtime_error(self) -> None:
		err = RuntimeError("boom")
		assert get_user_message(err) == "Tekkis viga: boom"
