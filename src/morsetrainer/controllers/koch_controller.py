"""Koch-method listening lessons: hear random groups, type them, unlock the next character."""

from __future__ import annotations

import random
from dataclasses import dataclass

from ..model.training import (
	KOCH_ORDER,
	KOCH_PASS_ACCURACY,
	CopyResult,
	koch_characters,
	koch_groups,
	score_copy,
)
from ..services.progress_store import ProgressStore
from ..utils.morse_translator import convert_text_to_morse


@dataclass(frozen=True)
class KochState:
	level: int
	max_level: int
	characters: list[str]
	new_char: str
	new_char_morse: str
	has_exercise: bool
	result: CopyResult | None
	passed: bool
	leveled_up: bool


class KochPresenter:
	"""Level = how many characters of the Koch order are unlocked (saved between runs)."""

	def __init__(self, progress: ProgressStore, rng: random.Random | None = None) -> None:
		self._progress = progress
		self._rng = rng or random.Random()
		self._exercise = ""
		self._result: CopyResult | None = None
		self._leveled_up = False

	@property
	def level(self) -> int:
		return min(self._progress.koch_level, len(KOCH_ORDER))

	def current_state(self) -> KochState:
		chars = koch_characters(self.level)
		new_char = chars[-1]
		passed = self._result is not None and self._result.accuracy >= KOCH_PASS_ACCURACY
		return KochState(
			level=self.level,
			max_level=len(KOCH_ORDER),
			characters=chars,
			new_char=new_char,
			new_char_morse=convert_text_to_morse(new_char),
			has_exercise=bool(self._exercise),
			result=self._result,
			passed=passed,
			leveled_up=self._leveled_up,
		)

	def new_exercise(self) -> KochState:
		chars = koch_characters(self.level)
		self._exercise = koch_groups(chars, self._rng, focus=chars[-1])
		self._result = None
		self._leveled_up = False
		return self.current_state()

	def exercise_morse(self) -> str:
		"""Groups as Morse words, ready to play."""
		return convert_text_to_morse(self._exercise) if self._exercise else ""

	def new_char_morse(self) -> str:
		"""The newest character three times, to learn its sound."""
		new_char = koch_characters(self.level)[-1]
		return convert_text_to_morse(" ".join([new_char] * 3))

	def check(self, given: str) -> KochState:
		"""Score the typed copy; 90 % or better unlocks the next character."""
		if not self._exercise:
			return self.current_state()
		self._result = score_copy(self._exercise, given)
		self._progress.record_many(self._result.per_char)
		self._leveled_up = False
		if self._result.accuracy >= KOCH_PASS_ACCURACY and self.level < len(KOCH_ORDER):
			self._progress.set_koch_level(self.level + 1)
			self._leveled_up = True
		return self.current_state()

	@property
	def exercise_text(self) -> str:
		return self._exercise

	def change_level(self, delta: int) -> KochState:
		"""Manual override, e.g. for someone who already knows some characters."""
		new_level = max(2, min(len(KOCH_ORDER), self.level + delta))
		self._progress.set_koch_level(new_level)
		self._exercise = ""
		self._result = None
		self._leveled_up = False
		return self.current_state()


__all__ = ["KochPresenter", "KochState"]
