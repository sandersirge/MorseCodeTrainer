from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import shutil

from ..services.audio_settings import AudioSettings
from ..utils import morse_translator
from ..services.morse_audio import synthesize_morse_audio


@dataclass(frozen=True)
class SandboxState:
    """Mutable sandbox view state exported as an immutable snapshot."""

    mode: str
    mode_label: str
    input_label: str
    output_label: str
    input_text: str
    output_text: str
    error_message: Optional[str]
    audio_ready: bool
    audio_path: Optional[Path]
    volume: float
    speed_ms: int
    pitch_hz: float


class TranslationSandboxPresenter:
    """Handles free-form translation and audio synthesis logic."""

    _MODE_LABELS = {
        "text_to_morse": "Tekst → Morse",
        "morse_to_text": "Morse → tekst",
    }

    _INPUT_LABELS = {
        "text_to_morse": "Tekst",
        "morse_to_text": "Morse",
    }

    _OUTPUT_LABELS = {
        "text_to_morse": "Morse",
        "morse_to_text": "Tekst",
    }

    def __init__(self) -> None:
        self._mode = "text_to_morse"
        self._input_text = ""
        self._output_text = ""
        self._error_message: Optional[str] = None
        self._morse_source: str = ""
        self._audio_path: Optional[Path] = None
        self._audio_settings = AudioSettings()

    def current_state(self) -> SandboxState:
        return self._build_state()

    def toggle_mode(self) -> SandboxState:
        self._mode = "morse_to_text" if self._mode == "text_to_morse" else "text_to_morse"
        self._input_text = ""
        self._output_text = ""
        self._error_message = None
        self._morse_source = ""
        self._discard_audio_file()
        return self._build_state()

    def set_mode(self, mode: str) -> SandboxState:
        if mode not in self._MODE_LABELS:
            raise ValueError(f"Unsupported mode: {mode}")
        if mode == self._mode:
            return self._build_state()
        self._mode = mode
        self._input_text = ""
        self._output_text = ""
        self._error_message = None
        self._morse_source = ""
        self._discard_audio_file()
        return self._build_state()

    def translate(self, text: str) -> SandboxState:
        self._input_text = text
        trimmed = text.strip()
        if not trimmed:
            self._output_text = ""
            self._error_message = None
            self._morse_source = ""
            self._discard_audio_file()
            return self._build_state()

        try:
            if self._mode == "text_to_morse":
                self._output_text = morse_translator.convert_text_to_morse(text)
                self._morse_source = self._output_text.strip()
            else:
                self._output_text = morse_translator.convert_morse_to_text(text)
                self._morse_source = trimmed
            self._error_message = None
        except ValueError as exc:
            self._output_text = ""
            self._morse_source = ""
            self._error_message = str(exc)
            self._discard_audio_file()
            return self._build_state()

        self._refresh_temp_audio()
        return self._build_state()

    def generate_audio(
        self,
        *,
        frequency: Optional[float] = None,
        unit_duration_ms: Optional[int] = None,
        volume: Optional[float] = None,
    ) -> SandboxState:
        if not self._morse_source:
            raise ValueError("Audio available only when Morse content exists")
        if frequency is not None:
            self._audio_settings = self._audio_settings.with_pitch(frequency)
        if unit_duration_ms is not None:
            self._audio_settings = self._audio_settings.with_speed(unit_duration_ms)
        if volume is not None:
            self._audio_settings = self._audio_settings.with_volume(volume)
        self._refresh_temp_audio()
        return self._build_state()

    def clear_audio(self) -> SandboxState:
        self._discard_audio_file()
        return self._build_state()

    def save_audio_to_output(self) -> tuple[SandboxState, Path]:
        if not self._audio_path:
            raise ValueError("Ei ole helifaili salvestamiseks.")
        target = self._next_output_file()
        try:
            shutil.copy2(self._audio_path, target)
        except OSError as exc:
            raise ValueError("Helifaili ei õnnestunud salvestada.") from exc
        self._discard_audio_file()
        return self._build_state(), target

    def save_audio_as(self, destination: Path) -> tuple[SandboxState, Path]:
        if not self._audio_path:
            raise ValueError("Ei ole helifaili salvestamiseks.")
        resolved_destination = destination
        if resolved_destination.suffix.lower() != ".wav":
            resolved_destination = resolved_destination.with_suffix(".wav")
        resolved_destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(self._audio_path, resolved_destination)
        except OSError as exc:
            raise ValueError("Helifaili ei õnnestunud salvestada.") from exc
        self._discard_audio_file()
        return self._build_state(), resolved_destination

    def _next_output_file(self) -> Path:
        output_dir = Path.cwd() / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        prefix = "tõlge"
        highest_index = 0
        for candidate in output_dir.glob(f"{prefix}*.wav"):
            suffix = candidate.stem[len(prefix):]
            if suffix.isdigit():
                highest_index = max(highest_index, int(suffix))
        next_index = highest_index + 1
        return output_dir / f"{prefix}{next_index}.wav"

    def update_volume(self, volume: float) -> SandboxState:
        self._audio_settings = self._audio_settings.with_volume(volume)
        if self._morse_source:
            self._refresh_temp_audio()
        return self._build_state()

    def update_speed(self, unit_duration_ms: int) -> SandboxState:
        self._audio_settings = self._audio_settings.with_speed(unit_duration_ms)
        if self._morse_source:
            self._refresh_temp_audio()
        return self._build_state()

    def update_pitch(self, frequency_hz: float) -> SandboxState:
        self._audio_settings = self._audio_settings.with_pitch(frequency_hz)
        if self._morse_source:
            self._refresh_temp_audio()
        return self._build_state()

    def _refresh_temp_audio(
        self,
    ) -> None:
        self._discard_audio_file()
        if not self._morse_source:
            return
        try:
            self._audio_path = synthesize_morse_audio(
                self._morse_source,
                **self._audio_settings.as_synthesis_kwargs,
            )
        except ValueError as exc:
            self._audio_path = None

    def _discard_audio_file(self) -> bool:
        if not self._audio_path:
            return False
        try:
            if self._audio_path.exists():
                self._audio_path.unlink()
        except OSError:
            pass
        finally:
            self._audio_path = None
        return True

    def _build_state(self) -> SandboxState:
        return SandboxState(
            mode=self._mode,
            mode_label=self._MODE_LABELS[self._mode],
            input_label=self._INPUT_LABELS[self._mode],
            output_label=self._OUTPUT_LABELS[self._mode],
            input_text=self._input_text,
            output_text=self._output_text,
            error_message=self._error_message,
            audio_ready=self._audio_path is not None,
            audio_path=self._audio_path,
            volume=self._audio_settings.volume,
            speed_ms=self._audio_settings.unit_duration_ms,
            pitch_hz=self._audio_settings.frequency_hz,
        )


__all__ = ["SandboxState", "TranslationSandboxPresenter"]
