"""Main-window sizing, scaling and icon handling for Windows, macOS and Linux.

The screens were designed for a 1920×1080 canvas with fixed font sizes. Rather
than opening a 1920×1080 window (bigger than most laptop screens, or than a
1080p screen at 125–150 % Windows scaling), the window opens at a size that
fits the screen, and every widget and font is scaled to match. Resizing or
maximising the window rescales the UI again, so it always fits.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import customtkinter as ctk

_log = logging.getLogger(__name__)

DESIGN_WIDTH = 1920
DESIGN_HEIGHT = 1080
MIN_SCALE = 0.45
MAX_SCALE = 1.6
# Leave room for the taskbar / dock / menu bar and window decorations.
_SCREEN_FILL = 0.9
# Wait until the user has stopped dragging before rescaling (rescaling briefly
# pins the window size, which would fight an ongoing resize).
_RESCALE_DELAY_MS = 400
_RESCALE_THRESHOLD = 0.04


def _icons_dir() -> Path:
	"""Icons live in <project>/resources/icons, or next to the PyInstaller bundle."""
	bundle = getattr(sys, "_MEIPASS", None)
	if bundle:
		return Path(bundle) / "resources" / "icons"
	return Path(__file__).resolve().parents[3] / "resources" / "icons"


def fit_scale(available_width: float, available_height: float) -> float:
	"""Scale factor that fits the design canvas into the given logical size."""
	scale = min(available_width / DESIGN_WIDTH, available_height / DESIGN_HEIGHT)
	return max(MIN_SCALE, min(MAX_SCALE, scale))


class MainWindow:
	"""Applies size, scaling and icon to the root window and keeps them in sync."""

	def __init__(self, root: ctk.CTk) -> None:
		self.root = root
		self._dpi_scale = 1.0
		self._ui_scale = 1.0
		self._pending: str | None = None

	def setup(self, title: str) -> None:
		self.root.title(title)
		self._dpi_scale = self._detect_dpi_scale()
		self._set_icon()

		screen_w = self.root.winfo_screenwidth() / self._dpi_scale
		screen_h = self.root.winfo_screenheight() / self._dpi_scale
		# Start at a size that fits the screen, but never larger than the design.
		scale = min(1.0, fit_scale(screen_w * _SCREEN_FILL, screen_h * _SCREEN_FILL))
		width = int(DESIGN_WIDTH * scale)
		height = int(DESIGN_HEIGHT * scale)
		x = max(0, int((screen_w - width) / 2))
		y = max(0, int((screen_h - height) / 3))
		# Order matters: CustomTkinter pins the window to its *current* size for
		# about a second whenever the scaling changes, so set the size first.
		self.root.minsize(int(DESIGN_WIDTH * MIN_SCALE), int(DESIGN_HEIGHT * MIN_SCALE))
		self.root.geometry(f"{width}x{height}+{x}+{y}")
		self._apply_ui_scale(scale)
		self.root.bind("<Configure>", self._on_configure, add="+")

	@property
	def ui_scale(self) -> float:
		return self._ui_scale

	# Scaling -------------------------------------------------------------

	def _detect_dpi_scale(self) -> float:
		"""Pixels per logical pixel.

		CustomTkinter detects this itself on Windows and macOS. On Linux it
		always assumes 96 DPI, so HiDPI screens get tiny text; there we read
		the X server's DPI and tell CustomTkinter about it.
		"""
		if sys.platform.startswith("linux"):
			try:
				dpi = float(self.root.winfo_fpixels("1i"))
			except Exception:
				dpi = 96.0
			scale = max(1.0, round(dpi / 96.0 * 4) / 4)  # snap to 0.25 steps
			if scale > 1.0:
				ctk.set_window_scaling(scale)
			return scale
		try:
			from customtkinter.windows.widgets.scaling import ScalingTracker

			return float(ScalingTracker.get_window_scaling(self.root))
		except Exception:
			return 1.0

	def _apply_ui_scale(self, scale: float) -> None:
		self._ui_scale = scale
		# On Linux the DPI factor is not applied automatically, so include it.
		dpi_part = self._dpi_scale if sys.platform.startswith("linux") else 1.0
		ctk.set_widget_scaling(scale * dpi_part)

	def _on_configure(self, event) -> None:
		if event.widget is not self.root:
			return
		if self._pending is not None:
			self.root.after_cancel(self._pending)
		self._pending = self.root.after(_RESCALE_DELAY_MS, self._rescale_to_window)

	def _rescale_to_window(self) -> None:
		self._pending = None
		width = self.root.winfo_width() / self._dpi_scale
		height = self.root.winfo_height() / self._dpi_scale
		if width < 50 or height < 50:  # minimised / not mapped yet
			return
		scale = fit_scale(width, height)
		if abs(scale - self._ui_scale) >= _RESCALE_THRESHOLD:
			self._apply_ui_scale(scale)

	# Icon ----------------------------------------------------------------

	def _set_icon(self) -> None:
		icons = _icons_dir()
		try:
			if sys.platform == "win32" and (icons / "morsetrainer.ico").is_file():
				# Also stops CustomTkinter from replacing it with its own icon.
				self.root.iconbitmap(str(icons / "morsetrainer.ico"))
				return
			png = icons / "morsetrainer-256.png"
			if png.is_file():
				# Tk 8.6 reads PNG natively; used by Linux window managers and the macOS dock.
				import tkinter as tk

				self._photo = tk.PhotoImage(file=str(png))  # keep a reference alive
				self.root.iconphoto(True, self._photo)
		except Exception:
			_log.debug("Could not set window icon", exc_info=True)


__all__ = ["DESIGN_HEIGHT", "DESIGN_WIDTH", "MainWindow", "fit_scale"]
