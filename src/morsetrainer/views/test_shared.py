from __future__ import annotations

import customtkinter as ctk

from .backdrop import PatternBackdrop, make_backdrop


def prepare_backdrop(root: ctk.CTk) -> PatternBackdrop:
	"""Full-size patterned backdrop (kept for older call sites; see ``make_page``)."""
	return make_backdrop(root)
