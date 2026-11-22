"""Window background: the theme colour with a faint scattering of Morse dots and dashes."""

from __future__ import annotations

import random
from tkinter import TclError

import customtkinter as ctk

from .motion import blend
from .theme import get_colors, register_theme_callback, unregister_theme_callback

PATTERN_STRENGTH = 0.06  # how far the pattern colour leans from background towards text
_CELL = 64  # px between pattern "words"
_FILL_CHANCE = 0.38  # share of cells that get a Morse word
_REDRAW_DELAY_MS = 80


def pattern_color(background: str, foreground: str, strength: float = PATTERN_STRENGTH) -> str:
	"""Colour that reads as *foreground* at low opacity on *background*."""
	return blend(background, foreground, strength)


class PatternBackdrop(ctk.CTkCanvas):
	"""Full-size canvas; place cards on it and the pattern shows around them.

	The layout of the pattern is seeded, so it stays the same between redraws
	(resizes and theme changes don't make it "jump").
	"""

	def __init__(self, master, *, seed: int = 7, **kwargs) -> None:
		colors = get_colors()
		super().__init__(master, highlightthickness=0, bd=0, bg=colors.backdrop_bg, **kwargs)
		self._seed = seed
		self._job: str | None = None
		self._size = (0, 0)
		self.bind("<Configure>", self._on_configure, add="+")
		self.bind("<Destroy>", self._on_destroy, add="+")
		register_theme_callback(self.redraw)

	def _on_configure(self, event) -> None:
		if (event.width, event.height) == self._size:
			return
		self._size = (event.width, event.height)
		if self._job is not None:
			self.after_cancel(self._job)
		self._job = self.after(_REDRAW_DELAY_MS, self.redraw)

	def _on_destroy(self, event) -> None:
		if event.widget is self:
			unregister_theme_callback(self.redraw)

	def redraw(self) -> None:
		self._job = None
		try:
			if not self.winfo_exists():
				return
			colors = get_colors()
			self.configure(bg=colors.backdrop_bg)
			self.delete("pattern")
			width, height = self.winfo_width(), self.winfo_height()
			if width < 2 or height < 2:
				return
			color = pattern_color(colors.backdrop_bg, colors.text_primary)
			rng = random.Random(self._seed)
			for y in range(_CELL // 2, height + _CELL, _CELL):
				for x in range(0, width + _CELL, _CELL):
					if rng.random() > _FILL_CHANCE:
						continue
					self._draw_word(x + rng.randint(-14, 14), y + rng.randint(-10, 10), rng, color)
			self.tag_lower("pattern")
		except TclError:
			pass

	def _draw_word(self, x: int, y: int, rng: random.Random, color: str) -> None:
		"""One short Morse 'word', e.g. ·–·, drawn left to right."""
		for _ in range(rng.randint(1, 4)):
			if rng.random() < 0.5:
				self.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color, outline="", tags="pattern")
				x += 12
			else:
				self.create_line(
					x - 3, y, x + 13, y, fill=color, width=5, capstyle="round", tags="pattern"
				)
				x += 24


def make_backdrop(root) -> PatternBackdrop:
	"""Create, pack and return the patterned background for a screen."""
	try:
		root.configure(fg_color=get_colors().backdrop_bg)
	except (TclError, ValueError):
		pass
	backdrop = PatternBackdrop(root)
	backdrop.pack(fill="both", expand=True)
	return backdrop


__all__ = ["PATTERN_STRENGTH", "PatternBackdrop", "make_backdrop", "pattern_color"]
