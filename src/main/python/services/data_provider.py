from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from types import MappingProxyType
from typing import Mapping, Tuple, TypeVar

from ..model.flashcard_session import FlashcardSession
from ..model.test_session import TestSession
from ..model.translation_session import TranslationSession
from ..resources import constants as consts

CardPair = Tuple[str, str]
_T = TypeVar("_T")


def _frozen_mapping(data: Mapping[str, _T]) -> Mapping[str, _T]:
    """Return an immutable mapping copy so callers cannot mutate shared data."""

    return MappingProxyType(dict(data))


@dataclass(frozen=True)
class TranslationResources:
    morse_to_text: TranslationSession
    text_to_morse: TranslationSession
    audio_map: Mapping[str, str]


@dataclass(frozen=True)
class FlashcardResources:
    sessions: Mapping[str, FlashcardSession]
    audio_map: Mapping[str, str]


@dataclass(frozen=True)
class FlashcardStaticData:
    letter_cards: Tuple[CardPair, ...]
    number_cards: Tuple[CardPair, ...]
    symbol_cards: Tuple[CardPair, ...]
    audio_map: Mapping[str, str]


def create_translation_resources() -> TranslationResources:
    morse_session = TranslationSession(
        prompts=list(consts.TRANSLATION_MORSE_SAMPLES),
        answers=list(consts.TRANSLATION_TEXT_SAMPLES),
    )
    text_session = TranslationSession(
        prompts=list(consts.TRANSLATION_TEXT_SAMPLES),
        answers=list(consts.TRANSLATION_MORSE_SAMPLES),
    )
    audio_map = _frozen_mapping(consts.PHRASE_AUDIO_MAP)
    return TranslationResources(
        morse_to_text=morse_session,
        text_to_morse=text_session,
        audio_map=audio_map,
    )


def create_test_session() -> TestSession:
    return TestSession(
        prompts=list(consts.TEST_TEXT_PROMPTS),
        answers=list(consts.TEST_MORSE_ANSWERS),
    )


@lru_cache(maxsize=1)
def _load_flashcard_static_data() -> FlashcardStaticData:
    letter_cards: Tuple[CardPair, ...] = tuple(
        (f"{upper} {lower}", consts.LETTER_TO_MORSE_MAP[upper])
        for upper, lower in zip(consts.UPPERCASE_LETTER_ORDER, consts.LOWERCASE_LETTER_ORDER)
    )
    number_cards: Tuple[CardPair, ...] = tuple(
        (number, consts.NUMBER_TO_MORSE_MAP[number])
        for number in consts.NUMBER_ORDER
    )
    symbol_cards: Tuple[CardPair, ...] = tuple(
        (symbol, consts.SYMBOL_TO_MORSE_MAP[symbol])
        for symbol in consts.SYMBOL_ORDER
    )
    audio_map = _frozen_mapping({
        **consts.LETTER_AUDIO_MAP,
        **consts.NUMBER_AUDIO_MAP,
        **consts.SYMBOL_AUDIO_MAP,
    })
    return FlashcardStaticData(
        letter_cards=letter_cards,
        number_cards=number_cards,
        symbol_cards=symbol_cards,
        audio_map=audio_map,
    )


def load_letter_cards() -> Tuple[CardPair, ...]:
    return _load_flashcard_static_data().letter_cards


def load_number_cards() -> Tuple[CardPair, ...]:
    return _load_flashcard_static_data().number_cards


def load_symbol_cards() -> Tuple[CardPair, ...]:
    return _load_flashcard_static_data().symbol_cards


def load_flashcard_audio_map() -> Mapping[str, str]:
    return _load_flashcard_static_data().audio_map


def create_flashcard_resources() -> FlashcardResources:
    static_data = _load_flashcard_static_data()
    sessions = {
        "tähed": FlashcardSession(static_data.letter_cards),
        "numbrid": FlashcardSession(static_data.number_cards),
        "märgid": FlashcardSession(static_data.symbol_cards),
    }
    return FlashcardResources(
        sessions=_frozen_mapping(sessions),
        audio_map=static_data.audio_map,
    )


__all__ = [
    "TranslationResources",
    "FlashcardResources",
    "create_flashcard_resources",
    "create_test_session",
    "create_translation_resources",
    "load_flashcard_audio_map",
    "load_letter_cards",
    "load_number_cards",
    "load_symbol_cards",
]
