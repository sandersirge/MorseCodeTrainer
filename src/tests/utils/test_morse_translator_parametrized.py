"""Parametrized tests for morse_translator — full letter/number/symbol coverage."""

from __future__ import annotations

import pytest

from src.main.python.resources.morse_data import LETTER_MORSE_PAIRS, NUMBER_SYMBOL_MORSE_PAIRS
from src.main.python.utils.morse_translator import convert_morse_to_text, convert_text_to_morse


@pytest.mark.parametrize("letter,expected_morse", LETTER_MORSE_PAIRS)
def test_encode_lowercase_letter(letter: str, expected_morse: str) -> None:
	"""Every lowercase letter encodes to its standard Morse representation."""
	assert convert_text_to_morse(letter) == expected_morse


@pytest.mark.parametrize("letter,expected_morse", LETTER_MORSE_PAIRS)
def test_encode_uppercase_letter(letter: str, expected_morse: str) -> None:
	"""Every uppercase letter encodes to the same Morse as its lowercase form."""
	assert convert_text_to_morse(letter.upper()) == expected_morse


@pytest.mark.parametrize(
	"char,expected_morse",
	[(c, m) for c, m in NUMBER_SYMBOL_MORSE_PAIRS if c.isdigit()],
)
def test_encode_digit(char: str, expected_morse: str) -> None:
	"""Every digit 0-9 encodes to its correct Morse sequence."""
	assert convert_text_to_morse(char) == expected_morse


@pytest.mark.parametrize(
	"char,expected_morse",
	[(c, m) for c, m in NUMBER_SYMBOL_MORSE_PAIRS if not c.isdigit()],
)
def test_encode_symbol(char: str, expected_morse: str) -> None:
	"""Every supported punctuation/symbol encodes to its correct Morse sequence."""
	assert convert_text_to_morse(char) == expected_morse


@pytest.mark.parametrize("letter,morse", LETTER_MORSE_PAIRS)
def test_round_trip_single_letter(letter: str, morse: str) -> None:
	"""Encoding then decoding any letter yields either uppercase (first position) letter."""
	encoded = convert_text_to_morse(letter)
	decoded = convert_morse_to_text(encoded)
	assert decoded.lower() == letter.lower()


@pytest.mark.parametrize(
	"char,morse",
	[(c, m) for c, m in NUMBER_SYMBOL_MORSE_PAIRS if c.isdigit()],
)
def test_round_trip_digit(char: str, morse: str) -> None:
	"""Encoding then decoding any digit is lossless."""
	assert convert_morse_to_text(convert_text_to_morse(char)) == char


@pytest.mark.parametrize(
	"char,morse",
	[(c, m) for c, m in NUMBER_SYMBOL_MORSE_PAIRS if not c.isdigit()],
)
def test_round_trip_symbol(char: str, morse: str) -> None:
	"""Encoding then decoding any symbol is lossless."""
	assert convert_morse_to_text(convert_text_to_morse(char)) == char


@pytest.mark.parametrize("letter,morse", LETTER_MORSE_PAIRS)
def test_decode_morse_letter(letter: str, morse: str) -> None:
	"""Decoding the Morse of a letter yields a non-empty alphabetic string."""
	result = convert_morse_to_text(morse)
	assert result
	assert result.lower() == letter.lower()
