"""Decode Morse sent with a straight key (key down / key up timestamps)."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..exceptions import MorseTrainerError
from ..utils.morse_translator import convert_morse_to_text

# Timing thresholds in dot units. Human keying is uneven, so the boundaries
# sit halfway between the ideal values (dot 1 / dash 3, gaps 1 / 3 / 7).
_DASH_FROM_UNITS = 2.0
_LETTER_GAP_FROM_UNITS = 2.0
_WORD_GAP_FROM_UNITS = 5.0


@dataclass
class KeyerDecoder:
	"""Feed it key presses with timestamps (seconds); read back Morse and text.

	*unit* is the length of one dot in seconds (1.2 / WPM).
	"""

	unit: float
	_letters: list[list[str]] = field(default_factory=lambda: [[]])
	_current: str = ""
	_down_at: float | None = None
	_up_at: float | None = None
	_durations: list[float] = field(default_factory=list)

	@property
	def is_down(self) -> bool:
		return self._down_at is not None

	def key_down(self, now: float) -> None:
		if self._down_at is not None:
			return  # auto-repeat while held
		if self._up_at is not None:
			self._close_gap(now - self._up_at)
		self._down_at = now

	def key_up(self, now: float) -> None:
		if self._down_at is None:
			return
		held = now - self._down_at
		self._durations.append(held)
		self._current += "." if held < _DASH_FROM_UNITS * self.unit else "-"
		self._down_at = None
		self._up_at = now

	def tick(self, now: float) -> None:
		"""Call regularly: finishes the last letter once the key stays up long enough."""
		if self._down_at is None and self._up_at is not None and self._current:
			if now - self._up_at >= _LETTER_GAP_FROM_UNITS * self.unit:
				self._finish_letter()

	def clear(self) -> None:
		self._letters = [[]]
		self._current = ""
		self._down_at = None
		self._up_at = None
		self._durations.clear()

	@property
	def morse(self) -> str:
		"""Everything sent so far, including the letter still being keyed."""
		words = [list(word) for word in self._letters]
		if self._current:
			words[-1].append(self._current)
		return "   ".join(" ".join(word) for word in words if word)

	@property
	def text(self) -> str:
		"""Decoded text of the finished letters; unknown codes show as '?'."""
		words = []
		for word in self._letters:
			if word:
				words.append("".join(_decode_letter(code) for code in word))
		return " ".join(words)

	@property
	def estimated_wpm(self) -> int | None:
		"""Speed estimated from the dots sent (needs a few elements)."""
		dots = [d for d in self._durations if d < _DASH_FROM_UNITS * self.unit]
		if len(dots) < 3:
			return None
		average_dot = sum(dots) / len(dots)
		return round(1.2 / average_dot) if average_dot > 0 else None

	def _close_gap(self, gap: float) -> None:
		if gap >= _LETTER_GAP_FROM_UNITS * self.unit and self._current:
			self._finish_letter()
		if gap >= _WORD_GAP_FROM_UNITS * self.unit and self._letters[-1]:
			self._letters.append([])

	def _finish_letter(self) -> None:
		self._letters[-1].append(self._current)
		self._current = ""


def _decode_letter(code: str) -> str:
	try:
		return convert_morse_to_text(code)
	except MorseTrainerError:
		return "?"


__all__ = ["KeyerDecoder"]
