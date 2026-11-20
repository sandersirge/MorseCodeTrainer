"""Plays Morse audio from memory, and keeps working when there is no sound device."""

from __future__ import annotations

import io
import logging
from collections import OrderedDict
from typing import Any

from .audio_settings import AudioSettings, AudioSettingsStore
from .morse_audio import DEFAULT_SAMPLE_RATE, render_wav_bytes

_log = logging.getLogger(__name__)
_CACHE_SIZE = 64


class AudioPlayer:
	"""Wraps ``pygame.mixer``.

	Sounds are rendered in memory (no temporary files to clean up or to be
	locked by the OS) and cached per Morse text + settings. If the mixer can't
	start (no audio device, remote desktop, headless Linux), ``available`` is
	False and every call is a harmless no-op instead of a crash.
	"""

	def __init__(self, pygame_module: Any, settings_store: AudioSettingsStore) -> None:
		self._pygame = pygame_module
		self._store = settings_store
		self._available = False
		self._sample_rate = DEFAULT_SAMPLE_RATE
		self._channel: Any = None
		self._sounds: OrderedDict[tuple[str, AudioSettings], Any] = OrderedDict()

	@property
	def available(self) -> bool:
		return self._available

	@property
	def settings(self) -> AudioSettings:
		return self._store.settings

	def start(self) -> bool:
		"""Open the audio device. Returns False (and stays silent) on failure."""

		try:
			self._pygame.mixer.init(frequency=DEFAULT_SAMPLE_RATE, size=-16, channels=1)
			init = self._pygame.mixer.get_init()
			if init:
				self._sample_rate = int(init[0])
			self._available = True
		except Exception:
			_log.warning("Audio device unavailable; continuing without sound", exc_info=True)
			self._available = False
		return self._available

	def play_morse(self, morse_code: str) -> bool:
		"""Play *morse_code* with the current settings. Returns True if it started."""

		if not self._available or not morse_code.strip():
			return False
		try:
			sound = self._sound_for(morse_code, self._store.settings)
			self.stop()
			self._channel = sound.play()
			return True
		except Exception:
			_log.warning("Could not play Morse audio", exc_info=True)
			return False

	def stop(self) -> None:
		if not self._available:
			return
		try:
			self._pygame.mixer.stop()
		except Exception:
			_log.debug("mixer.stop failed", exc_info=True)
		self._channel = None

	def is_busy(self) -> bool:
		if not self._available or self._channel is None:
			return False
		try:
			return bool(self._channel.get_busy())
		except Exception:
			return False

	def shutdown(self) -> None:
		if self._available:
			try:
				self._pygame.mixer.quit()
			except Exception:
				_log.debug("mixer.quit failed", exc_info=True)
		self._available = False
		self._sounds.clear()

	def _sound_for(self, morse_code: str, settings: AudioSettings) -> Any:
		key = (morse_code, settings)
		sound = self._sounds.get(key)
		if sound is None:
			wav = render_wav_bytes(morse_code, settings, self._sample_rate)
			# Loading a WAV from memory lets pygame convert it to whatever format
			# the device actually opened with (mono/stereo, 16/32-bit, ...).
			sound = self._pygame.mixer.Sound(file=io.BytesIO(wav))
			self._sounds[key] = sound
			if len(self._sounds) > _CACHE_SIZE:
				self._sounds.popitem(last=False)
		else:
			self._sounds.move_to_end(key)
		return sound


__all__ = ["AudioPlayer"]
