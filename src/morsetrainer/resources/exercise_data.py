"""Training exercise data for the translation and test modes.

Only plain text is stored here. The Morse versions are generated from it with
the translator (see ``services.data_provider``), so prompts and answers can
never disagree with each other.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Direction = Literal["text_to_morse", "morse_to_text"]
Category = Literal["word", "sentence"]


@dataclass(frozen=True)
class TestItemData:
	"""One test question: *text* is shown as-is or as Morse depending on *direction*."""

	text: str
	direction: Direction
	category: Category


TRANSLATION_SENTENCES: tuple[str, ...] = (
	"Programmeerimine",
	"Morsekood",
	"Marcus Kommussaar",
	"Sander Sirge",
	"Tartu linn",
	"Tartu Ülikool",
	"2 valget kassi",
	"1632",
	"Must & valge koer",
	"Delta keskus",
	"Tartu Ülikool asutati aastal 1632.",
	"Programmeerimine on eriti lahe!",
	"Kas sinule meeldib Pythoni keel?",
	"(x + y - z) = 420",
	"Meie email ei ole morsekood@morsekood.com",
	"Meie projektikood on PROJEKT-MORSEKOOD.py",
	"Praktikumid tulevad suureks kasuks.",
	"Kellegi arvutis jookseb 875 protsessi.",
	'"See on tsitaat, vist": Sander Sirge 2023',
	"Google'i 4. kvartali tulu oli 75,33 mld dollarit.",
)

TEST_ITEMS: tuple[TestItemData, ...] = (
	# Text shown, answer typed in Morse
	TestItemData("Programmeerimine", "text_to_morse", "word"),
	TestItemData("Morsekood", "text_to_morse", "word"),
	TestItemData("Linux", "text_to_morse", "word"),
	TestItemData("Windows", "text_to_morse", "word"),
	TestItemData("Android", "text_to_morse", "word"),
	TestItemData("Tartu Ülikool asutati aastal 1632.", "text_to_morse", "sentence"),
	TestItemData("Google'i 4. kvartali tulu oli 75,33 mld dollarit", "text_to_morse", "sentence"),
	TestItemData("Apple on parem kui Android?", "text_to_morse", "sentence"),
	TestItemData("Diskreetne matemaatika on raske!", "text_to_morse", "sentence"),
	TestItemData("Informaatika eriala on ainus sobiv valik", "text_to_morse", "sentence"),
	# Morse shown, answer typed as text
	TestItemData("Tartu Ülikool", "morse_to_text", "word"),
	TestItemData("Must & valge koer", "morse_to_text", "word"),
	TestItemData("Kernel", "morse_to_text", "word"),
	TestItemData("Javascript", "morse_to_text", "word"),
	TestItemData("Kasutajaliides", "morse_to_text", "word"),
	TestItemData("Kellegi arvutis jookseb 875 protsessi.", "morse_to_text", "sentence"),
	TestItemData("Praktikumid tulevad suureks kasuks.", "morse_to_text", "sentence"),
	TestItemData(
		"Ural on aastatel 1959-1971 toodetud elektronarvutite seeria.", "morse_to_text", "sentence"
	),
	TestItemData("Kas sa kordasid testiks?", "morse_to_text", "sentence"),
	TestItemData("Edu teile eksamil!", "morse_to_text", "sentence"),
)

__all__ = [
	"Category",
	"Direction",
	"TEST_ITEMS",
	"TRANSLATION_SENTENCES",
	"TestItemData",
]
