"""Flashcard navigation utilities for the learning views."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Flashcard:
    """Represents a single flashcard with front/back text."""

    front: str
    back: str


class FlashcardSession:
    """Maintain sequential navigation state for a flashcard deck."""

    def __init__(self, cards: Sequence[Flashcard] | Sequence[tuple[str, str]] = ()) -> None:
        self._cards: list[Flashcard] = [
            card if isinstance(card, Flashcard) else Flashcard(*card)
            for card in cards
        ]
        self.index = 0

    def is_empty(self) -> bool:
        return len(self._cards) == 0

    @property
    def total(self) -> int:
        return len(self._cards)

    def current(self) -> Flashcard:
        if self.is_empty():
            raise IndexError("FlashcardSession has no cards")
        return self._cards[self.index]

    def add_cards(self, cards: Iterable[tuple[str, str]] | Iterable[Flashcard]) -> None:
        for card in cards:
            self._cards.append(card if isinstance(card, Flashcard) else Flashcard(*card))

    def reset(self) -> None:
        self.index = 0

    def is_first(self) -> bool:
        return self.index == 0

    def is_last(self) -> bool:
        return self.is_empty() or self.index >= self.total - 1

    def move_next(self) -> bool:
        if self.is_last():
            return False
        self.index += 1
        return True

    def move_previous(self) -> bool:
        if self.is_first():
            return False
        self.index -= 1
        return True

    def progress_percentage(self) -> float:
        if self.is_empty():
            return 0.0
        if self.total <= 1:
            return 0.0
        return round((self.index / (self.total - 1)) * 100, 1)


__all__ = ["Flashcard", "FlashcardSession"]
