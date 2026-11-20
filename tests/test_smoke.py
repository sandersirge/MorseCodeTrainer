"""Smoke tests — fast sanity checks that the application bootstraps correctly.

Run in isolation with:  pytest -m smoke -q
Skip during full suite:  pytest -m "not smoke" -q
"""

from __future__ import annotations

import pytest


@pytest.mark.smoke
class TestResourceImports:
	"""All resource sub-modules must be importable and non-empty."""

	def test_morse_data_importable(self) -> None:
		from morsetrainer.resources import morse_data  # noqa: F401

	def test_exercise_data_importable(self) -> None:
		from morsetrainer.resources import exercise_data  # noqa: F401

	def test_constants_shim_importable(self) -> None:
		from morsetrainer.resources import constants  # noqa: F401

	def test_letter_morse_pairs_non_empty(self) -> None:
		from morsetrainer.resources.morse_data import LETTER_MORSE_PAIRS

		assert len(LETTER_MORSE_PAIRS) > 0

	def test_letter_to_morse_map_covers_upper_and_lower(self) -> None:
		from morsetrainer.resources.morse_data import (
			LETTER_MORSE_PAIRS,
			LETTER_TO_MORSE_MAP,
		)

		for letter, _ in LETTER_MORSE_PAIRS:
			assert letter in LETTER_TO_MORSE_MAP
			assert letter.upper() in LETTER_TO_MORSE_MAP

	def test_exercise_data_non_empty(self) -> None:
		from morsetrainer.resources.exercise_data import TEST_ITEMS, TRANSLATION_SENTENCES

		assert len(TRANSLATION_SENTENCES) > 0
		assert len(TEST_ITEMS) > 0


@pytest.mark.smoke
class TestExceptionsBootstrap:
	"""Exceptions package must be importable and fully functional."""

	def test_exceptions_package_importable(self) -> None:
		import morsetrainer.exceptions as exc  # noqa: F401

		assert hasattr(exc, "MorseTrainerError")
		assert hasattr(exc, "ErrorCode")

	def test_all_exception_classes_importable(self) -> None:
		from morsetrainer.exceptions import (  # noqa: F401
			AudioError,
			AudioSaveError,
			AudioSynthesisError,
			EmptyInputError,
			ErrorCode,
			InvalidModeError,
			MismatchedDataError,
			MorseTrainerError,
			NoAudioContentError,
			SessionError,
			SessionInvalidStateError,
			SessionNotInitializedError,
			TranslationError,
			UnsupportedCharacterError,
			UnsupportedMorseSymbolError,
			ValidationError,
		)

	def test_error_code_has_5xx_resource_codes(self) -> None:
		from morsetrainer.exceptions import ErrorCode

		assert ErrorCode.RESOURCE_NOT_FOUND.value == 500
		assert ErrorCode.RESOURCE_LOAD_FAILED.value == 501

	def test_morse_trainer_error_is_catchable_as_exception(self) -> None:
		from morsetrainer.exceptions import ErrorCode, MorseTrainerError

		with pytest.raises(Exception):
			raise MorseTrainerError("smoke test", code=ErrorCode.EMPTY_INPUT)


@pytest.mark.smoke
class TestTranslatorBootstrap:
	"""Core translator functions must be callable."""

	def test_translate_text_to_morse(self) -> None:
		from morsetrainer.utils.morse_translator import convert_text_to_morse

		assert convert_text_to_morse("SOS") == "... --- ..."

	def test_translate_morse_to_text(self) -> None:
		from morsetrainer.utils.morse_translator import convert_morse_to_text

		assert convert_morse_to_text("... --- ...").lower() == "sos"

	def test_empty_text_returns_empty(self) -> None:
		from morsetrainer.utils.morse_translator import convert_text_to_morse

		assert convert_text_to_morse("") == ""

	def test_empty_morse_returns_empty(self) -> None:
		from morsetrainer.utils.morse_translator import convert_morse_to_text

		assert convert_morse_to_text("") == ""
