"""Turns Morse code into audio samples and WAV data (no temporary files)."""

from __future__ import annotations

import io
import math
import wave
from array import array
from pathlib import Path

from ..exceptions import NoAudioContentError, UnsupportedMorseSymbolError
from ..utils.morse_translator import split_morse_words
from .audio_settings import AudioSettings

DEFAULT_SAMPLE_RATE = 44100
# Fade each tone in and out so it doesn't start/stop with an audible click.
_RAMP_MS = 5.0

Event = tuple[bool, float]  # (is_tone, duration in seconds)


def timing_seconds(settings: AudioSettings) -> tuple[float, float, float]:
	"""Return (unit, gap between letters, gap between words) in seconds.

	Uses ARRL Farnsworth timing when the effective speed is below the
	character speed; otherwise the standard 1 / 3 / 7 unit spacing.
	"""

	unit = settings.unit_ms / 1000.0
	char_wpm = settings.wpm
	eff_wpm = settings.effective_wpm
	if eff_wpm >= char_wpm:
		return unit, 3 * unit, 7 * unit
	total_delay = (60 * char_wpm - 37.2 * eff_wpm) / (char_wpm * eff_wpm)
	return unit, 3 * total_delay / 19, 7 * total_delay / 19


def morse_events(morse_code: str, settings: AudioSettings) -> list[Event]:
	"""Describe *morse_code* as a list of tones and silences."""

	unit, letter_gap, word_gap = timing_seconds(settings)
	events: list[Event] = []
	words = split_morse_words(morse_code)
	for word_index, letters in enumerate(words):
		if word_index:
			events.append((False, word_gap))
		for letter_index, letter in enumerate(letters):
			if letter_index:
				events.append((False, letter_gap))
			for symbol_index, symbol in enumerate(letter):
				if symbol_index:
					events.append((False, unit))
				if symbol == ".":
					events.append((True, unit))
				elif symbol == "-":
					events.append((True, 3 * unit))
				else:
					raise UnsupportedMorseSymbolError(letter)
	if not events:
		raise NoAudioContentError()
	return events


def _tone(seconds: float, settings: AudioSettings, sample_rate: int) -> array:
	count = max(1, int(round(seconds * sample_rate)))
	amplitude = settings.volume * 32767
	step = 2 * math.pi * settings.frequency_hz / sample_rate
	ramp = min(int(sample_rate * _RAMP_MS / 1000), count // 4)
	samples = array("h", bytes(2 * count))
	for i in range(count):
		gain = 1.0
		if i < ramp:
			gain = 0.5 - 0.5 * math.cos(math.pi * i / ramp)
		elif i >= count - ramp:
			gain = 0.5 - 0.5 * math.cos(math.pi * (count - 1 - i) / ramp)
		samples[i] = int(amplitude * gain * math.sin(step * i))
	return samples


def render_samples(
	morse_code: str, settings: AudioSettings, sample_rate: int = DEFAULT_SAMPLE_RATE
) -> array:
	"""Render 16-bit mono samples. Each distinct tone length is computed once."""

	tones: dict[float, array] = {}
	output = array("h")
	for is_tone, seconds in morse_events(morse_code, settings):
		if is_tone:
			if seconds not in tones:
				tones[seconds] = _tone(seconds, settings, sample_rate)
			output.extend(tones[seconds])
		else:
			output.extend(array("h", bytes(2 * int(round(seconds * sample_rate)))))
	return output


def render_wav_bytes(
	morse_code: str, settings: AudioSettings, sample_rate: int = DEFAULT_SAMPLE_RATE
) -> bytes:
	"""Render a complete WAV file in memory."""

	buffer = io.BytesIO()
	with wave.open(buffer, "wb") as wav_file:
		wav_file.setnchannels(1)
		wav_file.setsampwidth(2)
		wav_file.setframerate(sample_rate)
		wav_file.writeframes(render_samples(morse_code, settings, sample_rate).tobytes())
	return buffer.getvalue()


def save_wav(path: Path, morse_code: str, settings: AudioSettings) -> Path:
	"""Write the Morse audio to *path* (adds ``.wav`` if missing)."""

	target = path if path.suffix.lower() == ".wav" else path.with_suffix(".wav")
	target.parent.mkdir(parents=True, exist_ok=True)
	target.write_bytes(render_wav_bytes(morse_code, settings))
	return target


__all__ = [
	"DEFAULT_SAMPLE_RATE",
	"morse_events",
	"render_samples",
	"render_wav_bytes",
	"save_wav",
	"timing_seconds",
]
