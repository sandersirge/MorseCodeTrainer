"""Business logic for the timed Morse-code test."""

from __future__ import annotations

import random
import re
from collections.abc import Sequence
from dataclasses import dataclass
from difflib import SequenceMatcher

from ..exceptions import MismatchedDataError, SessionInvalidStateError
from ..strings import t
from ..utils.morse_translator import split_morse_words

_MORSE_ONLY = re.compile(r"[.\-\s/]+")
_FULL_POINTS = 1.0
_HALF_POINTS = 0.5
_HALF_POINTS_FROM_ACCURACY = 0.5


def answer_units(answer: str, *, morse: bool) -> list[str]:
	"""Split an answer into the units that get compared.

	Morse answers are compared letter by letter (word gaps are not scored, so
	spacing style doesn't matter). Text answers are compared character by
	character, ignoring case and repeated whitespace.
	"""

	if morse:
		return [letter for word in split_morse_words(answer) for letter in word]
	return list(" ".join(answer.upper().split()))


def score_answer(expected: str, given: str, *, morse: bool) -> float:
	"""1 point for an exact answer, ½ for at least half right, otherwise 0.

	"Half right" uses an alignment (difflib), so one missing or extra letter
	only costs that letter instead of shifting everything after it.
	"""

	expected_units = answer_units(expected, morse=morse)
	if not expected_units:
		return 0.0
	given_units = answer_units(given, morse=morse)
	if given_units == expected_units:
		return _FULL_POINTS
	matcher = SequenceMatcher(None, expected_units, given_units, autojunk=False)
	matched = sum(block.size for block in matcher.get_matching_blocks())
	accuracy = matched / max(len(expected_units), len(given_units))
	return _HALF_POINTS if accuracy >= _HALF_POINTS_FROM_ACCURACY else 0.0


def is_morse(text: str) -> bool:
	return bool(text.strip()) and _MORSE_ONLY.fullmatch(text) is not None


@dataclass
class TestResponse:
	"""Stores a single answered test question."""

	index: int
	prompt: str
	expected: str
	given: str
	elapsed: float
	score: float
	category: str


@dataclass
class TestSummary:
	"""Aggregated view of the whole test run."""

	responses: list[TestResponse]
	total_points: float
	max_points: int
	grade_text: str
	feedback: str
	word_speed: int
	sentence_speed: int

	@property
	def score_text(self) -> str:
		return t("grade.score", points=self.total_points, max_points=self.max_points)

	@property
	def answered_non_empty(self) -> int:
		return sum(1 for response in self.responses if response.given.strip())


class TestSession:
	"""Manages question order, scoring, and summaries for the timed test."""

	def __init__(
		self,
		prompts: Sequence[str],
		answers: Sequence[str],
		categories: Sequence[str] | None = None,
	) -> None:
		"""*categories* ("word"/"sentence") drive the speed statistics.

		When omitted, prompts of one or two words count as "word".
		"""
		if len(prompts) != len(answers):
			raise MismatchedDataError("TestSession requires equal numbers of prompts and answers")
		if categories is not None and len(categories) != len(prompts):
			raise MismatchedDataError("TestSession requires one category per prompt")
		self._prompts = list(prompts)
		self._answers = list(answers)
		self._categories = (
			list(categories)
			if categories is not None
			else [_infer_category(prompt, answer) for prompt, answer in zip(prompts, answers)]
		)
		self._total_questions = len(self._prompts)
		self._order: list[int] = []
		self._position: int = -1
		self._responses: dict[int, TestResponse] = {}
		self.reset()

	def reset(self) -> None:
		"""Clear state so a fresh test run can begin."""

		self._order = list(range(self._total_questions))
		if self._order:
			random.shuffle(self._order)
			self._position = 0
		else:
			self._position = -1
		self._responses = {}

	@property
	def total_questions(self) -> int:
		return self._total_questions

	@property
	def answered_count(self) -> int:
		return len(self._responses)

	def current_prompt(self) -> str | None:
		if self._position == -1:
			return None
		return self._prompts[self._order[self._position]]

	def next_question(self) -> str:
		"""Move to the next question in the shuffled order."""

		if not self.has_next_question():
			raise StopIteration("No questions left in the session")
		self._position += 1
		return self.current_prompt()

	def previous_question(self) -> str:
		"""Move to the previous question in the shuffled order."""

		if not self.has_previous_question():
			raise StopIteration("Already at the first question")
		self._position -= 1
		return self.current_prompt()

	def has_next_question(self) -> bool:
		if self._position == -1:
			return False
		return self._position < self._total_questions - 1

	def has_previous_question(self) -> bool:
		return self._position > 0

	def current_index(self) -> int | None:
		if self._position == -1:
			return None
		return self._order[self._position]

	def current_position(self) -> int:
		return self._position

	def record_response(self, answer: str, elapsed: float) -> TestResponse:
		"""Store an answer together with timing information."""

		index = self.current_index()
		if index is None:
			raise SessionInvalidStateError("Cannot record a response without an active question")

		response = self._build_response(index, answer or "", elapsed)
		self._responses[index] = response
		return response

	def responses(self) -> list[TestResponse]:
		return list(self._responses.values())

	def current_answer(self) -> str:
		index = self.current_index()
		if index is None:
			return ""
		response = self._responses.get(index)
		return response.given if response else ""

	def all_answered(self) -> bool:
		return self.answered_count >= self._total_questions

	def _build_response(self, index: int, given: str, elapsed: float) -> TestResponse:
		expected = self._answers[index]
		score = score_answer(expected, given, morse=is_morse(expected))
		return TestResponse(
			index=index,
			prompt=self._prompts[index],
			expected=expected,
			given=given,
			elapsed=elapsed,
			score=score,
			category=self._categories[index],
		)

	def summary(self) -> TestSummary:
		"""Produce aggregated scoring and speed information."""

		ordered_responses: list[TestResponse] = []
		for index in self._order:
			response = self._responses.get(index)
			if response is None:
				response = self._build_response(index, "", 0.0)
			ordered_responses.append(response)

		total_points = sum(response.score for response in ordered_responses)
		percentage = (total_points / self._total_questions) * 100 if self._total_questions else 0
		rounded_percentage = round(percentage, 1)
		grade_text, feedback = _grade_and_feedback(rounded_percentage)
		word_speed = _speed_from_times(
			[response.elapsed for response in ordered_responses if response.category == "word"]
		)
		sentence_speed = _speed_from_times(
			[response.elapsed for response in ordered_responses if response.category == "sentence"]
		)
		return TestSummary(
			responses=ordered_responses,
			total_points=total_points,
			max_points=self._total_questions,
			grade_text=grade_text,
			feedback=feedback,
			word_speed=word_speed,
			sentence_speed=sentence_speed,
		)


def _infer_category(prompt: str, answer: str) -> str:
	text = answer if is_morse(prompt) else prompt
	return "word" if len(text.split()) <= 2 else "sentence"


def _speed_from_times(entries: Sequence[float]) -> int:
	if not entries:
		return 0
	total_time = sum(entries)
	if total_time <= 0:
		return 0
	return round(len(entries) / total_time * 60)


def _grade_and_feedback(percentage: float) -> tuple[str, str]:
	if percentage <= 50:
		return (
			t("grade.f", percentage=percentage),
			t("grade.punktisumma_pole_just_koige"),
		)
	if percentage <= 60:
		return (
			t("grade.e", percentage=percentage),
			t("grade.punktisumma_pole_just_koige"),
		)
	if percentage <= 70:
		return (
			t("grade.d", percentage=percentage),
			t("grade.hakkab_juba_vaikselt_tulema"),
		)
	if percentage <= 80:
		return (
			t("grade.c", percentage=percentage),
			t("grade.hakkab_juba_vaikselt_tulema"),
		)
	if percentage <= 90:
		return (
			t("grade.b", percentage=percentage),
			t("grade.paris_hea_tundub_et"),
		)
	return (
		t("grade.a", percentage=percentage),
		t("grade.vaga_super_oled_testi"),
	)
