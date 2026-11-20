from __future__ import annotations

import os

# Keep pygame's "Hello from the pygame community" banner out of the console.
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

try:
	import pygame  # type: ignore[import]
except ImportError:  # pragma: no cover - fallback for environments without pygame
	import pygame_ce as pygame  # type: ignore[import]

__all__ = ["pygame"]
