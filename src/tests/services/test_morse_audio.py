"""Tests for morse_audio service."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.main.python.services.morse_audio import synthesize_morse_audio, _parse_morse_sequence


class TestParseMorseSequence:
    """Tests for _parse_morse_sequence function."""

    def test_empty_string_returns_empty(self):
        result = list(_parse_morse_sequence(""))
        assert result == []

    def test_whitespace_only_returns_empty(self):
        result = list(_parse_morse_sequence("   "))
        assert result == []

    def test_single_dot_returns_tone_1_unit(self):
        result = list(_parse_morse_sequence("."))
        assert result == [("tone", 1)]

    def test_single_dash_returns_tone_3_units(self):
        result = list(_parse_morse_sequence("-"))
        assert result == [("tone", 3)]

    def test_letter_a_returns_dot_gap_dash(self):
        result = list(_parse_morse_sequence(".-"))
        expected = [
            ("tone", 1),  # dot
            ("gap", 1),   # gap between symbols
            ("tone", 3),  # dash
        ]
        assert result == expected

    def test_two_letters_have_letter_gap(self):
        # A B = .- -...
        result = list(_parse_morse_sequence(".- -..."))
        # Should have a gap of 3 units between letters
        assert ("gap", 3) in result

    def test_two_words_have_word_gap(self):
        # "A A" with triple space word separator
        result = list(_parse_morse_sequence(".-   .-"))
        # Should have a gap of 7 units between words
        assert ("gap", 7) in result

    def test_invalid_symbol_raises(self):
        with pytest.raises(ValueError, match="Unsupported symbol"):
            list(_parse_morse_sequence(".-x"))


class TestSynthesizeMorseAudio:
    """Tests for synthesize_morse_audio function."""

    def test_empty_morse_raises(self):
        with pytest.raises(ValueError, match="No Morse content"):
            synthesize_morse_audio("")

    def test_whitespace_morse_raises(self):
        with pytest.raises(ValueError, match="No Morse content"):
            synthesize_morse_audio("   ")

    def test_returns_path(self):
        result = synthesize_morse_audio(".-")
        assert isinstance(result, Path)
        # Cleanup
        if result.exists():
            result.unlink()

    def test_creates_wav_file(self):
        result = synthesize_morse_audio(".-")
        assert result.exists()
        assert result.suffix == ".wav"
        # Cleanup
        result.unlink()

    def test_wav_file_is_valid(self):
        import wave
        result = synthesize_morse_audio(".-")
        with wave.open(str(result), "rb") as wav:
            assert wav.getnchannels() == 1
            assert wav.getsampwidth() == 2
            assert wav.getframerate() == 44100
        # Cleanup
        result.unlink()

    def test_custom_sample_rate(self):
        import wave
        result = synthesize_morse_audio(".-", sample_rate=22050)
        with wave.open(str(result), "rb") as wav:
            assert wav.getframerate() == 22050
        # Cleanup
        result.unlink()

    def test_volume_clamps_to_max(self):
        # Should not raise, just clamp
        result = synthesize_morse_audio(".-", volume=1.5)
        assert result.exists()
        result.unlink()

    def test_volume_clamps_to_min(self):
        # Should not raise, just clamp
        result = synthesize_morse_audio(".-", volume=-0.5)
        assert result.exists()
        result.unlink()

    def test_file_in_temp_directory(self):
        import tempfile
        result = synthesize_morse_audio(".-")
        assert str(result).startswith(tempfile.gettempdir())
        result.unlink()

    def test_file_has_unique_name(self):
        result1 = synthesize_morse_audio(".-")
        result2 = synthesize_morse_audio(".-")
        assert result1 != result2
        result1.unlink()
        result2.unlink()


class TestSynthesizeMorseAudioTiming:
    """Tests for timing calculations in audio synthesis."""

    def test_longer_duration_creates_larger_file(self):
        # Longer unit duration should create more samples
        short = synthesize_morse_audio(".-", unit_duration_ms=50)
        long = synthesize_morse_audio(".-", unit_duration_ms=150)
        
        short_size = short.stat().st_size
        long_size = long.stat().st_size
        
        assert long_size > short_size
        
        short.unlink()
        long.unlink()

    def test_complex_morse_code(self):
        # SOS = ... --- ...
        result = synthesize_morse_audio("... --- ...")
        assert result.exists()
        result.unlink()

    def test_word_separation(self):
        # HELLO WORLD with word gap
        result = synthesize_morse_audio(".... . .-.. .-.. ---   .-- --- .-. .-.. -..")
        assert result.exists()
        result.unlink()
