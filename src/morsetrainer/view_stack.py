"""Manages view-level frame visibility so navigation never destroys widgets."""

from __future__ import annotations

import customtkinter as ctk

from .views.motion import Animation, animate, ease_out_cubic

SLIDE_DISTANCE = 0.06  # share of the window width the new screen slides in from
SLIDE_MS = 200


def slide_direction(current_depth: int | None, new_depth: int) -> int:
	"""+1 = slide in from the right (going deeper), -1 = from the left (going back)."""
	if current_depth is None:
		return 0
	return 1 if new_depth >= current_depth else -1


class ViewStack:
	"""Keeps one CTkFrame per registered view; shows exactly one at a time.

	Each view has a *depth* in the menu tree (home 0, hubs 1, exercises 2...).
	Moving deeper slides the new screen in from the right; going back slides it
	in from the left. Frames are positioned with ``place`` so they can move.
	"""

	def __init__(self, root: ctk.CTk) -> None:
		self._root = root
		self._frames: dict[str, ctk.CTkFrame] = {}
		self._depths: dict[str, int] = {}
		self._active: str | None = None
		self._animation: Animation | None = None

	def register(self, name: str, depth: int = 1) -> ctk.CTkFrame:
		"""Create and return a full-size frame for *name*, initially hidden."""
		frame = ctk.CTkFrame(self._root, fg_color="transparent")
		self._frames[name] = frame
		self._depths[name] = depth
		return frame

	def show(self, name: str, *, animated: bool = True) -> None:
		"""Hide the current view and slide *name* into place."""
		if self._active == name:
			return
		direction = slide_direction(
			self._depths.get(self._active) if self._active else None, self._depths.get(name, 1)
		)
		if self._active and self._active in self._frames:
			self._frames[self._active].place_forget()
		frame = self._frames[name]
		self._active = name
		if self._animation is not None:
			self._animation.cancel()

		if not animated or direction == 0:
			frame.place(relx=0, rely=0, relwidth=1, relheight=1)
			return
		start = SLIDE_DISTANCE * direction
		frame.place(relx=start, rely=0, relwidth=1, relheight=1)
		frame.lift()
		# Draw the new screen once before the clock starts; the first paint of
		# fresh CTk widgets is the slow part and would otherwise eat the motion.
		try:
			frame.update_idletasks()
		except Exception:
			pass
		self._animation = animate(
			frame,
			SLIDE_MS,
			lambda p: frame.place_configure(relx=start * (1 - p)),
			easing=ease_out_cubic,
		)

	def depth(self, name: str) -> int:
		return self._depths.get(name, 1)

	@property
	def active(self) -> str | None:
		return self._active


__all__ = ["SLIDE_DISTANCE", "SLIDE_MS", "ViewStack", "slide_direction"]
