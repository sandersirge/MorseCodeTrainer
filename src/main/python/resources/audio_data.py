"""Audio asset path maps for Morse code training resources."""

from __future__ import annotations

from .morse_data import LETTER_MORSE_PAIRS, NUMBER_SYMBOL_MORSE_PAIRS

LETTER_AUDIO_MAP = {
	f"{letter.upper()} {letter}": f"resources/letters/{letter.upper()}.wav"
	for letter, _ in LETTER_MORSE_PAIRS
}

NUMBER_AUDIO_MAP = {
	char: f"resources/numbers/{char}.wav" for char, _ in NUMBER_SYMBOL_MORSE_PAIRS if char.isdigit()
}

_SYMBOL_AUDIO_LABELS = (
	("_", "alakriips"),
	("&", "ja"),
	("'", "ülakoma"),
	("@", "ät"),
	("(", "avav_sulg"),
	("$", "dollar"),
	("!", "hüüumärk"),
	("/", "kaldkriips"),
	(",", "koma"),
	(":", "koolon"),
	("?", "küsimärk"),
	("+", "pluss"),
	(".", "punkt"),
	(";", "semikoolon"),
	(")", "sulgev_sulg"),
	("=", "võrdusmärk"),
	('"', "jutumärk"),
	("-", "miinus"),
)

SYMBOL_AUDIO_MAP = {
	symbol: f"resources/symbols/{slug}.wav" for symbol, slug in _SYMBOL_AUDIO_LABELS
}

LETTER_AUDIO_KEYS = LETTER_AUDIO_MAP.keys()
NUMBER_AUDIO_KEYS = NUMBER_AUDIO_MAP.keys()
SYMBOL_AUDIO_KEYS = SYMBOL_AUDIO_MAP.keys()

__all__ = [
	"LETTER_AUDIO_MAP",
	"NUMBER_AUDIO_MAP",
	"SYMBOL_AUDIO_MAP",
	"LETTER_AUDIO_KEYS",
	"NUMBER_AUDIO_KEYS",
	"SYMBOL_AUDIO_KEYS",
]
