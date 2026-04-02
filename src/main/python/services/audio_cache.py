"""Dynamic audio cache that synthesizes morse audio on demand."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from pathlib import Path

from .morse_audio import synthesize_morse_audio

_log = logging.getLogger(__name__)


class AudioCache:
	"""Synthesizes and caches morse audio files, with optional static fallback."""

	def __init__(self, static_map: Mapping[str, str] | None = None) -> None:
		self._static_map: Mapping[str, str] = static_map or {}
		self._cache: dict[str, str] = {}

	def resolve(self, morse_code: str, key: str) -> str | None:
		"""Synthesize audio for *morse_code*, caching under *key*.

		Returns the file path as a string, or ``None`` on error.
		"""

		cached = self._cache.get(key)
		if cached is not None:
			return cached

		try:
			path = synthesize_morse_audio(morse_code)
			self._cache[key] = str(path)
			return str(path)
		except Exception:
			_log.debug("audio synthesis failed for key=%s", key, exc_info=True)
			return None

	def resolve_with_fallback(self, morse_code: str, key: str) -> str | None:
		"""Try dynamic synthesis first, then fall back to the static map."""

		result = self.resolve(morse_code, key)
		if result is not None:
			return result
		return self._static_map.get(key)

	def cleanup(self) -> None:
		"""Delete all cached temporary audio files."""

		for path_str in self._cache.values():
			try:
				Path(path_str).unlink(missing_ok=True)
			except OSError:
				_log.debug("failed to delete %s", path_str, exc_info=True)
		self._cache.clear()


__all__ = ["AudioCache"]
