"""Tests for Morse audio rendering (in memory, no temp files)."""

import io
import wave

import pytest

from src.main.python.exceptions import NoAudioContentError, UnsupportedMorseSymbolError
from src.main.python.services.audio_settings import AudioSettings
from src.main.python.services.morse_audio import (
	morse_events,
	render_samples,
	render_wav_bytes,
	save_wav,
	timing_seconds,
)

STANDARD = AudioSettings(wpm=20, effective_wpm=20)  # unit = 60 ms, no Farnsworth
UNIT = 0.06


class TestTiming:
	def test_standard_spacing_is_1_3_7(self):
		unit, letter_gap, word_gap = timing_seconds(STANDARD)
		assert unit == pytest.approx(UNIT)
		assert letter_gap == pytest.approx(3 * UNIT)
		assert word_gap == pytest.approx(7 * UNIT)

	def test_farnsworth_stretches_gaps_not_letters(self):
		unit, letter_gap, word_gap = timing_seconds(AudioSettings(wpm=20, effective_wpm=10))
		assert unit == pytest.approx(UNIT)
		assert letter_gap > 3 * UNIT
		assert word_gap > 7 * UNIT
		assert word_gap / letter_gap == pytest.approx(7 / 3)

	def test_farnsworth_hits_effective_speed(self):
		# "PARIS " is the standard word. With Farnsworth its total duration
		# (including the trailing word gap) must match the effective WPM.
		settings = AudioSettings(wpm=20, effective_wpm=10)
		events = morse_events(".--. .- .-. .. ...", settings)
		_, _, word_gap = timing_seconds(settings)
		total = sum(seconds for _, seconds in events) + word_gap
		assert total == pytest.approx(60 / 10, rel=0.01)


class TestEvents:
	def test_empty_raises(self):
		with pytest.raises(NoAudioContentError):
			morse_events("", STANDARD)

	def test_whitespace_only_raises(self):
		with pytest.raises(NoAudioContentError):
			morse_events("   \n ", STANDARD)

	def test_letter_a_is_dot_gap_dash(self):
		events = morse_events(".-", STANDARD)
		assert [kind for kind, _ in events] == [True, False, True]
		assert [seconds for _, seconds in events] == pytest.approx([UNIT, UNIT, 3 * UNIT])

	def test_two_letters_have_letter_gap(self):
		events = morse_events(". .", STANDARD)
		assert events[1][0] is False
		assert events[1][1] == pytest.approx(3 * UNIT)

	@pytest.mark.parametrize("separator", ["   ", "\n", " / "])
	def test_word_gap_from_spaces_newline_or_slash(self, separator):
		events = morse_events(f".{separator}.", STANDARD)
		assert events[1][1] == pytest.approx(7 * UNIT)

	def test_invalid_symbol_raises(self):
		with pytest.raises(UnsupportedMorseSymbolError):
			morse_events(".x-", STANDARD)


class TestSamples:
	def test_length_matches_timing(self):
		samples = render_samples(".-", STANDARD, sample_rate=8000)
		assert len(samples) == pytest.approx(5 * UNIT * 8000, abs=3)

	def test_tone_fades_in_and_out(self):
		# A hard start/stop is heard as a click; the first and last samples
		# of a tone must be (near) silent.
		samples = render_samples("-", STANDARD, sample_rate=44100)
		peak = max(abs(s) for s in samples)
		assert abs(samples[0]) < peak * 0.05
		assert abs(samples[-1]) < peak * 0.05

	def test_volume_scales_amplitude(self):
		quiet = max(render_samples("-", STANDARD.with_volume(0.2), 8000))
		loud = max(render_samples("-", STANDARD.with_volume(0.8), 8000))
		assert loud > 3 * quiet

	def test_zero_volume_is_silent(self):
		assert max(abs(s) for s in render_samples(".", STANDARD.with_volume(0.0), 8000)) == 0


class TestWav:
	def test_wav_bytes_are_valid(self):
		data = render_wav_bytes("... --- ...", STANDARD, sample_rate=22050)
		with wave.open(io.BytesIO(data)) as wav:
			assert wav.getnchannels() == 1
			assert wav.getsampwidth() == 2
			assert wav.getframerate() == 22050
			assert wav.getnframes() > 0

	def test_save_wav_adds_extension_and_creates_folder(self, tmp_path):
		target = save_wav(tmp_path / "sub" / "clip", ".-", STANDARD)
		assert target.suffix == ".wav"
		assert target.is_file()
		with wave.open(str(target)) as wav:
			assert wav.getnframes() > 0
