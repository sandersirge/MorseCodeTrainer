"""Saved training progress: per-character results, Koch level and audio settings.

Stored as JSON in the user's data folder, so it survives restarts and app
updates:

- Windows: %APPDATA%/MorseCodeTrainer/progress.json
- macOS:   ~/Library/Application Support/MorseCodeTrainer/progress.json
- Linux:   $XDG_DATA_HOME (or ~/.local/share)/MorseCodeTrainer/progress.json
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from .audio_settings import AudioSettings

_log = logging.getLogger(__name__)
_FILE_VERSION = 1
# Characters never practised count as fairly weak so they still come up.
_UNSEEN_WEAKNESS = 0.5


def default_data_dir() -> Path:
	if sys.platform == "win32":
		base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
	elif sys.platform == "darwin":
		base = Path.home() / "Library" / "Application Support"
	else:
		base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
	return base / "MorseCodeTrainer"


@dataclass
class CharStats:
	correct: int = 0
	wrong: int = 0

	@property
	def attempts(self) -> int:
		return self.correct + self.wrong

	@property
	def accuracy(self) -> float | None:
		return self.correct / self.attempts if self.attempts else None


class ProgressStore:
	"""Keeps progress in memory and writes it to disk after every change."""

	def __init__(self, path: Path | None = None, *, autosave: bool = True) -> None:
		self.path = path or default_data_dir() / "progress.json"
		self._autosave = autosave
		self._chars: dict[str, CharStats] = {}
		self._koch_level = 2
		self._audio: dict[str, float] | None = None
		self._load()

	# Per-character results --------------------------------------------------

	def record(self, char: str, correct: bool) -> None:
		stats = self._chars.setdefault(char.upper(), CharStats())
		if correct:
			stats.correct += 1
		else:
			stats.wrong += 1
		self._save()

	def record_many(self, results: dict[str, tuple[int, int]]) -> None:
		"""Add (correct, wrong) counts for several characters at once."""
		for char, (correct, wrong) in results.items():
			stats = self._chars.setdefault(char.upper(), CharStats())
			stats.correct += correct
			stats.wrong += wrong
		self._save()

	def stats(self, char: str) -> CharStats:
		return self._chars.get(char.upper(), CharStats())

	def weakness(self, char: str) -> float:
		"""0 = always right, 1 = always wrong; recent beginners count as 0.5.

		A character needs a few attempts before a perfect score counts fully,
		so one lucky answer doesn't hide it.
		"""
		stats = self.stats(char)
		if stats.attempts == 0:
			return _UNSEEN_WEAKNESS
		confidence = min(1.0, stats.attempts / 5)
		error_rate = stats.wrong / stats.attempts
		return confidence * error_rate + (1 - confidence) * _UNSEEN_WEAKNESS

	def weakest(self, chars: list[str], count: int = 5) -> list[str]:
		practised = [c for c in chars if self.stats(c).attempts]
		return sorted(practised, key=self.weakness, reverse=True)[:count]

	# Koch lessons -----------------------------------------------------------

	@property
	def koch_level(self) -> int:
		"""How many Koch characters are unlocked (starts at 2)."""
		return self._koch_level

	def set_koch_level(self, level: int) -> None:
		self._koch_level = max(2, level)
		self._save()

	# Audio settings ---------------------------------------------------------

	def audio_settings(self) -> AudioSettings | None:
		if not self._audio:
			return None
		try:
			return AudioSettings(**self._audio)
		except TypeError:
			return None

	def save_audio_settings(self, settings: AudioSettings) -> None:
		self._audio = asdict(settings)
		self._save()

	def reset(self) -> None:
		self._chars.clear()
		self._koch_level = 2
		self._save()

	# Persistence --------------------------------------------------------------

	def _load(self) -> None:
		try:
			data = json.loads(self.path.read_text(encoding="utf-8"))
		except FileNotFoundError:
			return
		except (OSError, ValueError):
			_log.warning("Progress file unreadable, starting fresh: %s", self.path)
			return
		chars = data.get("characters", {})
		self._chars = {
			c: CharStats(int(v.get("correct", 0)), int(v.get("wrong", 0))) for c, v in chars.items()
		}
		self._koch_level = max(2, int(data.get("koch_level", 2)))
		self._audio = data.get("audio") or None

	def _save(self) -> None:
		if not self._autosave:
			return
		data = {
			"version": _FILE_VERSION,
			"koch_level": self._koch_level,
			"characters": {c: asdict(s) for c, s in sorted(self._chars.items())},
			"audio": self._audio,
		}
		try:
			self.path.parent.mkdir(parents=True, exist_ok=True)
			# Write to a temp file and swap it in, so a crash can't leave half a file.
			tmp = self.path.with_suffix(".tmp")
			tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
			tmp.replace(self.path)
		except OSError:
			_log.warning("Could not save progress to %s", self.path, exc_info=True)


__all__ = ["CharStats", "ProgressStore", "default_data_dir"]
