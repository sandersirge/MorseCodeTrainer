"""Small animation toolkit on top of Tk's ``after`` timer.

Everything here animates colours or ``place`` coordinates only, which Tk can
redraw cheaply on every platform. Set ``MORSETRAINER_NO_ANIMATIONS=1`` to make
every animation jump straight to its end state (used by the tests).
"""

from __future__ import annotations

import os
from collections.abc import Callable
from tkinter import TclError
from typing import Any

FRAME_MS = 16  # ~60 fps
ANIMATIONS_ENABLED = os.environ.get("MORSETRAINER_NO_ANIMATIONS", "") not in {"1", "true", "yes"}


def ease_out_cubic(t: float) -> float:
	t = max(0.0, min(1.0, t))
	return 1 - (1 - t) ** 3


def ease_in_out(t: float) -> float:
	t = max(0.0, min(1.0, t))
	return 4 * t**3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def _rgb(color: str) -> tuple[int, int, int]:
	color = color.lstrip("#")
	if len(color) == 3:
		color = "".join(c * 2 for c in color)
	return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def blend(color_a: str, color_b: str, t: float) -> str:
	"""Mix two #rrggbb colours; t=0 gives a, t=1 gives b."""
	t = max(0.0, min(1.0, t))
	ra, ga, ba = _rgb(color_a)
	rb, gb, bb = _rgb(color_b)
	return f"#{round(ra + (rb - ra) * t):02x}{round(ga + (gb - ga) * t):02x}{round(ba + (bb - ba) * t):02x}"


class Animation:
	"""One running animation; ``cancel()`` stops it without calling on_done."""

	def __init__(self, widget: Any) -> None:
		self._widget = widget
		self._job: str | None = None
		self.finished = False

	def cancel(self) -> None:
		if self._job is not None:
			try:
				self._widget.after_cancel(self._job)
			except (TclError, ValueError):
				pass
			self._job = None
		self.finished = True


def animate(
	widget: Any,
	duration_ms: int,
	on_step: Callable[[float], None],
	on_done: Callable[[], None] | None = None,
	*,
	easing: Callable[[float], float] = ease_out_cubic,
	clock: Callable[[], float] | None = None,
) -> Animation:
	"""Call ``on_step(progress)`` with eased progress 0..1 over *duration_ms*.

	Stops quietly if the widget is destroyed mid-way. With animations disabled
	(or a zero duration) it calls ``on_step(1.0)`` and ``on_done`` at once.
	"""
	animation = Animation(widget)
	if not ANIMATIONS_ENABLED or duration_ms <= 0:
		on_step(1.0)
		if on_done:
			on_done()
		animation.finished = True
		return animation

	if clock is None:
		import time

		clock = time.monotonic
	start = clock()

	def tick() -> None:
		animation._job = None
		if animation.finished:
			return
		try:
			if not widget.winfo_exists():
				animation.finished = True
				return
		except TclError:
			animation.finished = True
			return
		raw = (clock() - start) * 1000 / duration_ms
		try:
			on_step(easing(min(1.0, raw)))
		except TclError:
			animation.finished = True
			return
		if raw >= 1.0:
			animation.finished = True
			if on_done:
				on_done()
			return
		animation._job = widget.after(FRAME_MS, tick)

	tick()
	return animation


def tween_color(
	widget: Any,
	option: str,
	start: str,
	end: str,
	duration_ms: int = 120,
	previous: Animation | None = None,
) -> Animation:
	"""Fade one colour option (e.g. ``fg_color``) of a CTk widget."""
	if previous is not None:
		previous.cancel()
	return animate(
		widget, duration_ms, lambda p: widget.configure(**{option: blend(start, end, p)})
	)


__all__ = [
	"ANIMATIONS_ENABLED",
	"Animation",
	"animate",
	"blend",
	"ease_in_out",
	"ease_out_cubic",
	"tween_color",
]
