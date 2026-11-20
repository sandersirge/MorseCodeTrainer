"""Input handling: Estonian letters, whitespace, word separators, display layout."""

import pytest

from src.main.python.exceptions import UnsupportedCharacterError
from src.main.python.utils.morse_translator import (
	convert_morse_to_text,
	convert_text_to_morse,
	format_morse_for_display,
	normalize_morse,
	split_morse_words,
)


class TestEstonianLetters:
	def test_o_tilde_is_sent_like_o_umlaut(self):
		assert convert_text_to_morse("õ") == convert_text_to_morse("ö") == "---."

	def test_app_title_translates(self):
		# The app's own title contains õ; this used to raise.
		assert convert_text_to_morse("Morsekoodi õppimisprogramm")

	def test_z_caron_round_trips(self):
		assert convert_text_to_morse("Žanr") == "--..- .- -. .-."
		assert convert_morse_to_text("--..- .- -. .-.") == "ŽANR"

	def test_unknown_character_still_raises(self):
		with pytest.raises(UnsupportedCharacterError):
			convert_text_to_morse("#")


class TestWhitespace:
	@pytest.mark.parametrize("text", ["HI MOM", "HI\tMOM", "HI\nMOM", "  HI   MOM  "])
	def test_any_whitespace_is_one_word_gap(self, text):
		assert convert_text_to_morse(text) == ".... ..   -- --- --"

	def test_empty_and_blank(self):
		assert convert_text_to_morse("") == ""
		assert convert_text_to_morse("   ") == ""


class TestMorseWordBreaks:
	@pytest.mark.parametrize(
		"morse",
		[".... ..   -- --- --", ".... .. / -- --- --", ".... ../-- --- --", ".... ..\n-- --- --"],
	)
	def test_word_break_styles(self, morse):
		assert convert_morse_to_text(morse) == "HI MOM"

	def test_split_words(self):
		assert split_morse_words(" .-  -... ") == [[".-"], ["-..."]]

	def test_normalize(self):
		assert normalize_morse(".-   / -...\n-.-.") == ".-   -...   -.-."


class TestDisplayFormat:
	def test_short_text_on_one_line(self):
		assert format_morse_for_display(".- -...   -.-.") == ".- -...   -.-."

	def test_long_text_breaks_only_between_words(self):
		morse = convert_text_to_morse("Kellegi arvutis jookseb 875 protsessi.")
		display = format_morse_for_display(morse, line_width=30)
		assert "\n" in display
		# Joining the lines back with word gaps gives the original exactly
		assert display.replace("\n", "   ") == morse
		assert convert_morse_to_text(display) == "KELLEGI ARVUTIS JOOKSEB 875 PROTSESSI."
