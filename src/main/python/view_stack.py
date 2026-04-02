"""Manages view-level frame visibility so navigation never destroys widgets."""

from __future__ import annotations

import customtkinter as ctk


class ViewStack:
	"""Keeps one CTkFrame per registered view; shows exactly one at a time."""

	def __init__(self, root: ctk.CTk) -> None:
		self._root = root
		self._frames: dict[str, ctk.CTkFrame] = {}
		self._active: str | None = None

	def register(self, name: str) -> ctk.CTkFrame:
		"""Create and return a full-size frame for *name*, initially hidden."""
		frame = ctk.CTkFrame(self._root, fg_color="transparent")
		self._frames[name] = frame
		return frame

	def show(self, name: str) -> None:
		"""Hide the current view and display *name*."""
		if self._active == name:
			return
		if self._active and self._active in self._frames:
			self._frames[self._active].pack_forget()
		self._frames[name].pack(fill="both", expand=True)
		self._active = name

	@property
	def active(self) -> str | None:
		return self._active
