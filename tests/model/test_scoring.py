"""Regression tests for test-mode scoring."""

import pytest

from morsetrainer.model.test_session import TestSession, answer_units, score_answer
from morsetrainer.services.data_provider import create_test_session

LONG_TEXT = "PRAKTIKUMID TULEVAD SUUREKS KASUKS."
LONG_MORSE = (
	".--. .-. .- -.- - .. -.- ..- -- .. -..   - ..- .-.. . ...- .- -..   "
	"... ..- ..- .-. . -.- ...   -.- .- ... ..- -.- ... .-.-.-"
)


class TestScoreAnswer:
	def test_exact_answer_full_points(self):
		assert score_answer(LONG_TEXT, LONG_TEXT, morse=False) == 1.0

	def test_case_and_spacing_ignored_for_text(self):
		assert score_answer("Tartu linn", "  tartu   LINN ", morse=False) == 1.0

	def test_one_mistake_in_long_text_is_not_full_points(self):
		# Old bug: accuracy was rounded to 1 decimal before the threshold,
		# so 95%+ counted as 100%.
		given = LONG_TEXT[:-2] + "X."
		assert score_answer(LONG_TEXT, given, morse=False) == 0.5

	def test_one_mistake_in_long_morse_is_not_full_points(self):
		given = LONG_MORSE.replace(".-.-.-", "-.-.--")
		assert score_answer(LONG_MORSE, given, morse=True) == 0.5

	def test_one_missing_character_is_half_not_zero(self):
		# Old bug: position-by-position comparison shifted everything after a
		# missing character and scored 0.
		assert score_answer(LONG_TEXT, LONG_TEXT[1:], morse=False) == 0.5

	def test_one_missing_morse_letter_is_half_not_zero(self):
		assert score_answer(LONG_MORSE, LONG_MORSE.split(" ", 1)[1], morse=True) == 0.5

	def test_mostly_wrong_is_zero(self):
		assert score_answer(LONG_TEXT, "TERE", morse=False) == 0.0

	def test_empty_answer_is_zero(self):
		assert score_answer(LONG_TEXT, "", morse=False) == 0.0

	def test_morse_word_gap_style_does_not_matter(self):
		assert score_answer("... ---   ...", "... --- / ...", morse=True) == 1.0
		assert score_answer("... ---   ...", "... ---\n...", morse=True) == 1.0


class TestAnswerUnits:
	def test_morse_units_are_letters(self):
		assert answer_units(".- -...   -.-.", morse=True) == [".-", "-...", "-.-."]

	def test_text_units_are_characters(self):
		assert answer_units("ab  c", morse=False) == ["A", "B", " ", "C"]


class TestCategories:
	def test_explicit_categories_used(self):
		session = TestSession(["A", "B"], [".-", "-..."], categories=["sentence", "word"])
		session._order = [0, 1]
		assert [r.category for r in session.summary().responses] == ["sentence", "word"]

	def test_inferred_category_from_word_count(self):
		session = TestSession(["HI", "THIS IS LONG"], [".... ..", "x"])
		assert session._categories == ["word", "sentence"]

	def test_mismatched_categories_raise(self):
		from morsetrainer.exceptions import MismatchedDataError

		with pytest.raises(MismatchedDataError):
			TestSession(["A"], [".-"], categories=["word", "word"])


class TestRealTestData:
	def test_correct_answers_score_full_points(self):
		session = create_test_session()
		for index, expected in enumerate(session._answers):
			session._position = session._order.index(index)
			assert session.record_response(expected, 1.0).score == 1.0

	def test_ten_words_and_ten_sentences(self):
		session = create_test_session()
		assert session._categories.count("word") == 10
		assert session._categories.count("sentence") == 10
