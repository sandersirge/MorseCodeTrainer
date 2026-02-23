"""Tests for AudioSettings service."""
import pytest
from src.main.python.services.audio_settings import AudioSettings, _clamp


class TestAudioSettingsDefaults:
    """Tests for default values."""

    def test_default_volume(self):
        settings = AudioSettings()
        assert settings.volume == 0.5

    def test_default_unit_duration_ms(self):
        settings = AudioSettings()
        assert settings.unit_duration_ms == 60

    def test_default_frequency_hz(self):
        settings = AudioSettings()
        assert settings.frequency_hz == 400.0


class TestAudioSettingsWithVolume:
    """Tests for with_volume method."""

    def test_with_volume_sets_value(self):
        settings = AudioSettings().with_volume(0.8)
        assert settings.volume == 0.8

    def test_with_volume_clamps_max(self):
        settings = AudioSettings().with_volume(1.5)
        assert settings.volume == 1.0

    def test_with_volume_clamps_min(self):
        settings = AudioSettings().with_volume(-0.5)
        assert settings.volume == 0.0

    def test_with_volume_preserves_other_fields(self):
        settings = AudioSettings(unit_duration_ms=100, frequency_hz=500.0)
        new_settings = settings.with_volume(0.9)
        assert new_settings.unit_duration_ms == 100
        assert new_settings.frequency_hz == 500.0


class TestAudioSettingsWithSpeed:
    """Tests for with_speed method."""

    def test_with_speed_sets_value(self):
        settings = AudioSettings().with_speed(100)
        assert settings.unit_duration_ms == 100

    def test_with_speed_clamps_max(self):
        settings = AudioSettings().with_speed(300)
        assert settings.unit_duration_ms == 180

    def test_with_speed_clamps_min(self):
        settings = AudioSettings().with_speed(10)
        assert settings.unit_duration_ms == 30

    def test_with_speed_preserves_other_fields(self):
        settings = AudioSettings(volume=0.7, frequency_hz=500.0)
        new_settings = settings.with_speed(120)
        assert new_settings.volume == 0.7
        assert new_settings.frequency_hz == 500.0


class TestAudioSettingsWithPitch:
    """Tests for with_pitch method."""

    def test_with_pitch_sets_value(self):
        settings = AudioSettings().with_pitch(600.0)
        assert settings.frequency_hz == 600.0

    def test_with_pitch_clamps_max(self):
        settings = AudioSettings().with_pitch(1000.0)
        assert settings.frequency_hz == 800.0

    def test_with_pitch_clamps_min(self):
        settings = AudioSettings().with_pitch(100.0)
        assert settings.frequency_hz == 200.0

    def test_with_pitch_preserves_other_fields(self):
        settings = AudioSettings(volume=0.7, unit_duration_ms=100)
        new_settings = settings.with_pitch(550.0)
        assert new_settings.volume == 0.7
        assert new_settings.unit_duration_ms == 100


class TestAudioSettingsSynthesisKwargs:
    """Tests for as_synthesis_kwargs property."""

    def test_returns_dict_with_correct_keys(self):
        settings = AudioSettings()
        kwargs = settings.as_synthesis_kwargs
        assert "volume" in kwargs
        assert "unit_duration_ms" in kwargs
        assert "frequency" in kwargs

    def test_returns_correct_values(self):
        settings = AudioSettings(volume=0.8, unit_duration_ms=80, frequency_hz=500.0)
        kwargs = settings.as_synthesis_kwargs
        assert kwargs["volume"] == 0.8
        assert kwargs["unit_duration_ms"] == 80
        assert kwargs["frequency"] == 500.0


class TestAudioSettingsImmutability:
    """Tests for immutability."""

    def test_settings_is_frozen(self):
        settings = AudioSettings()
        with pytest.raises(AttributeError):
            settings.volume = 0.9

    def test_with_methods_return_new_instance(self):
        original = AudioSettings()
        new = original.with_volume(0.9)
        assert original is not new
        assert original.volume == 0.5
        assert new.volume == 0.9


class TestClampFunction:
    """Tests for _clamp helper function."""

    def test_clamp_within_range(self):
        assert _clamp(5.0, 0.0, 10.0) == 5.0

    def test_clamp_at_lower_bound(self):
        assert _clamp(0.0, 0.0, 10.0) == 0.0

    def test_clamp_at_upper_bound(self):
        assert _clamp(10.0, 0.0, 10.0) == 10.0

    def test_clamp_below_lower_bound(self):
        assert _clamp(-5.0, 0.0, 10.0) == 0.0

    def test_clamp_above_upper_bound(self):
        assert _clamp(15.0, 0.0, 10.0) == 10.0
