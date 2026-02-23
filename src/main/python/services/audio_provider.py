from __future__ import annotations

try:
    import pygame  # type: ignore[import]
except ImportError:  # pragma: no cover - fallback for environments without pygame
    import pygame_ce as pygame  # type: ignore[import]

__all__ = ["pygame"]
