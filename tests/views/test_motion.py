"""Tests for the animation helpers, button styles, backdrop colour and slide direction."""

import pytest

from morsetrainer.view_stack import slide_direction
from morsetrainer.views import motion
from morsetrainer.views.backdrop import PATTERN_STRENGTH, pattern_color
from morsetrainer.views.theme import DARK_THEME, LIGHT_THEME, set_appearance_mode
from morsetrainer.views.widgets import BUTTON_SIZES, get_button_style, is_morse_text, pretty_morse


class TestEasing:
	@pytest.mark.parametrize("ease", [motion.ease_out_cubic, motion.ease_in_out])
	def test_endpoints(self, ease):
		assert ease(0.0) == 0.0
		assert ease(1.0) == 1.0

	@pytest.mark.parametrize("ease", [motion.ease_out_cubic, motion.ease_in_out])
	def test_clamped(self, ease):
		assert ease(-1) == 0.0
		assert ease(2) == 1.0

	def test_ease_out_is_fast_at_start(self):
		assert motion.ease_out_cubic(0.5) > 0.5


class TestBlend:
	def test_endpoints(self):
		assert motion.blend("#000000", "#ffffff", 0) == "#000000"
		assert motion.blend("#000000", "#ffffff", 1) == "#ffffff"

	def test_midpoint(self):
		assert motion.blend("#000000", "#ffffff", 0.5) == "#808080"

	def test_short_hex(self):
		assert motion.blend("#000", "#fff", 1) == "#ffffff"


class FakeWidget:
	"""Minimal stand-in for a Tk widget with a controllable clock."""

	def __init__(self):
		self.jobs = []
		self.alive = True
		self.cancelled = []

	def after(self, _ms, func):
		self.jobs.append(func)
		return f"job{len(self.jobs)}"

	def after_cancel(self, job):
		self.cancelled.append(job)

	def winfo_exists(self):
		return self.alive

	def run_pending(self):
		jobs, self.jobs = self.jobs, []
		for job in jobs:
			job()


@pytest.fixture
def animations_on(monkeypatch):
	monkeypatch.setattr(motion, "ANIMATIONS_ENABLED", True)


class TestAnimate:
	def test_runs_to_completion(self, animations_on):
		widget, now, steps, done = FakeWidget(), [0.0], [], []
		motion.animate(widget, 100, steps.append, lambda: done.append(True), clock=lambda: now[0])
		for t in (0.05, 0.1):
			now[0] = t
			widget.run_pending()
		assert steps[0] == 0.0
		assert steps[-1] == 1.0
		assert done == [True]
		assert steps == sorted(steps)

	def test_cancel_stops_without_on_done(self, animations_on):
		widget, now, done = FakeWidget(), [0.0], []
		animation = motion.animate(
			widget, 100, lambda _p: None, lambda: done.append(True), clock=lambda: now[0]
		)
		animation.cancel()
		now[0] = 1.0
		widget.run_pending()
		assert done == []
		assert animation.finished

	def test_stops_when_widget_destroyed(self, animations_on):
		widget, now, steps = FakeWidget(), [0.0], []
		motion.animate(widget, 100, steps.append, clock=lambda: now[0])
		widget.alive = False
		now[0] = 0.05
		widget.run_pending()
		assert steps == [0.0]

	def test_disabled_jumps_to_end(self, monkeypatch):
		monkeypatch.setattr(motion, "ANIMATIONS_ENABLED", False)
		steps, done = [], []
		motion.animate(FakeWidget(), 500, steps.append, lambda: done.append(True))
		assert steps == [1.0] and done == [True]


class TestButtonStyles:
	@pytest.mark.parametrize("mode", ["dark", "light"])
	def test_outline_variants_have_borders(self, mode):
		set_appearance_mode(mode)
		try:
			for variant in ("secondary", "danger"):
				style = get_button_style(variant)
				assert style.fg_color == "transparent"
				assert style.border_width == 2 and style.border_color
			ghost = get_button_style("ghost")
			assert ghost.fg_color == "transparent" and ghost.border_width == 0
		finally:
			set_appearance_mode("dark")

	def test_filled_buttons_use_white_text(self):
		for variant in ("primary", "positive"):
			assert get_button_style(variant).text_color == "#ffffff"

	def test_hover_differs_from_rest(self):
		for variant in ("primary", "positive", "secondary", "danger", "ghost", "muted"):
			style = get_button_style(variant)
			assert style.hover_color and style.hover_color != style.fg_color

	def test_sizes_are_ordered(self):
		heights = [BUTTON_SIZES[s][0] for s in ("sm", "md", "lg")]
		assert heights == sorted(heights)


class TestBackdrop:
	def test_pattern_is_close_to_background(self):
		color = pattern_color(DARK_THEME.backdrop_bg, DARK_THEME.text_primary)
		assert color != DARK_THEME.backdrop_bg
		assert color == motion.blend(
			DARK_THEME.backdrop_bg, DARK_THEME.text_primary, PATTERN_STRENGTH
		)

	def test_light_theme_pattern_is_darker_than_background(self):
		color = pattern_color(LIGHT_THEME.backdrop_bg, LIGHT_THEME.text_primary)
		assert int(color[1:3], 16) < int(LIGHT_THEME.backdrop_bg[1:3], 16)


class TestSlideDirection:
	def test_first_screen_does_not_slide(self):
		assert slide_direction(None, 0) == 0

	def test_deeper_slides_from_right(self):
		assert slide_direction(0, 1) == 1
		assert slide_direction(1, 1) == 1

	def test_back_slides_from_left(self):
		assert slide_direction(2, 0) == -1


NB = " "


class TestPrettyMorse:
	def test_glyphs_and_gaps(self):
		assert pretty_morse(".- -...") == f"•{NB}—{NB * 3}—{NB}•{NB}•{NB}•"

	def test_only_word_gaps_can_wrap(self):
		# Plain spaces (where a label may wrap) appear only between words.
		shown = pretty_morse(".- -...   -.-.")
		assert shown.count(" ") == 2
		assert shown.split("  ")[1] == f"—{NB}•{NB}—{NB}•"

	def test_line_breaks_kept(self):
		assert pretty_morse(".-\n-") == f"•{NB}—\n—"

	def test_non_morse_unchanged(self):
		assert pretty_morse("Tere") == "Tere"
		assert not is_morse_text("A .-")
