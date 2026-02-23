"""Factory helpers for constructing CustomTkinter widgets with shared styles."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import customtkinter as ctk

from .theme import (
	FONT_FAMILY_DEFAULT,
	FONT_FAMILY_MONO,
	FONT_FAMILY_MONO_ALT,
	FONT_FAMILY_SEMIBOLD,
	FONT_SIZE_4XL,
	FONT_SIZE_LG,
	FONT_SIZE_MD,
	FONT_SIZE_SM,
	FONT_SIZE_XL,
	SURFACE_ACCENT,
	SURFACE_DARK,
	SURFACE_LIGHT,
	TEXT_DARK,
	TEXT_MUTED,
	TEXT_PRIMARY,
)


# ---------------------------------------------------------------------------
# Shared styling tokens (deprecated - use theme.py constants)

DEFAULT_FONT_FAMILY = FONT_FAMILY_DEFAULT


@dataclass(frozen=True)
class ButtonStyle:
	fg_color: str
	hover_color: str
	text_color: str


BUTTON_STYLES: dict[str, ButtonStyle] = {
	"primary": ButtonStyle("#2563eb", "#1d4ed8", TEXT_PRIMARY),
	"secondary": ButtonStyle("#0ea5e9", "#0284c7", TEXT_DARK),
	"muted": ButtonStyle("#1e293b", "#141f33", "#e2e8f0"),
	"danger": ButtonStyle("#dc2626", "#b91c1c", TEXT_PRIMARY),
	"positive": ButtonStyle("#22c55e", "#16a34a", "#052e16"),
	"ghost": ButtonStyle("transparent", "#1e293b", TEXT_PRIMARY),
}


# ---------------------------------------------------------------------------
# Font utilities


def make_font(*, size: int, weight: str = "normal", family: str = FONT_FAMILY_DEFAULT) -> ctk.CTkFont:
	"""Return a configured CTkFont with the shared defaults."""

	normalized = weight.lower()
	if normalized not in {"normal", "bold"}:
		if normalized in {"semibold", "demibold", "medium"}:
			normalized = "bold"
		elif normalized in {"light", "regular"}:
			normalized = "normal"
		else:
			normalized = "bold" if "bold" in normalized else "normal"

	return ctk.CTkFont(family=family, size=size, weight=normalized)


# ---------------------------------------------------------------------------
# Font presets - common font configurations used across views


def font_title() -> ctk.CTkFont:
	"""Large bold title font (size 34)."""
	return make_font(size=FONT_SIZE_4XL, weight="bold")


def font_subtitle() -> ctk.CTkFont:
	"""Subtitle font (size 20, bold)."""
	return make_font(size=FONT_SIZE_LG, weight="bold")


def font_body() -> ctk.CTkFont:
	"""Standard body text font (size 18)."""
	return make_font(size=FONT_SIZE_MD)


def font_muted() -> ctk.CTkFont:
	"""Smaller muted/hint text font (size 16)."""
	return make_font(size=FONT_SIZE_SM)


def font_button() -> ctk.CTkFont:
	"""Button text font (size 18, bold, semibold family)."""
	return make_font(size=FONT_SIZE_MD, weight="bold", family=FONT_FAMILY_SEMIBOLD)


def font_button_large() -> ctk.CTkFont:
	"""Large button text font (size 20, bold, semibold family)."""
	return make_font(size=FONT_SIZE_LG, weight="bold", family=FONT_FAMILY_SEMIBOLD)


def font_callout() -> ctk.CTkFont:
	"""Callout/emphasis font (size 22, bold, semibold family)."""
	return make_font(size=FONT_SIZE_XL, weight="bold", family=FONT_FAMILY_SEMIBOLD)


def font_mono(size: int = FONT_SIZE_4XL) -> ctk.CTkFont:
	"""Monospace font for morse/code display (Consolas, bold)."""
	return make_font(size=size, weight="bold", family=FONT_FAMILY_MONO)


def font_timer() -> ctk.CTkFont:
	"""Timer display font (size 24, bold, JetBrains Mono)."""
	return make_font(size=24, weight="bold", family=FONT_FAMILY_MONO_ALT)


# ---------------------------------------------------------------------------
# Widget factories


def make_label(
	parent,
	text: str,
	*,
	font_size: int = 18,
	weight: str = "normal",
	font: ctk.CTkFont | None = None,
	text_color: str = TEXT_PRIMARY,
	wraplength: int | None = None,
	justify: str = "center",
	**options,
) -> ctk.CTkLabel:
	"""Create a CTkLabel using the shared typography and colour tokens."""

	label = ctk.CTkLabel(
		parent,
		text=text,
		font=font or make_font(size=font_size, weight=weight),
		text_color=text_color,
		justify=justify,
		**options,
	)
	if wraplength is not None:
		label.configure(wraplength=wraplength)
	return label


def make_button(
	parent,
	text: str,
	*,
	command: Callable[[], None],
	font_size: int = 18,
	weight: str = "bold",
	font: ctk.CTkFont | None = None,
	variant: str = "primary",
	width: int = 200,
	height: int = 44,
	corner_radius: int = 12,
	**options,
) -> ctk.CTkButton:
	"""Create a CTkButton with palette-driven variants (primary, danger, etc.)."""

	style = BUTTON_STYLES.get(variant, BUTTON_STYLES["primary"])
	return ctk.CTkButton(
		parent,
		text=text,
		command=command,
		font=font or make_font(size=font_size, weight=weight),
		fg_color=style.fg_color,
		hover_color=style.hover_color,
		text_color=style.text_color,
		width=width,
		height=height,
		corner_radius=corner_radius,
		**options,
	)


def make_entry(
	parent,
	*,
	font_size: int = 20,
	weight: str = "bold",
	font: ctk.CTkFont | None = None,
	width: int = 320,
	corner_radius: int = 10,
	placeholder_text: str | None = None,
	**options,
) -> ctk.CTkEntry:
	"""Create a CTkEntry with consistent typography and rounded corners."""

	entry = ctk.CTkEntry(
		parent,
		font=font or make_font(size=font_size, weight=weight),
		width=width,
		corner_radius=corner_radius,
		**options,
	)
	if placeholder_text is not None:
		entry.configure(placeholder_text=placeholder_text)
	return entry


def make_frame(
	parent,
	*,
	fg_color: str = "transparent",
	corner_radius: int = 0,
	border_width: int = 0,
	border_color: str | None = None,
	**options,
) -> ctk.CTkFrame:
	"""Create a CTkFrame wrapper with optional border and background tweaks."""

	cfg: dict[str, object] = {
		"fg_color": fg_color,
		"corner_radius": corner_radius,
		"border_width": border_width,
		**options,
	}
	if border_color is not None:
		cfg["border_color"] = border_color
	return ctk.CTkFrame(parent, **cfg)


def make_card(
	parent,
	*,
	corner_radius: int = 28,
	border_width: int = 1,
	fg_color: str = SURFACE_DARK,
	border_color: str = SURFACE_ACCENT,
	**options,
) -> ctk.CTkFrame:
	"""Create a elevated card-style frame used across the modern screens."""

	return make_frame(
		parent,
		fg_color=fg_color,
		corner_radius=corner_radius,
		border_width=border_width,
		border_color=border_color,
		**options,
	)


def make_progress_bar(
	parent,
	*,
	root,
	width: int | None = None,
	height: int = 12,
	fg_color: str | None = None,
	progress_color: str = BUTTON_STYLES["primary"].fg_color,
	corner_radius: int | None = None,
) -> ctk.CTkProgressBar:
	"""Create a CTkProgressBar with shared animation helpers bound to the widget."""

	bar = ctk.CTkProgressBar(
		parent,
		width=width,
		height=height,
		fg_color=fg_color,
		progress_color=progress_color,
	)
	if corner_radius is not None:
		bar.configure(corner_radius=corner_radius)

	state = {"job": None, "value": 0.0}

	def cancel_animation() -> None:
		job = state["job"]
		if job is not None:
			root.after_cancel(job)
			state["job"] = None

	def set_immediate(value: float) -> None:
		cancel_animation()
		clamped = max(0.0, min(1.0, value))
		bar.set(clamped)
		state["value"] = clamped

	def animate_to(target: float, *, duration_ms: int = 280) -> None:
		clamped_target = max(0.0, min(1.0, target))
		start = state["value"]
		if abs(clamped_target - start) < 1e-3:
			set_immediate(clamped_target)
			return

		cancel_animation()

		steps = max(1, duration_ms // 16)
		delta = (clamped_target - start) / steps

		def step(index: int = 1) -> None:
			if not bar.winfo_exists():
				state["job"] = None
				return

			new_value = start + delta * index
			finished = (
				(delta >= 0 and new_value >= clamped_target)
				or (delta < 0 and new_value <= clamped_target)
				or index >= steps
			)

			if finished:
				bar.set(clamped_target)
				state["value"] = clamped_target
				state["job"] = None
				return

			bar.set(new_value)
			state["value"] = new_value
			state["job"] = root.after(16, step, index + 1)

		step()

	def set_progress(value: float, *, animated: bool = True, duration_ms: int = 280) -> None:
		if animated:
			animate_to(value, duration_ms=duration_ms)
		else:
			set_immediate(value)

	bar.set_progress = set_progress  # type: ignore[attr-defined]
	bar.cancel_animation = cancel_animation  # type: ignore[attr-defined]
	bar.set_progress_immediate = set_immediate  # type: ignore[attr-defined]
	return bar


__all__ = [
	"make_font",
	"make_label",
	"make_button",
	"make_entry",
	"make_frame",
	"make_card",
	"make_progress_bar",
	"BUTTON_STYLES",
	"ButtonStyle",
]
