from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from types import MappingProxyType
from typing import TypeVar

from ..model.flashcard_session import FlashcardSession
from ..model.test_session import TestSession
from ..model.translation_session import TranslationSession
from ..resources import constants as consts
from ..utils.morse_translator import convert_text_to_morse, format_morse_for_display

CardPair = tuple[str, str]
_T = TypeVar("_T")


def _frozen_mapping(data: Mapping[str, _T]) -> Mapping[str, _T]:
	"""Return an immutable mapping copy so callers cannot mutate shared data."""

	return MappingProxyType(dict(data))


def to_display_morse(text: str) -> str:
	"""Translate *text* and lay it out for on-screen display."""

	return format_morse_for_display(convert_text_to_morse(text))


@dataclass(frozen=True)
class TranslationResources:
	morse_to_text: TranslationSession
	text_to_morse: TranslationSession


@dataclass(frozen=True)
class FlashcardResources:
	sessions: Mapping[str, FlashcardSession]


@dataclass(frozen=True)
class FlashcardStaticData:
	letter_cards: tuple[CardPair, ...]
	number_cards: tuple[CardPair, ...]
	symbol_cards: tuple[CardPair, ...]


def create_translation_resources() -> TranslationResources:
	texts = list(consts.TRANSLATION_SENTENCES)
	morse = [to_display_morse(text) for text in texts]
	return TranslationResources(
		morse_to_text=TranslationSession(prompts=morse, answers=list(texts)),
		text_to_morse=TranslationSession(prompts=list(texts), answers=morse),
	)


def create_test_session() -> TestSession:
	prompts: list[str] = []
	answers: list[str] = []
	categories: list[str] = []
	for item in consts.TEST_ITEMS:
		morse = to_display_morse(item.text)
		if item.direction == "text_to_morse":
			prompts.append(item.text)
			answers.append(morse)
		else:
			prompts.append(morse)
			answers.append(item.text)
		categories.append(item.category)
	return TestSession(prompts=prompts, answers=answers, categories=categories)


@lru_cache(maxsize=1)
def _load_flashcard_static_data() -> FlashcardStaticData:
	letter_cards: tuple[CardPair, ...] = tuple(
		(f"{upper} {lower}", consts.LETTER_TO_MORSE_MAP[upper])
		for upper, lower in zip(consts.UPPERCASE_LETTER_ORDER, consts.LOWERCASE_LETTER_ORDER)
	)
	number_cards: tuple[CardPair, ...] = tuple(
		(number, consts.NUMBER_TO_MORSE_MAP[number]) for number in consts.NUMBER_ORDER
	)
	symbol_cards: tuple[CardPair, ...] = tuple(
		(symbol, consts.SYMBOL_TO_MORSE_MAP[symbol]) for symbol in consts.SYMBOL_ORDER
	)
	return FlashcardStaticData(
		letter_cards=letter_cards,
		number_cards=number_cards,
		symbol_cards=symbol_cards,
	)


def load_letter_cards() -> tuple[CardPair, ...]:
	return _load_flashcard_static_data().letter_cards


def load_number_cards() -> tuple[CardPair, ...]:
	return _load_flashcard_static_data().number_cards


def load_symbol_cards() -> tuple[CardPair, ...]:
	return _load_flashcard_static_data().symbol_cards


def create_flashcard_resources() -> FlashcardResources:
	static_data = _load_flashcard_static_data()
	sessions = {
		"tähed": FlashcardSession(static_data.letter_cards),
		"numbrid": FlashcardSession(static_data.number_cards),
		"märgid": FlashcardSession(static_data.symbol_cards),
	}
	return FlashcardResources(sessions=_frozen_mapping(sessions))


__all__ = [
	"TranslationResources",
	"FlashcardResources",
	"create_flashcard_resources",
	"create_test_session",
	"create_translation_resources",
	"load_letter_cards",
	"load_number_cards",
	"load_symbol_cards",
	"to_display_morse",
]
