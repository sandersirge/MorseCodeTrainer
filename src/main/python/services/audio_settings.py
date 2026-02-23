from __future__ import annotations

from dataclasses import dataclass


_MIN_VOLUME = 0.0
_MAX_VOLUME = 1.0
_MIN_FREQUENCY_HZ = 200.0
_MAX_FREQUENCY_HZ = 800.0
_MIN_UNIT_DURATION_MS = 30
_MAX_UNIT_DURATION_MS = 180
_DEFAULT_FREQUENCY_HZ = 400.0
_DEFAULT_UNIT_DURATION_MS = 60
_DEFAULT_VOLUME = 0.5


@dataclass(frozen=True)
class AudioSettings:
    """Immutable audio synthesis configuration."""

    volume: float = _DEFAULT_VOLUME
    unit_duration_ms: int = _DEFAULT_UNIT_DURATION_MS
    frequency_hz: float = _DEFAULT_FREQUENCY_HZ

    def with_volume(self, volume: float) -> AudioSettings:
        return AudioSettings(
            volume=_clamp(volume, _MIN_VOLUME, _MAX_VOLUME),
            unit_duration_ms=self.unit_duration_ms,
            frequency_hz=self.frequency_hz,
        )

    def with_speed(self, unit_duration_ms: int) -> AudioSettings:
        clamped = int(_clamp(unit_duration_ms, _MIN_UNIT_DURATION_MS, _MAX_UNIT_DURATION_MS))
        return AudioSettings(
            volume=self.volume,
            unit_duration_ms=clamped,
            frequency_hz=self.frequency_hz,
        )

    def with_pitch(self, frequency_hz: float) -> AudioSettings:
        return AudioSettings(
            volume=self.volume,
            unit_duration_ms=self.unit_duration_ms,
            frequency_hz=_clamp(frequency_hz, _MIN_FREQUENCY_HZ, _MAX_FREQUENCY_HZ),
        )

    @property
    def as_synthesis_kwargs(self) -> dict[str, float | int]:
        return {
            "volume": self.volume,
            "unit_duration_ms": self.unit_duration_ms,
            "frequency": self.frequency_hz,
        }


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


__all__ = ["AudioSettings"]
