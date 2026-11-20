"""Training helpers: Koch lessons, weak-first ordering, copy scoring, word drills."""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import TypeVar

_T = TypeVar("_T")

# Koch order as used by LCWO: easy-to-tell-apart sounds first, then the rest.
# The Estonian letters come last, once the international set is known.
KOCH_ORDER: tuple[str, ...] = tuple("KMURESNAPTLWI.JZ=FOY,VG5/Q92H38B?47C1D60X") + (
	"Ä",
	"Ö",
	"Ü",
	"Š",
	"Ž",
)
KOCH_PASS_ACCURACY = 0.9


def koch_characters(level: int) -> list[str]:
	"""The characters unlocked at *level* (level 2 = the first two)."""
	return list(KOCH_ORDER[: max(2, min(level, len(KOCH_ORDER)))])


def weighted_order(
	items: Sequence[_T], weight: Callable[[_T], float], rng: random.Random
) -> list[_T]:
	"""Random order where heavier items tend to come first (each still appears once).

	Efraimidis–Spirakis weighted shuffle: sort by u ** (1 / w).
	"""
	keyed = [(rng.random() ** (1.0 / max(weight(item), 1e-6)), item) for item in items]
	return [item for _, item in sorted(keyed, key=lambda pair: pair[0], reverse=True)]


def koch_groups(
	chars: Sequence[str],
	rng: random.Random,
	*,
	groups: int = 5,
	group_size: int = 5,
	focus: str | None = None,
) -> str:
	"""Random letter groups ("KMMKU MUKKM ...") from *chars*.

	The newest character (*focus*) appears about a third of the time so it
	gets extra practice.
	"""
	pool = list(chars)
	result = []
	for _ in range(groups):
		group = []
		for _ in range(group_size):
			if focus and rng.random() < 1 / 3:
				group.append(focus)
			else:
				group.append(rng.choice(pool))
		result.append("".join(group))
	return " ".join(result)


@dataclass
class CopyResult:
	"""Outcome of copying (typing) what was heard."""

	expected: str
	given: str
	correct: int
	total: int
	per_char: dict[str, tuple[int, int]] = field(default_factory=dict)  # char -> (correct, wrong)

	@property
	def accuracy(self) -> float:
		return self.correct / self.total if self.total else 0.0


def score_copy(expected: str, given: str) -> CopyResult:
	"""Compare characters (spaces ignored, case-insensitive) with an alignment.

	A missed or extra character costs only itself; every expected character is
	counted as right or wrong for the per-character statistics.
	"""
	exp = [c for c in expected.upper() if not c.isspace()]
	got = [c for c in given.upper() if not c.isspace()]
	matched = [False] * len(exp)
	for block in SequenceMatcher(None, exp, got, autojunk=False).get_matching_blocks():
		for i in range(block.a, block.a + block.size):
			matched[i] = True
	per_char: dict[str, tuple[int, int]] = {}
	for char, ok in zip(exp, matched):
		right, wrong = per_char.get(char, (0, 0))
		per_char[char] = (right + ok, wrong + (not ok))
	# Extra typed characters lower the score too.
	extra = max(0, len(got) - sum(matched))
	total = len(exp) + extra
	return CopyResult(expected, given, sum(matched), total, per_char)


def word_drill(
	words: Sequence[str],
	weakness: Callable[[str], float],
	rng: random.Random,
	*,
	count: int = 10,
	max_words: int = 3,
) -> list[str]:
	"""Short phrases of 1–*max_words* random words, favouring weak letters."""

	def word_weight(word: str) -> float:
		# A word is worth practising if it contains at least one weak letter.
		return 0.1 + max(weakness(c) for c in word.upper())

	weights = [word_weight(w) for w in words]
	phrases = []
	for _ in range(count):
		size = rng.randint(1, max_words)
		phrases.append(" ".join(rng.choices(list(words), weights=weights, k=size)))
	return phrases


__all__ = [
	"KOCH_ORDER",
	"KOCH_PASS_ACCURACY",
	"CopyResult",
	"koch_characters",
	"koch_groups",
	"score_copy",
	"weighted_order",
	"word_drill",
]
