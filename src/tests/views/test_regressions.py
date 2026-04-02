"""Regression tests for bugs that have been fixed.

Each test documents a specific bug that was resolved and ensures
it cannot silently reappear.
"""

import pytest

from src.main.python.views.theme import (
	DARK_THEME,
	LIGHT_THEME,
	get_colors,
	set_appearance_mode,
)
from src.main.python.views.widgets import get_button_style


@pytest.fixture(autouse=True)
def _reset_theme():
	set_appearance_mode("dark")
	yield
	set_appearance_mode("dark")


class TestRegressionStaticThemeConstants:
	"""regression: static module-level colour constants were frozen to dark mode.

	Files that imported TEXT_PRIMARY, ERROR_TEXT, SURFACE_DARK etc. from
	theme.py always received the dark-theme value, even when the user had
	switched to light mode. Fixed by removing all static colour constants
	and replacing with get_colors() calls.
	"""

	def test_get_colors_returns_light_palette_in_light_mode(self):
		set_appearance_mode("light")
		colors = get_colors()
		assert colors.text_primary == LIGHT_THEME.text_primary
		assert colors.error_text == LIGHT_THEME.error_text

	def test_get_colors_returns_dark_palette_in_dark_mode(self):
		colors = get_colors()
		assert colors.text_primary == DARK_THEME.text_primary
		assert colors.error_text == DARK_THEME.error_text


class TestRegressionMutedButtonInLightMode:
	"""regression: muted button variant was invisible in light mode.

	BUTTON_STYLES["muted"] used hardcoded dark-mode colours (#1e293b bg,
	#141f33 hover) that were nearly invisible on light backgrounds. Fixed
	by converting to get_button_style() which reads colors.entry_bg and
	colors.entry_border dynamically.
	"""

	def test_muted_bg_is_visible_in_light_mode(self):
		set_appearance_mode("light")
		style = get_button_style("muted")
		# Light mode entry_bg should be a light colour, not the dark #1e293b
		assert style.fg_color == LIGHT_THEME.entry_bg
		assert style.fg_color != "#1e293b"

	def test_muted_hover_is_visible_in_light_mode(self):
		set_appearance_mode("light")
		style = get_button_style("muted")
		assert style.hover_color == LIGHT_THEME.entry_border
		assert style.hover_color != "#141f33"


class TestRegressionErrorTextThemeAware:
	"""regression: error text colour was hardcoded to dark-mode red (#f87171).

	translation_section.py used ERROR_TEXT (static constant = "#f87171")
	for error labels. In light mode the correct red is #dc2626. Fixed by
	using get_colors().error_text at point of use.
	"""

	def test_error_text_differs_between_themes(self):
		dark_error = get_colors().error_text
		set_appearance_mode("light")
		light_error = get_colors().error_text
		assert dark_error != light_error
		assert dark_error == DARK_THEME.error_text
		assert light_error == LIGHT_THEME.error_text


class TestRegressionNoStaticColorExports:
	"""regression: theme.py must not export backwards-compat colour constants.

	The static constants block (BACKDROP_BG, CARD_BG, TEXT_PRIMARY, etc.)
	was a constant source of light-mode bugs. It has been removed entirely.
	Only font constants remain as module-level exports.
	"""

	def test_no_static_colour_constants_exported(self):
		import src.main.python.views.theme as theme_module

		removed_names = [
			"BACKDROP_BG",
			"CARD_BG",
			"CARD_BORDER",
			"SECTION_BG",
			"SURFACE_DARK",
			"SURFACE_LIGHT",
			"SURFACE_ACCENT",
			"TEXT_PRIMARY",
			"TEXT_MUTED",
			"TEXT_PLACEHOLDER",
			"TEXT_DARK",
			"SUCCESS_TEXT",
			"ERROR_TEXT",
		]
		for name in removed_names:
			assert not hasattr(theme_module, name), (
				f"theme.py still exports {name!r} — static colour constants "
				"should be replaced with get_colors()"
			)

	def test_font_constants_still_exported(self):
		import src.main.python.views.theme as theme_module

		assert hasattr(theme_module, "FONT_FAMILY_DEFAULT")
		assert hasattr(theme_module, "FONT_SIZE_MD")


class TestRegressionGhostVariantRemoved:
	"""regression: ghost button variant existed but had zero call sites.

	It was dead code using hardcoded dark-mode colours. Removed from
	get_button_style(). Requesting 'ghost' should fall back to 'primary'.
	"""

	def test_ghost_falls_back_to_primary(self):
		ghost = get_button_style("ghost")
		primary = get_button_style("primary")
		assert ghost == primary
