from __future__ import annotations

from dataclasses import dataclass
from ..model.test_session import TestResponse, TestSession, TestSummary


@dataclass(frozen=True)
class TestQuestionState:
    """Information required to render a single test question."""

    prompt: str
    answered: int
    total: int
    progress_value: float
    progress_step: float
    progress_text: str
    question_number: int
    existing_answer: str
    has_previous: bool
    has_next: bool


class TestPresenter:
    """Coordinates test-session behaviour for the UI layer."""

    def __init__(self, session: TestSession) -> None:
        self._session = session
        self._summary: TestSummary | None = None

    def reset(self) -> None:
        """Reset the underlying session and cached summary."""

        self._session.reset()
        self._summary = None

    def total_questions(self) -> int:
        return self._session.total_questions

    def answered_count(self) -> int:
        return self._session.answered_count

    def has_active_prompt(self) -> bool:
        return self._session.current_prompt() is not None

    def current_state(self) -> TestQuestionState:
        prompt = self._ensure_active_prompt()
        return self._build_state(prompt)

    def record_answer(self, answer: str, elapsed: float) -> None:
        if self._session.current_prompt() is None:
            raise RuntimeError("Cannot record answer without an active prompt")

        self._session.record_response(answer, elapsed)
        self._summary = None

    def move_next(self) -> TestQuestionState:
        prompt = self._session.next_question()
        return self._build_state(prompt)

    def move_previous(self) -> TestQuestionState:
        prompt = self._session.previous_question()
        return self._build_state(prompt)

    def can_move_next(self) -> bool:
        return self._session.has_next_question()

    def can_move_previous(self) -> bool:
        return self._session.has_previous_question()

    def all_answered(self) -> bool:
        return self._session.all_answered()

    def summary(self) -> TestSummary:
        if self._summary is None:
            self._summary = self._session.summary()
        return self._summary

    def responses(self) -> list[TestResponse]:
        return self.summary().responses

    def _ensure_active_prompt(self) -> str:
        prompt = self._session.current_prompt()
        if prompt is None:
            raise RuntimeError("No active prompt available")
        return prompt

    def _build_state(self, prompt: str) -> TestQuestionState:
        total = self._session.total_questions
        answered = self._session.answered_count
        progress_value = (answered / total) * 100 if total else 0.0
        progress_step = 100.0 / total if total else 100.0
        position = self._session.current_position()
        question_number = position + 1 if position >= 0 else 0
        return TestQuestionState(
            prompt=prompt,
            answered=answered,
            total=total,
            progress_value=progress_value,
            progress_step=progress_step,
            progress_text=f"{progress_value:.1f}% läbitud",
            question_number=question_number,
            existing_answer=self._session.current_answer(),
            has_previous=self._session.has_previous_question(),
            has_next=self._session.has_next_question(),
        )
