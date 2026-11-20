"""Tests for window fitting maths (no real Tk window needed)."""

import pytest

from src.main.python.views.window import (
	DESIGN_HEIGHT,
	DESIGN_WIDTH,
	MAX_SCALE,
	MIN_SCALE,
	fit_scale,
)


class TestFitScale:
	def test_design_size_is_scale_one(self):
		assert fit_scale(DESIGN_WIDTH, DESIGN_HEIGHT) == pytest.approx(1.0)

	@pytest.mark.parametrize(
		("width", "height", "expected"),
		[
			(1366 * 0.9, 768 * 0.9, 0.64),  # common laptop
			(1280, 720, 0.6667),  # 1080p at 150 % Windows scaling
			(1728, 972, 0.9),
		],
	)
	def test_small_screens_scale_down(self, width, height, expected):
		assert fit_scale(width, height) == pytest.approx(expected, rel=0.01)

	def test_limited_by_tighter_dimension(self):
		# Very wide but short window: height decides
		assert fit_scale(3000, 540) == pytest.approx(0.5)

	def test_clamped(self):
		assert fit_scale(100, 100) == MIN_SCALE
		assert fit_scale(10000, 10000) == MAX_SCALE
