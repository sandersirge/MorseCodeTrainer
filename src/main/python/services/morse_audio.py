from __future__ import annotations

import math
import tempfile
import wave
from array import array
from pathlib import Path
from typing import Iterable, Tuple
from uuid import uuid4

_UNIT_GAP_AFTER_SYMBOL = 1
_GAP_BETWEEN_LETTERS = 3
_GAP_BETWEEN_WORDS = 7


def _parse_morse_sequence(morse_code: str) -> Iterable[Tuple[str, int]]:
    """Yield (type, units) pairs describing tones and silences."""

    stripped = morse_code.strip()
    if not stripped:
        return []

    events: list[Tuple[str, int]] = []
    words = [word for word in stripped.split("   ") if word != ""]
    for word_index, word in enumerate(words):
        letters = [letter for letter in word.split(" ") if letter != ""]
        for letter_index, letter in enumerate(letters):
            for symbol_index, symbol in enumerate(letter):
                if symbol == '.':
                    events.append(("tone", 1))
                elif symbol == '-':
                    events.append(("tone", 3))
                else:
                    raise ValueError(f"Unsupported symbol '{symbol}' in Morse code")
                if symbol_index != len(letter) - 1:
                    events.append(("gap", _UNIT_GAP_AFTER_SYMBOL))
            if letter_index != len(letters) - 1:
                events.append(("gap", _GAP_BETWEEN_LETTERS))
        if word_index != len(words) - 1:
            events.append(("gap", _GAP_BETWEEN_WORDS))
    return events


def synthesize_morse_audio(
    morse_code: str,
    *,
    frequency: float = 600.0,
    unit_duration_ms: int = 100,
    volume: float = 0.5,
    sample_rate: int = 44100,
) -> Path:
    """Generate a temporary WAV file for the provided Morse sequence."""

    events = list(_parse_morse_sequence(morse_code))
    if not events:
        raise ValueError("No Morse content available for audio synthesis")

    amplitude = max(0.0, min(volume, 1.0)) * 32767
    unit_seconds = unit_duration_ms / 1000.0

    samples = array("h")
    angle_step = 2 * math.pi * frequency / sample_rate

    for kind, units in events:
        duration_samples = max(1, int(unit_seconds * units * sample_rate))
        if kind == "tone":
            for index in range(duration_samples):
                value = int(amplitude * math.sin(angle_step * index))
                samples.append(value)
        else:
            samples.extend([0] * duration_samples)

    temp_path = Path(tempfile.gettempdir()) / f"morse_{uuid4().hex}.wav"
    with wave.open(str(temp_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())
    return temp_path


__all__ = ["synthesize_morse_audio"]
