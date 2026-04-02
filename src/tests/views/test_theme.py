"""Tests for theme state management and colour resolution."""

import pytest

from src.main.python.views.theme import (
	DARK_THEME,
	LIGHT_THEME,
	ThemeColors,
	get_appearance_mode,
	get_colors,
	register_theme_callback,
	set_appearance_mode,
	toggle_appearance_mode,
	unregister_theme_callback,
)


@pytest.fixture(autouse=True)
def _reset_theme():
	"""Ensure every test starts with dark mode and clean callbacks."""
	set_appearance_mode("dark")
	yield
	set_appearance_mode("dark")


class TestThemeColors:
	"""ThemeColors dataclass invariants."""

	def test_dark_theme_is_frozen(self):
		with pytest.raises(AttributeError):
			DARK_THEME.backdrop_bg = "#000000"

	def test_light_theme_is_frozen(self):
		with pytest.raises(AttributeError):
			LIGHT_THEME.card_bg = "#ffffff"

	def test_dark_theme_has_all_fields(self):
		assert isinstance(DARK_THEME, ThemeColors)
		for field in ThemeColors.__dataclass_fields__:
			assert isinstance(getattr(DARK_THEME, field), str)

	def test_light_theme_has_all_fields(self):
		assert isinstance(LIGHT_THEME, ThemeColors)
		for field in ThemeColors.__dataclass_fields__:
			assert isinstance(getattr(LIGHT_THEME, field), str)

	def test_dark_and_light_differ(self):
		assert DARK_THEME.backdrop_bg != LIGHT_THEME.backdrop_bg
		assert DARK_THEME.card_bg != LIGHT_THEME.card_bg
		assert DARK_THEME.text_primary != LIGHT_THEME.text_primary

	def test_error_text_differs_between_themes(self):
		assert DARK_THEME.error_text != LIGHT_THEME.error_text


class TestGetAppearanceMode:
	def test_default_is_dark(self):
		assert get_appearance_mode() == "dark"

	def test_returns_light_after_set(self):
		set_appearance_mode("light")
		assert get_appearance_mode() == "light"


class TestSetAppearanceMode:
	def test_set_light(self):
		set_appearance_mode("light")
		assert get_appearance_mode() == "light"

	def test_set_dark(self):
		set_appearance_mode("light")
		set_appearance_mode("dark")
		assert get_appearance_mode() == "dark"

	def test_unknown_mode_defaults_to_dark(self):
		set_appearance_mode("neon")
		assert get_appearance_mode() == "dark"

	def test_case_insensitive(self):
		set_appearance_mode("LIGHT")
		assert get_appearance_mode() == "light"

	def test_same_mode_is_noop(self):
		calls = []

		def cb():
			calls.append(1)

		register_theme_callback(cb)
		set_appearance_mode("dark")  # already dark
		assert len(calls) == 0
		unregister_theme_callback(cb)

	def test_change_triggers_callbacks(self):
		calls = []

		def cb():
			calls.append("called")

		register_theme_callback(cb)
		set_appearance_mode("light")
		assert calls == ["called"]
		unregister_theme_callback(cb)


class TestToggleAppearanceMode:
	def test_toggle_from_dark_to_light(self):
		result = toggle_appearance_mode()
		assert result == "light"
		assert get_appearance_mode() == "light"

	def test_toggle_from_light_to_dark(self):
		set_appearance_mode("light")
		result = toggle_appearance_mode()
		assert result == "dark"
		assert get_appearance_mode() == "dark"

	def test_double_toggle_returns_to_original(self):
		toggle_appearance_mode()
		toggle_appearance_mode()
		assert get_appearance_mode() == "dark"


class TestGetColors:
	def test_dark_returns_dark_theme(self):
		assert get_colors() is DARK_THEME

	def test_light_returns_light_theme(self):
		set_appearance_mode("light")
		assert get_colors() is LIGHT_THEME

	def test_returns_current_theme_after_toggle(self):
		toggle_appearance_mode()
		assert get_colors() is LIGHT_THEME
		toggle_appearance_mode()
		assert get_colors() is DARK_THEME


class TestThemeCallbacks:
	def test_register_and_fire(self):
		results = []

		def cb():
			results.append("fired")

		register_theme_callback(cb)
		set_appearance_mode("light")
		assert results == ["fired"]
		unregister_theme_callback(cb)

	def test_unregister_prevents_fire(self):
		results = []

		def cb():
			results.append("fired")

		register_theme_callback(cb)
		unregister_theme_callback(cb)
		set_appearance_mode("light")
		assert results == []

	def test_duplicate_register_fires_once(self):
		results = []

		def cb():
			results.append(1)

		register_theme_callback(cb)
		register_theme_callback(cb)
		set_appearance_mode("light")
		assert results == [1]
		unregister_theme_callback(cb)

	def test_unregister_nonexistent_is_safe(self):
		unregister_theme_callback(lambda: None)  # should not raise

	def test_callback_exception_does_not_block_others(self):
		results = []

		def bad_callback():
			raise RuntimeError("boom")

		def good_callback():
			results.append("ok")

		register_theme_callback(bad_callback)
		register_theme_callback(good_callback)
		set_appearance_mode("light")
		assert results == ["ok"]
		unregister_theme_callback(bad_callback)
		unregister_theme_callback(good_callback)
