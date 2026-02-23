"""Training data navigation and scoring helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TranslationSession:
    """Holds the state for iterating over paired prompts and answers."""

    prompts: list[str]
    answers: list[str]
    index: int = 0

    def __post_init__(self) -> None:
        if len(self.prompts) != len(self.answers):
            raise ValueError("TranslationSession requires equal numbers of prompts and answers")
        if not self.prompts:
            self.index = 0
            return
        if not 0 <= self.index < len(self.prompts):
            raise ValueError("TranslationSession index must point to an existing prompt")

    @property
    def total(self) -> int:
        return len(self.prompts)

    def current_prompt(self) -> str:
        if not self.prompts:
            raise IndexError("No prompts available")
        return self.prompts[self.index]

    def current_answer(self) -> str:
        if not self.answers:
            raise IndexError("No answers available")
        return self.answers[self.index]

    def is_last(self) -> bool:
        return self.total == 0 or self.index >= self.total - 1

    def is_first(self) -> bool:
        return self.index == 0

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

    def reset(self) -> None:
        self.index = 0


__all__ = ["TranslationSession"]
