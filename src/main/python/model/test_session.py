"""Business logic for the timed Morse-code test."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Sequence

_WORD_PROMPT_INDICES = {0, 1, 2, 3, 4, 10, 11, 12, 13, 14}
_SPLIT_AS_WORDS_THRESHOLD = 10


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

    responses: List[TestResponse]
    total_points: float
    max_points: int
    grade_text: str
    feedback: str
    word_speed: int
    sentence_speed: int

    @property
    def score_text(self) -> str:
        return f"Vastasid {self.total_points} / {self.max_points} õigesti"

    @property
    def answered_non_empty(self) -> int:
        return sum(1 for response in self.responses if response.given.strip())


class TestSession:
    """Manages question order, scoring, and summaries for the timed test."""

    def __init__(self, prompts: Sequence[str], answers: Sequence[str]) -> None:
        if len(prompts) != len(answers):
            raise ValueError("TestSession requires equal numbers of prompts and answers")
        self._prompts = list(prompts)
        self._answers = list(answers)
        self._total_questions = len(self._prompts)
        self._order: List[int] = []
        self._position: int = -1
        self._responses: Dict[int, TestResponse] = {}
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
            raise RuntimeError("Cannot record a response without an active question")

        response = self._build_response(index, answer or "", elapsed)
        self._responses[index] = response
        return response

    def responses(self) -> List[TestResponse]:
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
        category = "word" if index in _WORD_PROMPT_INDICES else "sentence"

        if index < _SPLIT_AS_WORDS_THRESHOLD:
            expected_units = expected.split(" ")
            given_units = given.split(" ")
        else:
            expected_units = list(expected)
            given_units = list(given)

        correct = 0
        for position, token in enumerate(given_units):
            if expected_units and position < len(expected_units) and token == expected_units[position]:
                correct += 1
            if expected_units and position == len(expected_units) - 1:
                break

        if not expected_units:
            score = 0.0
        else:
            accuracy = round(correct / len(expected_units), 1) * 100
            if 0 <= accuracy < 50:
                score = 0.0
            elif 50 <= accuracy < 100:
                score = 0.5
            else:
                score = 1.0

        return TestResponse(
            index=index,
            prompt=self._prompts[index],
            expected=expected,
            given=given,
            elapsed=elapsed,
            score=score,
            category=category,
        )

    def summary(self) -> TestSummary:
        """Produce aggregated scoring and speed information."""

        ordered_responses: List[TestResponse] = []
        for index in self._order:
            response = self._responses.get(index)
            if response is None:
                response = self._build_response(index, "", 0.0)
            ordered_responses.append(response)

        total_points = sum(response.score for response in ordered_responses)
        percentage = (total_points / self._total_questions) * 100 if self._total_questions else 0
        rounded_percentage = round(percentage, 1)
        grade_text, feedback = _grade_and_feedback(rounded_percentage)
        word_speed = _speed_from_times([response.elapsed for response in ordered_responses if response.category == "word"])
        sentence_speed = _speed_from_times([response.elapsed for response in ordered_responses if response.category == "sentence"])
        return TestSummary(
            responses=ordered_responses,
            total_points=total_points,
            max_points=self._total_questions,
            grade_text=grade_text,
            feedback=feedback,
            word_speed=word_speed,
            sentence_speed=sentence_speed,
        )


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
            f"F (mitterahuldav) / {percentage}%",
            "Punktisumma pole just kõige parem, aga arenguruumi on kõigil piisavalt.",
        )
    if percentage <= 60:
        return (
            f"E (kasin) / {percentage}%",
            "Punktisumma pole just kõige parem, aga arenguruumi on kõigil piisavalt.",
        )
    if percentage <= 70:
        return (
            f"D (rahuldav) / {percentage}%",
            "Hakkab juba vaikselt tulema.\nHarjuta veel mõned korrad ning kindlasti saad veelgi parema tulemuse.",
        )
    if percentage <= 80:
        return (
            f"C (hea) / {percentage}%",
            "Hakkab juba vaikselt tulema.\nHarjuta veel mõned korrad ning kindlasti saad veelgi parema tulemuse.",
        )
    if percentage <= 90:
        return (
            f"B (väga hea) / {percentage}%",
            "Päris hea. Tundub, et hakkad palju paremaks muutuma.",
        )
    return (
        f"A (suurepärane) / {percentage}%",
        "Väga super.\nOled testi sooritanud headele punktidele ning võid ennast nimetada morsekoodi meistriks.",
    )
