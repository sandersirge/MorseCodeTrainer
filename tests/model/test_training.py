"""Tests for Koch lessons, weighted ordering, copy scoring and word drills."""

import random

import pytest

from morsetrainer.model.keyer import KeyerDecoder
from morsetrainer.model.training import (
	KOCH_ORDER,
	koch_characters,
	koch_groups,
	score_copy,
	weighted_order,
	word_drill,
)
from morsetrainer.resources.word_list import WORDS_ET
from morsetrainer.utils.morse_translator import convert_text_to_morse


class TestKoch:
	def test_order_starts_with_k_m_and_has_no_duplicates(self):
		assert KOCH_ORDER[:2] == ("K", "M")
		assert len(set(KOCH_ORDER)) == len(KOCH_ORDER)

	def test_every_koch_character_can_be_sent(self):
		for char in KOCH_ORDER:
			assert convert_text_to_morse(char)

	def test_levels(self):
		assert koch_characters(0) == ["K", "M"]
		assert koch_characters(3) == ["K", "M", "U"]
		assert koch_characters(999) == list(KOCH_ORDER)

	def test_groups_use_only_unlocked_characters(self):
		text = koch_groups(["K", "M", "U"], random.Random(1), groups=4, group_size=5, focus="U")
		groups = text.split(" ")
		assert len(groups) == 4 and all(len(g) == 5 for g in groups)
		assert set(text.replace(" ", "")) <= {"K", "M", "U"}

	def test_focus_character_appears_more_often(self):
		text = koch_groups(list("KMURESNAPT"), random.Random(2), groups=40, focus="T")
		share = text.count("T") / len(text.replace(" ", ""))
		assert share > 0.3


class TestWeightedOrder:
	def test_keeps_every_item_once(self):
		items = list("ABCDEFG")
		assert sorted(weighted_order(items, lambda _: 1.0, random.Random(0))) == items

	def test_heavy_items_tend_to_come_first(self):
		rng = random.Random(3)
		firsts = [
			weighted_order(list("ABCDE"), lambda c: 20.0 if c == "E" else 1.0, rng)[0]
			for _ in range(200)
		]
		assert firsts.count("E") > 100


class TestScoreCopy:
	def test_perfect(self):
		result = score_copy("KMU MK", "kmumk")
		assert result.accuracy == 1.0
		assert result.per_char == {"K": (2, 0), "M": (2, 0), "U": (1, 0)}

	def test_missing_character_costs_only_itself(self):
		result = score_copy("KMUKM", "KMKM")
		assert result.correct == 4
		assert result.per_char["U"] == (0, 1)

	def test_extra_characters_lower_accuracy(self):
		assert score_copy("KM", "KMMMM").accuracy < 1.0

	def test_empty(self):
		assert score_copy("", "").accuracy == 0.0


class TestWordDrill:
	def test_all_words_can_be_sent(self):
		for word in WORDS_ET:
			assert convert_text_to_morse(word), word

	def test_drill_shape(self):
		phrases = word_drill(WORDS_ET, lambda _: 0.5, random.Random(4), count=12, max_words=3)
		assert len(phrases) == 12
		assert all(1 <= len(p.split()) <= 3 for p in phrases)

	def test_weak_letters_are_favoured(self):
		words = ["žürii", "maja", "kodu", "tee", "linn"]
		weak_z = lambda c: 1.0 if c == "Ž" else 0.0  # noqa: E731
		phrases = word_drill(words, weak_z, random.Random(5), count=200, max_words=1)
		assert phrases.count("žürii") > 200 / len(words) * 2


def _send(decoder: KeyerDecoder, morse: str, unit: float = 0.06) -> float:
	"""Simulate perfect keying of *morse*; returns the end time."""
	now = 0.0
	for word_index, word in enumerate(morse.split("   ")):
		if word_index:
			now += 4 * unit  # +3 already added after the last letter = 7 units
		for letter in word.split(" "):
			for symbol in letter:
				decoder.key_down(now)
				now += unit if symbol == "." else 3 * unit
				decoder.key_up(now)
				now += unit
			now += 2 * unit  # letter gap = 3 units in total
	return now


class TestKeyerDecoder:
	def test_decodes_perfect_timing(self):
		decoder = KeyerDecoder(unit=0.06)
		end = _send(decoder, "... ---   ...")
		decoder.tick(end + 1)
		assert decoder.text == "SO S"
		assert decoder.morse == "... ---   ..."

	def test_tolerates_uneven_keying(self):
		decoder = KeyerDecoder(unit=0.1)
		# dot 0.14 s (1.4 units), dash 0.25 s (2.5 units), short letter gap
		for down, up in [(0.0, 0.14), (0.25, 0.5)]:
			decoder.key_down(down)
			decoder.key_up(up)
		decoder.tick(2.0)
		assert decoder.text == "A"

	def test_auto_repeat_key_down_is_ignored(self):
		decoder = KeyerDecoder(unit=0.06)
		decoder.key_down(0.0)
		decoder.key_down(0.03)  # OS key repeat while held
		decoder.key_up(0.06)
		decoder.tick(1.0)
		assert decoder.text == "E"

	def test_unknown_code_shows_question_mark(self):
		decoder = KeyerDecoder(unit=0.06)
		end = _send(decoder, "........")
		decoder.tick(end + 1)
		assert decoder.text == "?"

	def test_partial_letter_visible_in_morse(self):
		decoder = KeyerDecoder(unit=0.06)
		decoder.key_down(0.0)
		decoder.key_up(0.06)
		assert decoder.morse == "."
		assert decoder.text == ""

	def test_estimated_wpm(self):
		decoder = KeyerDecoder(unit=0.06)
		end = _send(decoder, "... ...")
		decoder.tick(end + 1)
		assert decoder.estimated_wpm == 20

	@pytest.mark.parametrize("wpm", [10, 25])
	def test_other_speeds(self, wpm):
		unit = 1.2 / wpm
		decoder = KeyerDecoder(unit=unit)
		end = _send(decoder, "-- --- .-. ... .", unit)
		decoder.tick(end + 1)
		assert decoder.text == "MORSE"

	def test_clear(self):
		decoder = KeyerDecoder(unit=0.06)
		_send(decoder, "...")
		decoder.clear()
		assert decoder.morse == "" and decoder.text == ""
