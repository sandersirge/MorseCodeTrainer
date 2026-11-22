"""Loading screen shown while the application builds its screens."""

from __future__ import annotations

import time
import tkinter
from collections.abc import Callable
from tkinter import TclError

import customtkinter as ctk

from ..strings import t
from .backdrop import PatternBackdrop
from .motion import ANIMATIONS_ENABLED, Animation, animate, blend, ease_in_out
from .theme import get_colors
from .widgets import accent_color, font_mono, font_muted, make_label, make_progress_bar

MIN_VISIBLE_MS = 700  # never flash: stay at least this long
_PULSE_MS = 900
_EXIT_MS = 320


class SplashScreen:
	"""Covers the window: pulsing "· — ·" logo, title, progress bar, status line."""

	def __init__(self, root: ctk.CTk) -> None:
		self.root = root
		self._started = time.monotonic()
		self._pulse: Animation | None = None
		self._pulse_forward = True
		colors = get_colors()

		self.frame = PatternBackdrop(root)
		self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)
		center = ctk.CTkFrame(self.frame, fg_color=colors.backdrop_bg, corner_radius=0)
		center.place(relx=0.5, rely=0.5, anchor="center")

		self.logo = make_label(center, "·  —  ·", font=font_mono(64), text_color=accent_color())
		self.logo.pack(pady=(0, 6))
		make_label(center, t("app.morsekoodi_oppimisprogramm"), font_size=30, weight="bold").pack()
		self.bar = make_progress_bar(center, root=root, width=360, height=8)
		self.bar.set_progress(0.0, animated=False)
		self.bar.pack(pady=(26, 10))
		self.status = make_label(
			center, t("splash.starting"), font=font_muted(), text_color=colors.text_muted
		)
		self.status.pack()
		self._start_pulse()

	def update(self, status: str, fraction: float) -> None:
		"""Show the next build step."""
		try:
			self.status.configure(text=status)
			self.bar.set_progress(fraction, duration_ms=200)
			self.root.update_idletasks()
		except TclError:
			pass

	def finish(self, on_done: Callable[[], None] | None = None) -> None:
		"""Wait the minimum time, then slide the splash up and away."""
		elapsed_ms = (time.monotonic() - self._started) * 1000
		wait = max(0, int(MIN_VISIBLE_MS - elapsed_ms)) if ANIMATIONS_ENABLED else 0
		self.root.after(wait, lambda: self._slide_out(on_done))

	def _slide_out(self, on_done: Callable[[], None] | None) -> None:
		if self._pulse is not None:
			self._pulse.cancel()
		try:
			# Canvas.lift() means "raise canvas items"; raise the widget itself.
			tkinter.Misc.tkraise(self.frame)
		except TclError:
			return

		def done() -> None:
			try:
				self.frame.destroy()
			except TclError:
				pass
			if on_done:
				on_done()

		animate(
			self.frame,
			_EXIT_MS,
			lambda p: self.frame.place_configure(rely=-p),
			done,
			easing=ease_in_out,
		)

	def _start_pulse(self) -> None:
		"""Gently fade the logo between muted and accent while loading."""
		colors = get_colors()
		start, end = colors.text_muted, accent_color()
		if not self._pulse_forward:
			start, end = end, start
		self._pulse_forward = not self._pulse_forward
		if not ANIMATIONS_ENABLED:
			return
		self._pulse = animate(
			self.logo,
			_PULSE_MS,
			lambda p: self.logo.configure(text_color=blend(start, end, p)),
			self._start_pulse,
			easing=ease_in_out,
		)


def fade_in_window(root: ctk.CTk, duration_ms: int = 260) -> None:
	"""Fade the whole window in where the platform supports window alpha."""
	try:
		root.attributes("-alpha", 0.0)
	except TclError:
		return

	def step(p: float) -> None:
		try:
			root.attributes("-alpha", p)
		except TclError:
			pass

	animate(root, duration_ms, step, easing=ease_in_out)


__all__ = ["MIN_VISIBLE_MS", "SplashScreen", "fade_in_window"]
