"""Utility functions for converting between text and Morse code.

Conventions used throughout the app:
- letters inside a word are separated by one space
- words are separated by three spaces
- when reading Morse, a newline or a ``/`` also counts as a word break
- Morse has no letter case, so decoded text is always UPPERCASE
"""

from __future__ import annotations

import re

from ..exceptions import UnsupportedCharacterError, UnsupportedMorseSymbolError
from ..resources import constants as consts

WORD_SEPARATOR = "   "
LETTER_SEPARATOR = " "

_TEXT_TO_MORSE: dict[str, str] = {
	**consts.LETTER_TO_MORSE_MAP,
	**consts.NUMBER_TO_MORSE_MAP,
	**consts.SYMBOL_TO_MORSE_MAP,
}

_MORSE_TO_TEXT: dict[str, str] = {}
for _letter, _code in consts.LETTER_MORSE_PAIRS:
	_MORSE_TO_TEXT[_code] = _letter.upper()
for _char, _code in (*consts.NUMBER_TO_MORSE_MAP.items(), *consts.SYMBOL_TO_MORSE_MAP.items()):
	_MORSE_TO_TEXT[_code] = _char

# A word break in Morse input: a slash or a newline (with any spaces around
# it), or two or more spaces/tabs.
_MORSE_WORD_BREAK = re.compile(r"\s*/\s*|\s*\n\s*|[ \t]{2,}")


def convert_text_to_morse(message: str) -> str:
	"""Translate plain text into a Morse code string.

	Any run of whitespace (spaces, tabs, newlines) becomes one word break.
	"""

	morse_words: list[str] = []
	for word in message.split():
		symbols: list[str] = []
		for char in word:
			code = _TEXT_TO_MORSE.get(char)
			if code is None:
				raise UnsupportedCharacterError(char)
			symbols.append(code)
		morse_words.append(LETTER_SEPARATOR.join(symbols))
	return WORD_SEPARATOR.join(morse_words)


def split_morse_words(message: str) -> list[list[str]]:
	"""Split Morse input into words, each a list of letter codes."""

	words: list[list[str]] = []
	for chunk in _MORSE_WORD_BREAK.split(message.strip()):
		letters = chunk.split()
		if letters:
			words.append(letters)
	return words


def convert_morse_to_text(message: str) -> str:
	"""Translate a Morse string back into (uppercase) text."""

	decoded_words: list[str] = []
	for letters in split_morse_words(message):
		chars: list[str] = []
		for symbol in letters:
			char = _MORSE_TO_TEXT.get(symbol)
			if char is None:
				raise UnsupportedMorseSymbolError(symbol)
			chars.append(char)
		decoded_words.append("".join(chars))
	return " ".join(decoded_words)


def normalize_morse(message: str) -> str:
	"""Canonical spacing: one space between letters, three between words."""

	return WORD_SEPARATOR.join(LETTER_SEPARATOR.join(word) for word in split_morse_words(message))


def format_morse_for_display(message: str, line_width: int = 44) -> str:
	"""Canonical Morse with line breaks only *between* words.

	Labels that wrap on their own could split a word across lines, which makes
	a letter gap look like a word gap. A newline counts as a word break when
	the text is read back, so the result still translates correctly.
	"""

	lines: list[str] = []
	current = ""
	for word in (LETTER_SEPARATOR.join(letters) for letters in split_morse_words(message)):
		candidate = f"{current}{WORD_SEPARATOR}{word}" if current else word
		if current and len(candidate) > line_width:
			lines.append(current)
			current = word
		else:
			current = candidate
	if current:
		lines.append(current)
	return "\n".join(lines)


__all__ = [
	"LETTER_SEPARATOR",
	"WORD_SEPARATOR",
	"convert_morse_to_text",
	"convert_text_to_morse",
	"format_morse_for_display",
	"normalize_morse",
	"split_morse_words",
]
