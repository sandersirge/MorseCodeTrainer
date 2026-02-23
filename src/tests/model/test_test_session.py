"""Tests for TestSession model."""
import pytest
from src.main.python.model.test_session import TestSession, TestResponse, TestSummary, _grade_and_feedback, _speed_from_times


class TestTestSessionInit:
    """Tests for TestSession initialization."""

    def test_init_with_matching_lengths(self):
        session = TestSession(prompts=["A", "B"], answers=[".-", "-..."])
        assert session.total_questions == 2

    def test_init_mismatched_lengths_raises(self):
        with pytest.raises(ValueError, match="equal numbers"):
            TestSession(prompts=["A"], answers=[".-", "-..."])

    def test_init_empty(self):
        session = TestSession(prompts=[], answers=[])
        assert session.total_questions == 0


class TestTestSessionNavigation:
    """Tests for TestSession navigation."""

    def test_current_prompt_at_start(self, test_session):
        # After init, we're at position 0
        prompt = test_session.current_prompt()
        assert prompt is not None

    def test_has_next_question_true(self, test_session):
        assert test_session.has_next_question()

    def test_has_previous_question_false_at_start(self, test_session):
        assert not test_session.has_previous_question()

    def test_next_question_advances(self, test_session):
        first_prompt = test_session.current_prompt()
        test_session.next_question()
        second_prompt = test_session.current_prompt()
        # Due to shuffle, we just verify navigation happened
        assert test_session.current_position() == 1

    def test_next_question_at_end_raises(self, test_session):
        # Navigate to end
        while test_session.has_next_question():
            test_session.next_question()
        with pytest.raises(StopIteration, match="No questions left"):
            test_session.next_question()

    def test_previous_question_at_start_raises(self, test_session):
        with pytest.raises(StopIteration, match="first question"):
            test_session.previous_question()

    def test_previous_question_works_after_next(self, test_session):
        test_session.next_question()
        test_session.previous_question()
        assert test_session.current_position() == 0

    def test_current_position_starts_at_zero(self, test_session):
        assert test_session.current_position() == 0

    def test_current_index_returns_shuffled_index(self, test_session):
        index = test_session.current_index()
        assert index is not None
        assert 0 <= index < test_session.total_questions


class TestTestSessionEmpty:
    """Tests for empty TestSession behavior."""

    def test_current_prompt_empty_is_none(self):
        session = TestSession(prompts=[], answers=[])
        assert session.current_prompt() is None

    def test_current_index_empty_is_none(self):
        session = TestSession(prompts=[], answers=[])
        assert session.current_index() is None

    def test_has_next_question_empty_is_false(self):
        session = TestSession(prompts=[], answers=[])
        assert not session.has_next_question()


class TestTestSessionRecordResponse:
    """Tests for recording responses."""

    def test_record_response_returns_test_response(self, test_session):
        response = test_session.record_response(".- -...", 5.0)
        assert isinstance(response, TestResponse)
        assert response.elapsed == 5.0

    def test_record_response_stores_answer(self, test_session):
        test_session.record_response("my answer", 3.0)
        assert test_session.current_answer() == "my answer"

    def test_record_response_increments_count(self, test_session):
        assert test_session.answered_count == 0
        test_session.record_response("answer", 1.0)
        assert test_session.answered_count == 1

    def test_record_response_without_active_raises(self):
        session = TestSession(prompts=[], answers=[])
        with pytest.raises(RuntimeError, match="active question"):
            session.record_response("answer", 1.0)

    def test_current_answer_empty_when_not_answered(self, test_session):
        assert test_session.current_answer() == ""

    def test_responses_list(self, test_session):
        test_session.record_response("ans1", 1.0)
        test_session.next_question()
        test_session.record_response("ans2", 2.0)
        responses = test_session.responses()
        assert len(responses) == 2


class TestTestSessionScoring:
    """Tests for scoring logic."""

    def test_perfect_match_scores_full(self):
        session = TestSession(prompts=["A"], answers=[".-"])
        session.record_response(".-", 1.0)
        response = session.responses()[0]
        assert response.score == 1.0

    def test_partial_match_scores_half(self):
        # For word prompts (index < 10), scoring is by space-separated tokens
        session = TestSession(prompts=["AB"], answers=[".- -..."])
        session.record_response(".- .---", 1.0)  # First token correct, second wrong
        response = session.responses()[0]
        assert response.score == 0.5

    def test_wrong_answer_scores_zero(self):
        session = TestSession(prompts=["A"], answers=[".-"])
        session.record_response("-...", 1.0)
        response = session.responses()[0]
        assert response.score == 0.0

    def test_empty_answer_scores_zero(self):
        session = TestSession(prompts=["A"], answers=[".-"])
        session.record_response("", 1.0)
        response = session.responses()[0]
        assert response.score == 0.0


class TestTestSessionAllAnswered:
    """Tests for all_answered state."""

    def test_all_answered_false_initially(self, test_session):
        assert not test_session.all_answered()

    def test_all_answered_true_after_all_recorded(self, test_session):
        # Record all answers
        test_session.record_response("ans", 1.0)
        while test_session.has_next_question():
            test_session.next_question()
            test_session.record_response("ans", 1.0)
        assert test_session.all_answered()


class TestTestSessionSummary:
    """Tests for TestSummary generation."""

    def test_summary_returns_test_summary(self, test_session):
        test_session.record_response("ans", 1.0)
        summary = test_session.summary()
        assert isinstance(summary, TestSummary)

    def test_summary_includes_all_questions(self, test_session):
        summary = test_session.summary()
        assert len(summary.responses) == test_session.total_questions

    def test_summary_unanswered_get_zero_score(self, test_session):
        # Don't answer anything
        summary = test_session.summary()
        assert summary.total_points == 0.0

    def test_summary_max_points_equals_total(self, test_session):
        summary = test_session.summary()
        assert summary.max_points == test_session.total_questions


class TestTestSessionReset:
    """Tests for session reset."""

    def test_reset_clears_responses(self, test_session):
        test_session.record_response("ans", 1.0)
        test_session.reset()
        assert test_session.answered_count == 0

    def test_reset_reshuffles(self, test_session, monkeypatch):
        shuffle_calls = []
        def mock_shuffle(x):
            shuffle_calls.append(len(x))
        monkeypatch.setattr("random.shuffle", mock_shuffle)
        test_session.reset()
        assert len(shuffle_calls) == 1


class TestTestSummaryProperties:
    """Tests for TestSummary dataclass properties."""

    def test_score_text_format(self):
        summary = TestSummary(
            responses=[],
            total_points=5.0,
            max_points=10,
            grade_text="C",
            feedback="Good",
            word_speed=30,
            sentence_speed=20
        )
        assert summary.score_text == "Vastasid 5.0 / 10 õigesti"

    def test_answered_non_empty_counts_correctly(self):
        responses = [
            TestResponse(0, "A", ".-", ".-", 1.0, 1.0, "word"),
            TestResponse(1, "B", "-...", "", 1.0, 0.0, "word"),
            TestResponse(2, "C", "-.-.", "-.-.", 1.0, 1.0, "word"),
        ]
        summary = TestSummary(
            responses=responses,
            total_points=2.0,
            max_points=3,
            grade_text="C",
            feedback="Good",
            word_speed=30,
            sentence_speed=20
        )
        assert summary.answered_non_empty == 2


class TestGradeAndFeedback:
    """Tests for _grade_and_feedback function."""

    def test_grade_f_at_50_percent(self):
        grade, _ = _grade_and_feedback(50.0)
        assert "F" in grade

    def test_grade_e_at_60_percent(self):
        grade, _ = _grade_and_feedback(60.0)
        assert "E" in grade

    def test_grade_d_at_70_percent(self):
        grade, _ = _grade_and_feedback(70.0)
        assert "D" in grade

    def test_grade_c_at_80_percent(self):
        grade, _ = _grade_and_feedback(80.0)
        assert "C" in grade

    def test_grade_b_at_90_percent(self):
        grade, _ = _grade_and_feedback(90.0)
        assert "B" in grade

    def test_grade_a_at_100_percent(self):
        grade, _ = _grade_and_feedback(100.0)
        assert "A" in grade


class TestSpeedFromTimes:
    """Tests for _speed_from_times function."""

    def test_empty_entries_returns_zero(self):
        assert _speed_from_times([]) == 0

    def test_calculates_items_per_minute(self):
        # 2 items in 1 second each = 2 items in 2 seconds = 60 items/minute
        result = _speed_from_times([1.0, 1.0])
        assert result == 60

    def test_zero_time_returns_zero(self):
        assert _speed_from_times([0.0, 0.0]) == 0
