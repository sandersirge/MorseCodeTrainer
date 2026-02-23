"""Utility functions for converting between text and Morse code."""

from __future__ import annotations

from typing import Dict, Tuple

from ..resources import constants as consts


_LETTER_FROM_MORSE: Dict[str, Tuple[str, str]] = {}
for letter, code in consts.LETTER_MORSE_PAIRS:
    _LETTER_FROM_MORSE[code] = (letter.upper(), letter)

_NUMBER_FROM_MORSE: Dict[str, str] = {
    code: char for char, code in consts.NUMBER_TO_MORSE_MAP.items()
}

_SYMBOL_FROM_MORSE: Dict[str, str] = {
    code: char for char, code in consts.SYMBOL_TO_MORSE_MAP.items()
}


def convert_text_to_morse(message: str) -> str:
    """Translate plain text into a Morse code string."""

    if not message:
        return ""

    morse_words: list[str] = []
    for word in message.split(" "):
        if word == "":
            morse_words.append("")
            continue
        symbols: list[str] = []
        for char in word:
            if char in consts.LETTER_TO_MORSE_MAP:
                symbols.append(consts.LETTER_TO_MORSE_MAP[char])
            elif char in consts.NUMBER_TO_MORSE_MAP:
                symbols.append(consts.NUMBER_TO_MORSE_MAP[char])
            elif char in consts.SYMBOL_TO_MORSE_MAP:
                symbols.append(consts.SYMBOL_TO_MORSE_MAP[char])
            else:
                raise ValueError(f"Unsupported character '{char}' in input")
        morse_words.append(" ".join(symbols))
    return "   ".join(morse_words)


def convert_morse_to_text(message: str) -> str:
    """Translate a Morse string back into human-readable text."""

    if not message:
        return ""

    translation: list[str] = []
    previous_empty = False
    for symbol in message.split(" "):
        if symbol == "":
            if previous_empty and translation and translation[-1] != " ":
                translation.append(" ")
            previous_empty = True
            continue

        previous_empty = False
        if symbol in _LETTER_FROM_MORSE:
            upper, lower = _LETTER_FROM_MORSE[symbol]
            translation.append(upper if (not translation or translation[-1] == " ") else lower)
        elif symbol in _NUMBER_FROM_MORSE:
            translation.append(_NUMBER_FROM_MORSE[symbol])
        elif symbol in _SYMBOL_FROM_MORSE:
            translation.append(_SYMBOL_FROM_MORSE[symbol])
        else:
            raise ValueError(f"Unsupported Morse symbol '{symbol}' in input")
    return "".join(translation)


__all__ = ["convert_morse_to_text", "convert_text_to_morse"]
