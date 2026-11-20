"""Keyer practice: send a target word with a straight key and check it."""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass

from ..model.keyer import KeyerDecoder
from ..model.training import score_copy
from ..services.audio_settings import AudioSettingsStore
from ..services.progress_store import ProgressStore
from ..utils.morse_translator import convert_text_to_morse


@dataclass(frozen=True)
class KeyerState:
	target: str
	target_morse: str
	sent_morse: str
	sent_text: str
	wpm: int
	estimated_wpm: int | None
	checked: bool
	correct: bool


class KeyerPresenter:
	"""Owns the decoder; the view only forwards key presses with timestamps."""

	def __init__(
		self,
		settings_store: AudioSettingsStore,
		words: Sequence[str],
		progress: ProgressStore | None = None,
		rng: random.Random | None = None,
	) -> None:
		self._store = settings_store
		# Short words are easier to key; fall back to all words if none are short.
		self._words = [w for w in words if len(w) <= 5] or list(words)
		self._progress = progress
		self._rng = rng or random.Random()
		self._decoder = KeyerDecoder(unit=self._unit())
		self._target = ""
		self._checked = False
		self._correct = False
		self.new_target()

	def _unit(self) -> float:
		return 1.2 / self._store.settings.wpm

	@property
	def is_key_down(self) -> bool:
		return self._decoder.is_down

	def key_down(self, now: float) -> None:
		self._decoder.unit = self._unit()
		self._decoder.key_down(now)

	def key_up(self, now: float) -> None:
		self._decoder.key_up(now)

	def tick(self, now: float) -> None:
		self._decoder.tick(now)

	def clear(self) -> KeyerState:
		self._decoder.clear()
		self._checked = False
		self._correct = False
		return self.current_state()

	def new_target(self) -> KeyerState:
		self._target = self._rng.choice(self._words).upper()
		return self.clear()

	def check(self) -> KeyerState:
		sent = self._decoder.text
		self._checked = True
		self._correct = sent.replace(" ", "") == self._target.replace(" ", "")
		if self._progress is not None and sent:
			self._progress.record_many(score_copy(self._target, sent).per_char)
		return self.current_state()

	def current_state(self) -> KeyerState:
		return KeyerState(
			target=self._target,
			target_morse=convert_text_to_morse(self._target),
			sent_morse=self._decoder.morse,
			sent_text=self._decoder.text,
			wpm=self._store.settings.wpm,
			estimated_wpm=self._decoder.estimated_wpm,
			checked=self._checked,
			correct=self._correct,
		)


__all__ = ["KeyerPresenter", "KeyerState"]
