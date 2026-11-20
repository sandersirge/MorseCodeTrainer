from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..exceptions import (
	AudioSaveError,
	InvalidModeError,
	MorseTrainerError,
	NoAudioContentError,
)
from ..services.audio_settings import AudioSettingsStore
from ..services.morse_audio import save_wav
from ..strings import t
from ..utils import morse_translator

_OUTPUT_PREFIX = "tõlge"


def default_output_dir() -> Path:
	"""Where "Save" puts files: a folder in the user's Documents.

	The working directory is not usable for this: in a packaged app it is "/"
	on macOS and may be read-only (e.g. Program Files) on Windows.
	"""

	documents = Path.home() / "Documents"
	base = documents if documents.is_dir() else Path.home()
	return base / "MorseCodeTrainer"


@dataclass(frozen=True)
class SandboxState:
	"""Mutable sandbox view state exported as an immutable snapshot."""

	mode: str
	mode_label: str
	input_label: str
	output_label: str
	input_text: str
	output_text: str
	error_message: str | None
	audio_ready: bool
	audio_morse: str | None
	volume: float
	wpm: int
	effective_wpm: int
	pitch_hz: float


class TranslationSandboxPresenter:
	"""Handles free-form translation and audio settings."""

	_MODE_LABELS = {
		"text_to_morse": t("common.tekst_morse"),
		"morse_to_text": t("common.morse_tekst"),
	}

	_INPUT_LABELS = {
		"text_to_morse": t("sandbox.tekst"),
		"morse_to_text": t("sandbox.morse"),
	}

	_OUTPUT_LABELS = {
		"text_to_morse": t("sandbox.morse"),
		"morse_to_text": t("sandbox.tekst"),
	}

	def __init__(
		self,
		settings_store: AudioSettingsStore | None = None,
		*,
		output_dir: Path | None = None,
	) -> None:
		self._store = settings_store or AudioSettingsStore()
		self._output_dir = output_dir
		self._mode = "text_to_morse"
		self._input_text = ""
		self._output_text = ""
		self._error_message: str | None = None
		self._morse_source: str = ""

	def current_state(self) -> SandboxState:
		return self._build_state()

	def toggle_mode(self) -> SandboxState:
		other = "morse_to_text" if self._mode == "text_to_morse" else "text_to_morse"
		return self.set_mode(other)

	def set_mode(self, mode: str) -> SandboxState:
		if mode not in self._MODE_LABELS:
			raise InvalidModeError(mode)
		if mode == self._mode:
			return self._build_state()
		self._mode = mode
		self._input_text = ""
		self._output_text = ""
		self._error_message = None
		self._morse_source = ""
		return self._build_state()

	def translate(self, text: str) -> SandboxState:
		self._input_text = text
		if not text.strip():
			self._output_text = ""
			self._error_message = None
			self._morse_source = ""
			return self._build_state()

		try:
			if self._mode == "text_to_morse":
				self._output_text = morse_translator.convert_text_to_morse(text)
				self._morse_source = self._output_text
			else:
				self._output_text = morse_translator.convert_morse_to_text(text)
				self._morse_source = morse_translator.normalize_morse(text)
			self._error_message = None
		except MorseTrainerError as exc:
			self._output_text = ""
			self._morse_source = ""
			self._error_message = exc.user_message
		return self._build_state()

	def clear_audio(self) -> SandboxState:
		self._morse_source = ""
		return self._build_state()

	def save_audio_to_output(self) -> tuple[SandboxState, Path]:
		target = self._next_output_file()
		return self._build_state(), self._save(target)

	def save_audio_as(self, destination: Path) -> tuple[SandboxState, Path]:
		return self._build_state(), self._save(destination)

	def suggested_save_path(self) -> Path:
		return self._next_output_file()

	def update_volume(self, volume: float) -> SandboxState:
		self._store.update(self._store.settings.with_volume(volume))
		return self._build_state()

	def update_wpm(self, wpm: int) -> SandboxState:
		self._store.update(self._store.settings.with_wpm(wpm))
		return self._build_state()

	def update_effective_wpm(self, effective_wpm: int) -> SandboxState:
		self._store.update(self._store.settings.with_effective_wpm(effective_wpm))
		return self._build_state()

	def update_pitch(self, frequency_hz: float) -> SandboxState:
		self._store.update(self._store.settings.with_pitch(frequency_hz))
		return self._build_state()

	def _save(self, destination: Path) -> Path:
		if not self._morse_source:
			raise NoAudioContentError(user_message=t("sandbox.ei_ole_helifaili_salvestamiseks"))
		try:
			return save_wav(destination, self._morse_source, self._store.settings)
		except OSError as exc:
			raise AudioSaveError(
				"Failed to save audio file",
				user_message=t("sandbox.helifaili_ei_onnestunud_salvestada"),
				cause=exc,
			) from exc

	def _next_output_file(self) -> Path:
		output_dir = self._output_dir or default_output_dir()
		highest_index = 0
		if output_dir.is_dir():
			for candidate in output_dir.glob(f"{_OUTPUT_PREFIX}*.wav"):
				suffix = candidate.stem[len(_OUTPUT_PREFIX) :]
				if suffix.isdigit():
					highest_index = max(highest_index, int(suffix))
		return output_dir / f"{_OUTPUT_PREFIX}{highest_index + 1}.wav"

	def _build_state(self) -> SandboxState:
		settings = self._store.settings
		return SandboxState(
			mode=self._mode,
			mode_label=self._MODE_LABELS[self._mode],
			input_label=self._INPUT_LABELS[self._mode],
			output_label=self._OUTPUT_LABELS[self._mode],
			input_text=self._input_text,
			output_text=self._output_text,
			error_message=self._error_message,
			audio_ready=bool(self._morse_source),
			audio_morse=self._morse_source or None,
			volume=settings.volume,
			wpm=settings.wpm,
			effective_wpm=settings.effective_wpm,
			pitch_hz=settings.frequency_hz,
		)


__all__ = ["SandboxState", "TranslationSandboxPresenter", "default_output_dir"]
