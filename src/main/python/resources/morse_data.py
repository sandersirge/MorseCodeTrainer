"""Morse code symbol tables and lookup maps."""

from __future__ import annotations

LETTER_MORSE_PAIRS = (
	("a", ".-"),
	("b", "-..."),
	("c", "-.-."),
	("d", "-.."),
	("e", "."),
	("f", "..-."),
	("g", "--."),
	("h", "...."),
	("i", ".."),
	("j", ".---"),
	("k", "-.-"),
	("l", ".-.."),
	("m", "--"),
	("n", "-."),
	("o", "---"),
	("p", ".--."),
	("q", "--.-"),
	("r", ".-."),
	("s", "..."),
	("š", "----"),
	("t", "-"),
	("u", "..-"),
	("v", "...-"),
	("w", ".--"),
	("ä", ".-.-"),
	("ö", "---."),
	("ü", "..--"),
	("x", "-..-"),
	("y", "-.--"),
	("z", "--.."),
)

LETTER_TO_MORSE_MAP: dict[str, str] = {}
for _letter, _code in LETTER_MORSE_PAIRS:
	LETTER_TO_MORSE_MAP[_letter] = _code
	LETTER_TO_MORSE_MAP[_letter.upper()] = _code

NUMBER_SYMBOL_MORSE_PAIRS = (
	("1", ".----"),
	("2", "..---"),
	("3", "...--"),
	("4", "....-"),
	("5", "....."),
	("6", "-...."),
	("7", "--..."),
	("8", "---.."),
	("9", "----."),
	("0", "-----"),
	(",", "--..--"),
	(".", ".-.-.-"),
	("!", "-.-.--"),
	("?", "..--.."),
	("/", "-..-."),
	("-", "-....-"),
	("'", ".----."),
	('"', ".-..-."),
	(":", "---..."),
	(";", "-.-.-."),
	("+", ".-.-."),
	("=", "-...-"),
	("(", "-.--."),
	(")", "-.--.-"),
	("&", ".-..."),
	("$", "...-..-"),
	("@", ".--.-."),
	("_", "..--.-"),
)

NUMBER_TO_MORSE_MAP = {char: code for char, code in NUMBER_SYMBOL_MORSE_PAIRS if char.isdigit()}
SYMBOL_TO_MORSE_MAP = {char: code for char, code in NUMBER_SYMBOL_MORSE_PAIRS if not char.isdigit()}

# Pre-computed key views for faster lookup
UPPERCASE_LETTER_KEYS = tuple(letter.upper() for letter, _ in LETTER_MORSE_PAIRS)
UPPERCASE_LETTER_ORDER = UPPERCASE_LETTER_KEYS
LOWERCASE_LETTER_KEYS = tuple(letter for letter, _ in LETTER_MORSE_PAIRS)
LOWERCASE_LETTER_ORDER = LOWERCASE_LETTER_KEYS
NUMBER_KEYS = tuple(char for char, _ in NUMBER_SYMBOL_MORSE_PAIRS if char.isdigit())
NUMBER_ORDER = NUMBER_KEYS
SYMBOL_KEYS = tuple(char for char, _ in NUMBER_SYMBOL_MORSE_PAIRS if not char.isdigit())
SYMBOL_ORDER = SYMBOL_KEYS

__all__ = [
	"LETTER_MORSE_PAIRS",
	"LETTER_TO_MORSE_MAP",
	"NUMBER_SYMBOL_MORSE_PAIRS",
	"NUMBER_TO_MORSE_MAP",
	"SYMBOL_TO_MORSE_MAP",
	"UPPERCASE_LETTER_KEYS",
	"UPPERCASE_LETTER_ORDER",
	"LOWERCASE_LETTER_KEYS",
	"LOWERCASE_LETTER_ORDER",
	"NUMBER_KEYS",
	"NUMBER_ORDER",
	"SYMBOL_KEYS",
	"SYMBOL_ORDER",
]
