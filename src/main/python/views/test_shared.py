from __future__ import annotations

from tkinter import TclError

import customtkinter as ctk

from .theme import BACKDROP_BG
from .widgets import make_frame


def prepare_backdrop(root: ctk.CTk) -> ctk.CTkFrame:
    """Set up a full-size backdrop frame with the shared background colour."""

    try:
        root.configure(fg_color=BACKDROP_BG)
    except TclError:
        try:
            root.configure(bg=BACKDROP_BG)
        except TclError:
            pass
    backdrop = make_frame(root, fg_color=BACKDROP_BG)
    backdrop.pack(fill="both", expand=True)
    return backdrop
