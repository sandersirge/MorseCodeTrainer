"""Tests for morse_translator utility functions."""
import pytest
from src.main.python.utils.morse_translator import convert_text_to_morse, convert_morse_to_text


class TestConvertTextToMorse:
    """Tests for convert_text_to_morse function."""

    def test_empty_string_returns_empty(self):
        assert convert_text_to_morse("") == ""

    def test_single_letter(self):
        assert convert_text_to_morse("A") == ".-"

    def test_single_letter_lowercase(self):
        assert convert_text_to_morse("a") == ".-"

    def test_word_with_spaces_between_letters(self):
        # Each letter separated by single space
        result = convert_text_to_morse("AB")
        assert result == ".- -..."

    def test_multiple_words_separated_by_triple_space(self):
        result = convert_text_to_morse("HI MOM")
        # H=.... I=.. M=-- O=--- M=--
        assert result == ".... ..   -- --- --"

    def test_number(self):
        assert convert_text_to_morse("1") == ".----"

    def test_all_digits(self):
        result = convert_text_to_morse("12345")
        expected = ".---- ..--- ...-- ....- ....."
        assert result == expected

    def test_symbol_period(self):
        assert convert_text_to_morse(".") == ".-.-.-"

    def test_symbol_question_mark(self):
        assert convert_text_to_morse("?") == "..--.."

    def test_mixed_letters_and_numbers(self):
        result = convert_text_to_morse("A1")
        assert result == ".- .----"

    # Estonian characters
    def test_estonian_character_a_umlaut(self):
        # ä = .-.-
        assert convert_text_to_morse("ä") == ".-.-"
        assert convert_text_to_morse("Ä") == ".-.-"

    def test_estonian_character_o_umlaut(self):
        # ö = ---.
        assert convert_text_to_morse("ö") == "---."
        assert convert_text_to_morse("Ö") == "---."

    def test_estonian_character_u_umlaut(self):
        # ü = ..--
        assert convert_text_to_morse("ü") == "..--"
        assert convert_text_to_morse("Ü") == "..--"

    def test_estonian_character_s_caron(self):
        # š = ----
        assert convert_text_to_morse("š") == "----"
        assert convert_text_to_morse("Š") == "----"

    def test_unsupported_character_raises(self):
        with pytest.raises(ValueError, match="Unsupported character"):
            convert_text_to_morse("©")

    def test_consecutive_spaces_in_input(self):
        # Multiple spaces become multiple word separators
        result = convert_text_to_morse("A  B")
        # Two spaces means empty word in between
        assert "   " in result


class TestConvertMorseToText:
    """Tests for convert_morse_to_text function."""

    def test_empty_string_returns_empty(self):
        assert convert_morse_to_text("") == ""

    def test_single_letter(self):
        result = convert_morse_to_text(".-")
        assert result == "A"

    def test_word_capitalization(self):
        # First letter of each word is uppercase, rest lowercase
        result = convert_morse_to_text(".... ..")
        assert result == "Hi"

    def test_multiple_words(self):
        # Triple space separates words
        result = convert_morse_to_text(".... ..   -- --- --")
        # "HI MOM" but with capitalization: "Hi Mom"
        assert result == "Hi Mom"

    def test_number(self):
        assert convert_morse_to_text(".----") == "1"

    def test_all_digits(self):
        result = convert_morse_to_text(".---- ..--- ...-- ....- .....")
        assert result == "12345"

    def test_symbol(self):
        result = convert_morse_to_text(".-.-.-")
        assert result == "."

    # Estonian characters
    def test_estonian_a_umlaut_at_start(self):
        result = convert_morse_to_text(".-.-")
        assert result == "Ä"

    def test_estonian_a_umlaut_after_letter(self):
        result = convert_morse_to_text(".- .-.-")
        # Second character is lowercase
        assert result == "Aä"

    def test_estonian_o_umlaut(self):
        result = convert_morse_to_text("---.")
        assert result == "Ö"

    def test_estonian_u_umlaut(self):
        result = convert_morse_to_text("..--")
        assert result == "Ü"

    def test_estonian_s_caron(self):
        result = convert_morse_to_text("----")
        assert result == "Š"

    def test_unsupported_morse_raises(self):
        with pytest.raises(ValueError, match="Unsupported Morse symbol"):
            convert_morse_to_text(".-.-.-.-.-.")

    def test_single_space_separates_letters(self):
        result = convert_morse_to_text(".- -...")
        assert result == "Ab"

    def test_triple_space_separates_words(self):
        result = convert_morse_to_text(".-   -...")
        assert result == "A B"


class TestRoundTrip:
    """Tests for text→morse→text round-trip consistency."""

    def test_roundtrip_single_word(self):
        original = "HELLO"
        morse = convert_text_to_morse(original)
        back = convert_morse_to_text(morse)
        # Capitalization: "Hello" (first upper, rest lower)
        assert back == "Hello"

    def test_roundtrip_multiple_words(self):
        original = "HELLO WORLD"
        morse = convert_text_to_morse(original)
        back = convert_morse_to_text(morse)
        assert back == "Hello World"

    def test_roundtrip_with_numbers(self):
        original = "ABC123"
        morse = convert_text_to_morse(original)
        back = convert_morse_to_text(morse)
        # Numbers don't have case
        assert back == "Abc123"

    def test_roundtrip_estonian_word(self):
        original = "TÄNAV"  # street in Estonian
        morse = convert_text_to_morse(original)
        back = convert_morse_to_text(morse)
        assert back == "Tänav"
