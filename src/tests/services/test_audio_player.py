"""Tests for AudioPlayer with a fake pygame (no sound device needed)."""

import types

from src.main.python.services.audio_player import AudioPlayer
from src.main.python.services.audio_settings import AudioSettingsStore


class FakeChannel:
	def __init__(self) -> None:
		self.busy = True

	def get_busy(self) -> bool:
		return self.busy


class FakeSound:
	created = 0

	def __init__(self, file) -> None:
		FakeSound.created += 1
		self.data = file.read()
		self.channel = FakeChannel()

	def play(self) -> FakeChannel:
		return self.channel


def make_pygame(*, init_fails: bool = False):
	calls = {"stop": 0, "quit": 0}

	def init(**_kwargs):
		if init_fails:
			raise RuntimeError("No audio device")

	mixer = types.SimpleNamespace(
		init=init,
		get_init=lambda: (48000, -16, 2),
		Sound=FakeSound,
		stop=lambda: calls.__setitem__("stop", calls["stop"] + 1),
		quit=lambda: calls.__setitem__("quit", calls["quit"] + 1),
	)
	return types.SimpleNamespace(mixer=mixer), calls


class TestStartup:
	def test_available_after_successful_init(self):
		pygame, _ = make_pygame()
		player = AudioPlayer(pygame, AudioSettingsStore())
		assert player.start() is True
		assert player.available

	def test_missing_device_does_not_crash(self):
		pygame, _ = make_pygame(init_fails=True)
		player = AudioPlayer(pygame, AudioSettingsStore())
		assert player.start() is False
		assert not player.available
		# Every call is a safe no-op
		assert player.play_morse(".-") is False
		player.stop()
		assert player.is_busy() is False
		player.shutdown()


class TestPlayback:
	def setup_method(self):
		FakeSound.created = 0
		self.pygame, self.calls = make_pygame()
		self.store = AudioSettingsStore()
		self.player = AudioPlayer(self.pygame, self.store)
		self.player.start()

	def test_play_returns_true_and_is_busy(self):
		assert self.player.play_morse(".-") is True
		assert self.player.is_busy() is True

	def test_wav_rendered_at_device_rate(self):
		self.player.play_morse(".")
		# 48000 Hz reported by get_init -> RIFF header contains that rate
		sound = self.player._sounds[next(iter(self.player._sounds))]
		assert sound.data[:4] == b"RIFF"
		assert int.from_bytes(sound.data[24:28], "little") == 48000

	def test_sounds_are_cached(self):
		self.player.play_morse(".-")
		self.player.play_morse(".-")
		assert FakeSound.created == 1

	def test_settings_change_renders_new_sound(self):
		self.player.play_morse(".-")
		self.store.update(self.store.settings.with_pitch(800))
		self.player.play_morse(".-")
		assert FakeSound.created == 2

	def test_empty_morse_is_not_played(self):
		assert self.player.play_morse("   ") is False

	def test_invalid_morse_returns_false(self):
		assert self.player.play_morse(".x.") is False

	def test_stop_and_shutdown(self):
		self.player.play_morse(".")
		self.player.stop()
		assert self.calls["stop"] >= 1
		assert self.player.is_busy() is False
		self.player.shutdown()
		assert self.calls["quit"] == 1
		assert not self.player.available
