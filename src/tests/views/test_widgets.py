"""Tests for widget helper functions (non-Tk logic only)."""

import pytest

from src.main.python.views.theme import (
	DARK_THEME,
	LIGHT_THEME,
	set_appearance_mode,
)
from src.main.python.views.widgets import ButtonStyle, get_button_style


@pytest.fixture(autouse=True)
def _reset_theme():
	"""Start each test in dark mode."""
	set_appearance_mode("dark")
	yield
	set_appearance_mode("dark")


class TestGetButtonStyle:
	"""get_button_style returns theme-aware ButtonStyle instances."""

	def test_returns_button_style(self):
		style = get_button_style("primary")
		assert isinstance(style, ButtonStyle)

	def test_unknown_variant_falls_back_to_primary(self):
		assert get_button_style("nonexistent") == get_button_style("primary")

	def test_default_variant_is_primary(self):
		assert get_button_style() == get_button_style("primary")

	@pytest.mark.parametrize("variant", ["primary", "secondary", "muted", "danger", "positive"])
	def test_all_variants_return_style(self, variant):
		style = get_button_style(variant)
		assert style.fg_color
		assert style.hover_color
		assert style.text_color

	def test_primary_text_is_theme_text_primary(self):
		style = get_button_style("primary")
		assert style.text_color == DARK_THEME.text_primary

	def test_primary_text_changes_with_theme(self):
		dark_style = get_button_style("primary")
		set_appearance_mode("light")
		light_style = get_button_style("primary")
		assert dark_style.text_color == DARK_THEME.text_primary
		assert light_style.text_color == LIGHT_THEME.text_primary

	def test_secondary_text_is_theme_text_dark(self):
		style = get_button_style("secondary")
		assert style.text_color == DARK_THEME.text_dark

	def test_muted_bg_changes_with_theme(self):
		dark_style = get_button_style("muted")
		set_appearance_mode("light")
		light_style = get_button_style("muted")
		assert dark_style.fg_color == DARK_THEME.entry_bg
		assert light_style.fg_color == LIGHT_THEME.entry_bg
		assert dark_style.fg_color != light_style.fg_color

	def test_muted_hover_changes_with_theme(self):
		dark_style = get_button_style("muted")
		set_appearance_mode("light")
		light_style = get_button_style("muted")
		assert dark_style.hover_color == DARK_THEME.entry_border
		assert light_style.hover_color == LIGHT_THEME.entry_border

	def test_danger_text_is_theme_text_primary(self):
		style = get_button_style("danger")
		assert style.text_color == DARK_THEME.text_primary

	def test_positive_is_theme_independent(self):
		dark_style = get_button_style("positive")
		set_appearance_mode("light")
		light_style = get_button_style("positive")
		assert dark_style == light_style

	def test_ghost_variant_removed(self):
		"""ghost was dead code and should gracefully fall back to primary."""
		style = get_button_style("ghost")
		assert style == get_button_style("primary")


class TestButtonStyleDataclass:
	def test_frozen(self):
		style = ButtonStyle("#aaa", "#bbb", "#ccc")
		with pytest.raises(AttributeError):
			style.fg_color = "#000"

	def test_equality(self):
		a = ButtonStyle("#a", "#b", "#c")
		b = ButtonStyle("#a", "#b", "#c")
		assert a == b

	def test_inequality(self):
		a = ButtonStyle("#a", "#b", "#c")
		b = ButtonStyle("#x", "#b", "#c")
		assert a != b
