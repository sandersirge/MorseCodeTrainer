"""Tests for constants module integrity."""

from morsetrainer.resources import constants as consts
from morsetrainer.utils.morse_translator import convert_text_to_morse


class TestLetterMorsePairs:
	"""Tests for LETTER_MORSE_PAIRS structure."""

	def test_is_tuple(self):
		assert isinstance(consts.LETTER_MORSE_PAIRS, tuple)

	def test_pairs_are_tuples(self):
		for pair in consts.LETTER_MORSE_PAIRS:
			assert isinstance(pair, tuple)
			assert len(pair) == 2

	def test_morse_contains_only_dots_and_dashes(self):
		for _, code in consts.LETTER_MORSE_PAIRS:
			assert all(c in ".-" for c in code), f"Invalid morse: {code}"

	def test_includes_estonian_characters(self):
		letters = {letter for letter, _ in consts.LETTER_MORSE_PAIRS}
		assert "ä" in letters
		assert "ö" in letters
		assert "ü" in letters
		assert "š" in letters


class TestLetterToMorseMap:
	"""Tests for LETTER_TO_MORSE_MAP structure."""

	def test_contains_both_cases(self):
		assert "a" in consts.LETTER_TO_MORSE_MAP
		assert "A" in consts.LETTER_TO_MORSE_MAP

	def test_cases_map_to_same_code(self):
		assert consts.LETTER_TO_MORSE_MAP["a"] == consts.LETTER_TO_MORSE_MAP["A"]

	def test_all_letters_mapped(self):
		for letter, code in consts.LETTER_MORSE_PAIRS:
			assert consts.LETTER_TO_MORSE_MAP[letter] == code
			assert consts.LETTER_TO_MORSE_MAP[letter.upper()] == code


class TestNumberSymbolMorsePairs:
	"""Tests for NUMBER_SYMBOL_MORSE_PAIRS structure."""

	def test_is_tuple(self):
		assert isinstance(consts.NUMBER_SYMBOL_MORSE_PAIRS, tuple)

	def test_morse_contains_only_dots_and_dashes(self):
		for _, code in consts.NUMBER_SYMBOL_MORSE_PAIRS:
			assert all(c in ".-" for c in code), f"Invalid morse: {code}"


class TestNumberToMorseMap:
	"""Tests for NUMBER_TO_MORSE_MAP structure."""

	def test_contains_all_digits(self):
		for digit in "0123456789":
			assert digit in consts.NUMBER_TO_MORSE_MAP

	def test_all_values_are_morse(self):
		for code in consts.NUMBER_TO_MORSE_MAP.values():
			assert all(c in ".-" for c in code)


class TestSymbolToMorseMap:
	"""Tests for SYMBOL_TO_MORSE_MAP structure."""

	def test_contains_common_symbols(self):
		assert "." in consts.SYMBOL_TO_MORSE_MAP
		assert "," in consts.SYMBOL_TO_MORSE_MAP
		assert "?" in consts.SYMBOL_TO_MORSE_MAP
		assert "!" in consts.SYMBOL_TO_MORSE_MAP

	def test_all_values_are_morse(self):
		for code in consts.SYMBOL_TO_MORSE_MAP.values():
			assert all(c in ".-" for c in code)


class TestTranslationSentences:
	"""Tests for translation exercise data."""

	def test_has_20_sentences(self):
		assert len(consts.TRANSLATION_SENTENCES) == 20

	def test_every_sentence_is_translatable(self):
		# Every character must exist in the Morse tables (catches typos and
		# characters the trainer can't send).
		for sentence in consts.TRANSLATION_SENTENCES:
			convert_text_to_morse(sentence)


class TestTestItems:
	"""Tests for test question data."""

	def test_has_20_items(self):
		assert len(consts.TEST_ITEMS) == 20

	def test_items_have_valid_direction_and_category(self):
		for item in consts.TEST_ITEMS:
			assert item.direction in ("text_to_morse", "morse_to_text")
			assert item.category in ("word", "sentence")

	def test_both_directions_and_categories_present(self):
		combos = {(item.direction, item.category) for item in consts.TEST_ITEMS}
		assert len(combos) == 4

	def test_every_item_is_translatable(self):
		for item in consts.TEST_ITEMS:
			convert_text_to_morse(item.text)


class TestKeyViews:
	"""Tests for pre-computed key views."""

	def test_uppercase_letter_keys_are_uppercase(self):
		for key in consts.UPPERCASE_LETTER_KEYS:
			assert key == key.upper()

	def test_lowercase_letter_keys_are_lowercase(self):
		for key in consts.LOWERCASE_LETTER_KEYS:
			assert key == key.lower()

	def test_number_keys_are_digits(self):
		for key in consts.NUMBER_KEYS:
			assert key.isdigit()

	def test_symbol_keys_are_not_digits(self):
		for key in consts.SYMBOL_KEYS:
			assert not key.isdigit()
