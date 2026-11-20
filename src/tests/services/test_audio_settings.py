"""Tests for AudioSettings and AudioSettingsStore."""

import dataclasses

import pytest

from src.main.python.services.audio_settings import (
	MAX_FREQUENCY_HZ,
	MAX_WPM,
	MIN_FREQUENCY_HZ,
	MIN_WPM,
	AudioSettings,
	AudioSettingsStore,
	_clamp,
)


class TestAudioSettingsDefaults:
	def test_default_volume(self):
		assert AudioSettings().volume == 0.5

	def test_default_speeds_use_farnsworth(self):
		settings = AudioSettings()
		assert settings.wpm == 20
		assert settings.effective_wpm == 15

	def test_default_frequency_hz(self):
		assert AudioSettings().frequency_hz == 600.0


class TestUnitDuration:
	@pytest.mark.parametrize(("wpm", "unit_ms"), [(20, 60.0), (12, 100.0), (5, 240.0), (40, 30.0)])
	def test_paris_timing(self, wpm, unit_ms):
		assert AudioSettings(wpm=wpm, effective_wpm=wpm).unit_ms == pytest.approx(unit_ms)


class TestClampingOnCreation:
	def test_volume_clamped(self):
		assert AudioSettings(volume=3.0).volume == 1.0
		assert AudioSettings(volume=-1.0).volume == 0.0

	def test_wpm_clamped(self):
		assert AudioSettings(wpm=500).wpm == MAX_WPM
		assert AudioSettings(wpm=0, effective_wpm=0).wpm == MIN_WPM

	def test_effective_wpm_never_above_wpm(self):
		assert AudioSettings(wpm=18, effective_wpm=30).effective_wpm == 18

	def test_frequency_clamped(self):
		assert AudioSettings(frequency_hz=50).frequency_hz == MIN_FREQUENCY_HZ
		assert AudioSettings(frequency_hz=5000).frequency_hz == MAX_FREQUENCY_HZ


class TestWithMethods:
	def test_with_volume(self):
		assert AudioSettings().with_volume(0.8).volume == 0.8

	def test_with_wpm_lowers_effective_speed_if_needed(self):
		settings = AudioSettings(wpm=25, effective_wpm=20).with_wpm(10)
		assert settings.wpm == 10
		assert settings.effective_wpm == 10

	def test_with_wpm_keeps_lower_effective_speed(self):
		settings = AudioSettings(wpm=20, effective_wpm=12).with_wpm(30)
		assert settings.wpm == 30
		assert settings.effective_wpm == 12

	def test_with_effective_wpm(self):
		assert AudioSettings(wpm=25, effective_wpm=25).with_effective_wpm(15).effective_wpm == 15

	def test_with_pitch(self):
		assert AudioSettings().with_pitch(700).frequency_hz == 700

	def test_with_methods_preserve_other_fields(self):
		base = AudioSettings(volume=0.3, wpm=22, effective_wpm=18, frequency_hz=550)
		changed = base.with_pitch(650)
		assert (changed.volume, changed.wpm, changed.effective_wpm) == (0.3, 22, 18)


class TestImmutability:
	def test_settings_is_frozen(self):
		with pytest.raises(dataclasses.FrozenInstanceError):
			AudioSettings().volume = 1.0  # type: ignore[misc]

	def test_with_methods_return_new_instance(self):
		base = AudioSettings()
		assert base.with_volume(0.9) is not base

	def test_settings_are_hashable(self):
		# Used as part of the player's sound-cache key.
		assert hash(AudioSettings()) == hash(AudioSettings())


class TestAudioSettingsStore:
	def test_starts_with_defaults(self):
		assert AudioSettingsStore().settings == AudioSettings()

	def test_update_notifies_listeners(self):
		store = AudioSettingsStore()
		seen = []
		store.subscribe(seen.append)
		store.update(store.settings.with_volume(0.9))
		assert [s.volume for s in seen] == [0.9]

	def test_same_settings_do_not_notify(self):
		store = AudioSettingsStore()
		seen = []
		store.subscribe(seen.append)
		store.update(AudioSettings())
		assert seen == []


class TestClampFunction:
	@pytest.mark.parametrize(("value", "expected"), [(5, 5), (0, 0), (10, 10), (-3, 0), (42, 10)])
	def test_clamp(self, value, expected):
		assert _clamp(value, 0, 10) == expected
