from __future__ import annotations

from tkinter import TclError

import customtkinter as ctk

from .theme import get_colors
from .widgets import make_frame


def prepare_backdrop(root: ctk.CTk) -> ctk.CTkFrame:
	"""Set up a full-size backdrop frame with the shared background colour."""
	colors = get_colors()

	try:
		root.configure(fg_color=colors.backdrop_bg)
	except TclError:
		try:
			root.configure(bg=colors.backdrop_bg)
		except TclError:
			pass
	backdrop = make_frame(root, fg_color=colors.backdrop_bg)
	backdrop.pack(fill="both", expand=True)
	return backdrop
