"""Tests for constants module integrity."""
import pytest
from src.main.python.resources import constants as consts


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


class TestAudioMaps:
    """Tests for audio mapping structures."""

    def test_letter_audio_map_paths_are_wav(self):
        for path in consts.LETTER_AUDIO_MAP.values():
            assert path.endswith(".wav")

    def test_number_audio_map_paths_are_wav(self):
        for path in consts.NUMBER_AUDIO_MAP.values():
            assert path.endswith(".wav")

    def test_symbol_audio_map_paths_are_wav(self):
        for path in consts.SYMBOL_AUDIO_MAP.values():
            assert path.endswith(".wav")

    def test_phrase_audio_map_has_words_and_sentences(self):
        # Should have sõna1-10 and lause1-10
        assert any("sõna" in key for key in consts.PHRASE_AUDIO_MAP)
        assert any("lause" in key for key in consts.PHRASE_AUDIO_MAP)


class TestTranslationSamples:
    """Tests for translation sample data."""

    def test_text_and_morse_samples_equal_length(self):
        assert len(consts.TRANSLATION_TEXT_SAMPLES) == len(consts.TRANSLATION_MORSE_SAMPLES)

    def test_has_20_samples(self):
        assert len(consts.TRANSLATION_TEXT_SAMPLES) == 20

    def test_morse_samples_valid(self):
        for morse in consts.TRANSLATION_MORSE_SAMPLES:
            # Morse can contain dots, dashes, spaces, and newlines
            for char in morse:
                assert char in ".- \n", f"Invalid char '{char}' in morse sample"


class TestTestData:
    """Tests for test prompts and answers."""

    def test_prompts_and_answers_equal_length(self):
        assert len(consts.TEST_TEXT_PROMPTS) == len(consts.TEST_MORSE_ANSWERS)

    def test_has_20_items(self):
        assert len(consts.TEST_TEXT_PROMPTS) == 20

    def test_prompts_are_strings(self):
        for prompt in consts.TEST_TEXT_PROMPTS:
            assert isinstance(prompt, str)

    def test_answers_are_strings(self):
        for answer in consts.TEST_MORSE_ANSWERS:
            assert isinstance(answer, str)


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
