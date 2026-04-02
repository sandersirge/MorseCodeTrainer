"""Shared styling constants for the modern CustomTkinter UI.

Supports light and dark themes with a unified API. Use get_colors() to retrieve
current theme colors, or access the module-level constants for backwards compat.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeColors:
	"""Color palette for a single theme mode."""

	backdrop_bg: str
	card_bg: str
	card_border: str
	section_bg: str
	text_primary: str
	text_muted: str
	text_placeholder: str
	text_dark: str
	success_text: str
	error_text: str
	entry_bg: str
	entry_border: str
	focus_ring: str


# ---------------------------------------------------------------------------
# Theme Palettes
# ---------------------------------------------------------------------------

DARK_THEME = ThemeColors(
	backdrop_bg="#0b1120",
	card_bg="#111c2f",
	card_border="#1f2a44",
	section_bg="#0f172a",
	text_primary="#f8fafc",
	text_muted="#cbd5f5",
	text_placeholder="#94a3b8",
	text_dark="#0f172a",
	success_text="#22c55e",
	error_text="#f87171",
	entry_bg="#1e293b",
	entry_border="#334155",
	focus_ring="#3b82f6",
)

LIGHT_THEME = ThemeColors(
	backdrop_bg="#f1f5f9",
	card_bg="#ffffff",
	card_border="#e2e8f0",
	section_bg="#f8fafc",
	text_primary="#0f172a",
	text_muted="#1e293b",
	text_placeholder="#94a3b8",
	text_dark="#0f172a",
	success_text="#16a34a",
	error_text="#dc2626",
	entry_bg="#ffffff",
	entry_border="#cbd5e1",
	focus_ring="#2563eb",
)

# ---------------------------------------------------------------------------
# Theme State Management
# ---------------------------------------------------------------------------

_current_mode: str = "dark"
_theme_change_callbacks: list[Callable[[], None]] = []


def get_appearance_mode() -> str:
	"""Return the current appearance mode ('light' or 'dark')."""
	return _current_mode


def set_appearance_mode(mode: str) -> None:
	"""Set the appearance mode and notify listeners.

	Args:
		mode: Either 'light' or 'dark'
	"""
	global _current_mode
	normalized = mode.lower()
	if normalized not in ("light", "dark"):
		normalized = "dark"
	if normalized == _current_mode:
		return  # No change needed
	_current_mode = normalized
	# Note: We skip ctk.set_appearance_mode() here to avoid the flicker caused
	# by CustomTkinter's internal widget re-rendering. Since we manually apply
	# all colors via _apply_colors() callbacks, CTK's mode change is redundant.
	# Notify all registered callbacks to apply our custom colors
	for callback in _theme_change_callbacks:
		try:
			callback()
		except Exception:
			pass


def toggle_appearance_mode() -> str:
	"""Toggle between light and dark mode. Returns the new mode."""
	new_mode = "light" if _current_mode == "dark" else "dark"
	set_appearance_mode(new_mode)
	return new_mode


def register_theme_callback(callback: Callable[[], None]) -> None:
	"""Register a callback to be notified when theme changes."""
	if callback not in _theme_change_callbacks:
		_theme_change_callbacks.append(callback)


def unregister_theme_callback(callback: Callable[[], None]) -> None:
	"""Remove a theme change callback."""
	if callback in _theme_change_callbacks:
		_theme_change_callbacks.remove(callback)


def get_colors() -> ThemeColors:
	"""Return the current theme's color palette."""
	return LIGHT_THEME if _current_mode == "light" else DARK_THEME


# ---------------------------------------------------------------------------
# Font Families
# ---------------------------------------------------------------------------
FONT_FAMILY_DEFAULT = "Segoe UI"
FONT_FAMILY_SEMIBOLD = "Segoe UI Semibold"
FONT_FAMILY_MONO = "Consolas"
FONT_FAMILY_MONO_ALT = "JetBrains Mono"

# ---------------------------------------------------------------------------
# Font Sizes
# ---------------------------------------------------------------------------
FONT_SIZE_XS = 14
FONT_SIZE_SM = 16
FONT_SIZE_MD = 18
FONT_SIZE_LG = 20
FONT_SIZE_XL = 22
FONT_SIZE_2XL = 26
FONT_SIZE_3XL = 30
FONT_SIZE_4XL = 34
FONT_SIZE_5XL = 44
FONT_SIZE_DISPLAY = 78
