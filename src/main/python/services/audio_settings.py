"""Audio settings shared by every screen that plays Morse."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

MIN_VOLUME = 0.0
MAX_VOLUME = 1.0
MIN_FREQUENCY_HZ = 300.0
MAX_FREQUENCY_HZ = 1000.0
MIN_WPM = 5
MAX_WPM = 40
DEFAULT_FREQUENCY_HZ = 600.0
DEFAULT_WPM = 20
DEFAULT_EFFECTIVE_WPM = 15
DEFAULT_VOLUME = 0.5


@dataclass(frozen=True)
class AudioSettings:
	"""Immutable audio configuration.

	*wpm* is the character speed: how fast each letter is sent.
	*effective_wpm* is the overall speed. When it is lower than *wpm*, the
	letters keep their full speed but the gaps between letters and words get
	longer (Farnsworth timing), which is the usual way to learn Morse by ear.
	"""

	volume: float = DEFAULT_VOLUME
	wpm: int = DEFAULT_WPM
	effective_wpm: int = DEFAULT_EFFECTIVE_WPM
	frequency_hz: float = DEFAULT_FREQUENCY_HZ

	def __post_init__(self) -> None:
		wpm = int(round(_clamp(self.wpm, MIN_WPM, MAX_WPM)))
		object.__setattr__(self, "volume", _clamp(self.volume, MIN_VOLUME, MAX_VOLUME))
		object.__setattr__(self, "wpm", wpm)
		object.__setattr__(
			self, "effective_wpm", int(round(_clamp(self.effective_wpm, MIN_WPM, wpm)))
		)
		object.__setattr__(
			self, "frequency_hz", _clamp(self.frequency_hz, MIN_FREQUENCY_HZ, MAX_FREQUENCY_HZ)
		)

	@property
	def unit_ms(self) -> float:
		"""Length of one dot. Standard "PARIS" timing: 1200 ms / WPM."""
		return 1200.0 / self.wpm

	def with_volume(self, volume: float) -> AudioSettings:
		return replace(self, volume=volume)

	def with_wpm(self, wpm: int) -> AudioSettings:
		"""Change the character speed; the overall speed never exceeds it."""
		return replace(self, wpm=wpm, effective_wpm=min(self.effective_wpm, int(round(wpm))))

	def with_effective_wpm(self, effective_wpm: int) -> AudioSettings:
		return replace(self, effective_wpm=effective_wpm)

	def with_pitch(self, frequency_hz: float) -> AudioSettings:
		return replace(self, frequency_hz=frequency_hz)


class AudioSettingsStore:
	"""Holds the current settings and tells listeners when they change."""

	def __init__(self, settings: AudioSettings | None = None) -> None:
		self._settings = settings or AudioSettings()
		self._listeners: list[Callable[[AudioSettings], None]] = []

	@property
	def settings(self) -> AudioSettings:
		return self._settings

	def update(self, settings: AudioSettings) -> None:
		if settings == self._settings:
			return
		self._settings = settings
		for listener in list(self._listeners):
			listener(settings)

	def subscribe(self, listener: Callable[[AudioSettings], None]) -> None:
		if listener not in self._listeners:
			self._listeners.append(listener)


def _clamp(value: float, lower: float, upper: float) -> float:
	return max(lower, min(value, upper))


__all__ = [
	"AudioSettings",
	"AudioSettingsStore",
	"MAX_FREQUENCY_HZ",
	"MAX_WPM",
	"MIN_FREQUENCY_HZ",
	"MIN_WPM",
]
