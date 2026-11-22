"""Factory helpers for constructing CustomTkinter widgets with shared styles."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import customtkinter as ctk

from .motion import Animation, animate, blend, tween_color
from .theme import (
	FONT_FAMILY_DEFAULT,
	FONT_SIZE_4XL,
	FONT_SIZE_LG,
	FONT_SIZE_MD,
	FONT_SIZE_SM,
	FONT_SIZE_XL,
	get_appearance_mode,
	get_colors,
	resolve_font_family,
)

# ---------------------------------------------------------------------------
# Shared styling tokens (deprecated - use theme.py constants)

DEFAULT_FONT_FAMILY = FONT_FAMILY_DEFAULT


@dataclass(frozen=True)
class ButtonStyle:
	"""Colours for one button variant.

	``fg_color`` may be ``"transparent"`` (outline and ghost buttons); hover
	then fades from the parent's background to ``hover_color``.
	"""

	fg_color: str
	hover_color: str
	text_color: str
	border_color: str | None = None
	border_width: int = 0


_FILLED_TEXT = "#ffffff"


def accent_color() -> str:
	"""Readable blue for outline buttons and links in the current theme."""
	return "#1d4ed8" if get_appearance_mode() == "light" else "#60a5fa"


def get_button_style(variant: str = "primary") -> ButtonStyle:
	"""Return a theme-aware ButtonStyle for the given variant.

	- primary / positive: filled, for the one main action of a screen
	- secondary: outline in the accent colour, for other actions
	- danger: outline in red, for destructive actions (stop, cancel)
	- ghost: text only, for navigation such as "← Avalehele"
	- muted: subtle filled, for low-emphasis toggles
	"""
	colors = get_colors()
	accent = accent_color()
	styles: dict[str, ButtonStyle] = {
		"primary": ButtonStyle("#2563eb", "#1d4ed8", _FILLED_TEXT),
		"positive": ButtonStyle("#16a34a", "#15803d", _FILLED_TEXT),
		"secondary": ButtonStyle(
			"transparent", blend(colors.card_bg, accent, 0.16), accent, accent, 2
		),
		"danger": ButtonStyle(
			"transparent",
			blend(colors.card_bg, colors.error_text, 0.16),
			colors.error_text,
			colors.error_text,
			2,
		),
		"ghost": ButtonStyle(
			"transparent", blend(colors.card_bg, colors.text_muted, 0.12), colors.text_muted
		),
		"muted": ButtonStyle(colors.entry_bg, colors.entry_border, colors.text_primary),
	}
	return styles.get(variant, styles["primary"])


# Button sizes: height, font size, corner radius, default width
BUTTON_SIZES: dict[str, tuple[int, int, int, int]] = {
	"lg": (52, 19, 16, 240),
	"md": (44, 16, 12, 180),
	"sm": (36, 14, 10, 120),
}


# ---------------------------------------------------------------------------
# Keyboard Navigation Helpers
# ---------------------------------------------------------------------------


def setup_keyboard_navigation(widgets: list[ctk.CTkBaseClass]) -> None:
	"""Configure Tab order for a list of widgets.

	Widgets will be traversable in the order provided.
	Enter key will activate buttons.
	"""
	for i, widget in enumerate(widgets):
		# Enable focus
		try:
			widget.configure(takefocus=True)
		except Exception:
			pass

		# Add Enter key binding for buttons
		if isinstance(widget, ctk.CTkButton):
			widget.bind("<Return>", lambda e, w=widget: _invoke_button(w))
			widget.bind("<KP_Enter>", lambda e, w=widget: _invoke_button(w))
			widget.bind("<space>", lambda e, w=widget: _invoke_button(w))


def _invoke_button(button: ctk.CTkButton) -> None:
	"""Safely invoke a button's command."""
	try:
		command = button.cget("command")
		if command:
			command()
	except Exception:
		pass


def add_focus_highlight(widget: ctk.CTkBaseClass, focus_color: str | None = None) -> None:
	"""Add visual focus indicator to a widget.

	When focused, the widget gets a colored border/ring.
	If focus_color is None the current theme's focus_ring color is read at
	focus time so theme switches are always reflected correctly.
	"""
	original_border_color = None
	original_border_width = None

	try:
		original_border_color = widget.cget("border_color")
		original_border_width = widget.cget("border_width")
	except Exception:
		return

	def on_focus_in(event: Any) -> None:
		try:
			ring = focus_color if focus_color is not None else get_colors().focus_ring
			widget.configure(border_color=ring, border_width=2)
		except Exception:
			pass

	def on_focus_out(event: Any) -> None:
		try:
			widget.configure(
				border_color=original_border_color or "transparent",
				border_width=original_border_width or 0,
			)
		except Exception:
			pass

	try:
		widget.bind("<FocusIn>", on_focus_in, add="+")
		widget.bind("<FocusOut>", on_focus_out, add="+")
	except NotImplementedError:
		# Some CTk widgets (e.g. CTkSegmentedButton) don't support bind();
		# they simply go without the focus ring instead of aborting the build.
		pass


def bind_escape_to_back(root: ctk.CTk, callback: Callable[[], None]) -> str:
	"""Bind Escape key to a back/cancel action. Returns binding ID."""
	return root.bind("<Escape>", lambda e: callback())


def unbind_escape(root: ctk.CTk, binding_id: str) -> None:
	"""Remove an Escape key binding."""
	try:
		root.unbind("<Escape>", binding_id)
	except Exception:
		pass


# ---------------------------------------------------------------------------
# Font utilities


def make_font(*, size: int, weight: str = "normal", family: str | None = None) -> ctk.CTkFont:
	"""Return a configured CTkFont with the shared defaults.

	*family* defaults to the best installed sans-serif font for this OS.
	"""

	if family is None:
		family = resolve_font_family("sans")
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
	"""Button text font (size 18, bold)."""
	return make_font(size=FONT_SIZE_MD, weight="bold")


def font_button_large() -> ctk.CTkFont:
	"""Large button text font (size 20, bold)."""
	return make_font(size=FONT_SIZE_LG, weight="bold")


def font_callout() -> ctk.CTkFont:
	"""Callout/emphasis font (size 22, bold)."""
	return make_font(size=FONT_SIZE_XL, weight="bold")


def font_mono(size: int = FONT_SIZE_4XL) -> ctk.CTkFont:
	"""Bold monospace font for Morse display (best installed mono font)."""
	return make_font(size=size, weight="bold", family=resolve_font_family("mono"))


def font_timer() -> ctk.CTkFont:
	"""Timer display font (size 24, bold monospace)."""
	return font_mono(24)


# ---------------------------------------------------------------------------
# Widget factories


def make_label(
	parent,
	text: str,
	*,
	font_size: int = 18,
	weight: str = "normal",
	font: ctk.CTkFont | None = None,
	text_color: str | None = None,
	wraplength: int | None = None,
	justify: str = "center",
	**options,
) -> ctk.CTkLabel:
	"""Create a CTkLabel using the shared typography and colour tokens.

	text_color defaults to the current theme's primary text color when None.
	"""
	resolved_color = text_color if text_color is not None else get_colors().text_primary

	label = ctk.CTkLabel(
		parent,
		text=text,
		font=font or make_font(size=font_size, weight=weight),
		text_color=resolved_color,
		justify=justify,
		**options,
	)
	if wraplength is not None:
		label.configure(wraplength=wraplength)
	return label


_MORSE_ONLY = frozenset(".- /\n")


def is_morse_text(text: str) -> bool:
	return bool(text.strip()) and set(text) <= _MORSE_ONLY


def pretty_morse(code: str) -> str:
	"""Display form of Morse: round dots and long dashes, evenly spaced.

	Letters keep one gap, words (three spaces) a wider one; line breaks stay.
	Inside a word only non-breaking spaces are used, so a label that wraps
	can only break between words, never inside a letter.
	Text that isn't pure Morse is returned unchanged.
	"""
	if not is_morse_text(code):
		return code
	nbsp = " "

	def line(text: str) -> str:
		return "  ".join(
			(nbsp * 3).join(
				nbsp.join("•" if s == "." else "—" if s == "-" else s for s in letter)
				for letter in word.split()
			)
			for word in text.split("   ")
		)

	return "\n".join(line(part) for part in code.split("\n"))


def resolve_background(widget) -> str:
	"""The colour actually shown behind *widget* (skips transparent parents)."""
	node = widget.master
	while node is not None:
		try:
			color = node.cget("fg_color")
		except (ValueError, AttributeError, Exception):
			try:
				return node.cget("bg")
			except Exception:
				break
		if isinstance(color, (tuple, list)):
			color = color[1] if get_appearance_mode() == "dark" else color[0]
		if color and color != "transparent":
			return color
		node = getattr(node, "master", None)
	return get_colors().card_bg


def attach_hover(button: ctk.CTkButton, variant: str) -> None:
	"""Smooth hover/press feedback driven by colour tweens.

	CTk's own hover swaps colours instantly; this fades over ~120 ms and adds
	a darker shade while pressed. Colours are read from the theme at event
	time, so it keeps working after a light/dark switch.
	"""
	state: dict[str, Any] = {"anim": None, "inside": False}

	def disabled() -> bool:
		try:
			return button.cget("state") == "disabled"
		except Exception:
			return True

	def rest_color() -> str:
		style = get_button_style(variant)
		return resolve_background(button) if style.fg_color == "transparent" else style.fg_color

	def current_color() -> str:
		color = button.cget("fg_color")
		if isinstance(color, (tuple, list)):
			color = color[1] if get_appearance_mode() == "dark" else color[0]
		return rest_color() if color == "transparent" else color

	def fade_to(target: str, *, restore_transparent: bool = False) -> None:
		start = current_color()
		previous: Animation | None = state["anim"]
		anim = tween_color(button, "fg_color", start, target, 120, previous)
		state["anim"] = anim
		if restore_transparent and get_button_style(variant).fg_color == "transparent":
			# Go back to real transparency once faded, so theme changes stay correct.
			button.after(140, lambda: _set_transparent_if_idle(button, state))

	def on_enter(_event=None) -> None:
		state["inside"] = True
		if not disabled():
			fade_to(get_button_style(variant).hover_color)

	def on_leave(_event=None) -> None:
		state["inside"] = False
		if not disabled():
			fade_to(rest_color(), restore_transparent=True)

	def on_press(_event=None) -> None:
		if not disabled():
			if state["anim"] is not None:
				state["anim"].cancel()
			button.configure(fg_color=blend(get_button_style(variant).hover_color, "#000000", 0.18))

	def on_release(_event=None) -> None:
		if not disabled() and state["inside"]:
			button.configure(fg_color=get_button_style(variant).hover_color)

	button.bind("<Enter>", on_enter, add="+")
	button.bind("<Leave>", on_leave, add="+")
	button.bind("<ButtonPress-1>", on_press, add="+")
	button.bind("<ButtonRelease-1>", on_release, add="+")


def _set_transparent_if_idle(button: ctk.CTkButton, state: dict[str, Any]) -> None:
	try:
		if not state["inside"] and button.winfo_exists():
			button.configure(fg_color="transparent")
	except Exception:
		pass


def make_button(
	parent,
	text: str,
	*,
	command: Callable[[], None],
	font_size: int | None = None,
	weight: str = "bold",
	font: ctk.CTkFont | None = None,
	variant: str = "primary",
	size: str = "md",
	width: int | None = None,
	height: int | None = None,
	corner_radius: int | None = None,
	**options,
) -> ctk.CTkButton:
	"""Create a CTkButton in one of the shared variants and sizes.

	``size`` ("lg", "md", "sm") sets height, font size, corner radius and a
	default width; explicit arguments still win.
	"""

	style = get_button_style(variant)
	size_height, size_font, size_radius, size_width = BUTTON_SIZES.get(size, BUTTON_SIZES["md"])
	if style.border_color:
		options.setdefault("border_color", style.border_color)
	button = ctk.CTkButton(
		parent,
		text=text,
		command=command,
		font=font or make_font(size=font_size or size_font, weight=weight),
		fg_color=style.fg_color,
		hover=False,
		text_color=style.text_color,
		text_color_disabled=blend(get_colors().card_bg, style.text_color, 0.45),
		border_width=style.border_width,
		width=width if width is not None else size_width,
		height=height if height is not None else size_height,
		corner_radius=corner_radius if corner_radius is not None else size_radius,
		cursor="hand2",
		**options,
	)
	attach_hover(button, variant)
	return button


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
	"""Create a CTkEntry with consistent typography, theme colours and rounded corners."""

	colors = get_colors()
	options.setdefault("fg_color", colors.entry_bg)
	options.setdefault("border_color", colors.entry_border)
	options.setdefault("text_color", colors.text_primary)
	options.setdefault("placeholder_text_color", colors.text_placeholder)
	options.setdefault("border_width", 2)
	entry = ctk.CTkEntry(
		parent,
		font=font or make_font(size=font_size, weight=weight),
		width=width,
		corner_radius=corner_radius,
		**options,
	)
	# The border lights up in the accent colour while the field has focus.
	entry.bind("<FocusIn>", lambda _e: entry.configure(border_color=accent_color()), add="+")
	entry.bind(
		"<FocusOut>", lambda _e: entry.configure(border_color=get_colors().entry_border), add="+"
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
	fg_color: str | None = None,
	border_color: str | None = None,
	**options,
) -> ctk.CTkFrame:
	"""Create a elevated card-style frame used across the modern screens."""
	if fg_color is None or border_color is None:
		colors = get_colors()
		if fg_color is None:
			fg_color = colors.card_bg
		if border_color is None:
			border_color = colors.card_border

	return make_frame(
		parent,
		fg_color=fg_color,
		corner_radius=corner_radius,
		border_width=border_width,
		border_color=border_color,
		**options,
	)


@dataclass
class Page:
	"""A full-height screen: header (back + title), body (fills the height), footer."""

	backdrop: Any
	card: ctk.CTkFrame
	header: ctk.CTkFrame
	body: ctk.CTkFrame
	footer: ctk.CTkFrame
	title_label: ctk.CTkLabel | None = None
	subtitle_label: ctk.CTkLabel | None = None


def make_page(
	root,
	*,
	title: str | None = None,
	subtitle: str | None = None,
	back: tuple[str, Callable[[], None]] | None = None,
	relwidth: float = 0.86,
	relheight: float = 0.9,
) -> Page:
	"""Build the shared screen skeleton on a patterned backdrop.

	The body row has all the vertical weight, so content placed in it with
	grid weights spreads over the whole card height instead of bunching at
	the top. A *back* button sits as a ghost link in the header's top-left.
	"""
	from .backdrop import make_backdrop

	colors = get_colors()
	backdrop = make_backdrop(root)
	card = make_card(backdrop, fg_color=colors.card_bg, border_color=colors.card_border)
	# The card "settles" into place: starts slightly low and eases up once it
	# is actually on screen (screens are built before they slide in).
	card.place(relx=0.5, rely=0.52, anchor="center", relwidth=relwidth, relheight=relheight)
	settled = {"started": False}

	def settle(_event=None) -> None:
		if not settled["started"]:
			settled["started"] = True
			animate(card, 240, lambda p: card.place_configure(rely=0.52 - 0.02 * p))

	card.bind("<Map>", settle, add="+")
	card.grid_columnconfigure(0, weight=1)
	card.grid_rowconfigure(1, weight=1)

	header = make_frame(card)
	header.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 4))
	header.grid_columnconfigure(0, weight=1)

	title_label = subtitle_label = None
	if back is not None:
		label, callback = back
		make_button(
			header, f"← {label}", command=callback, variant="ghost", size="sm", width=0
		).place(x=0, y=0)
	if title:
		title_label = make_label(header, title, font=font_title())
		title_label.grid(row=0, column=0, pady=(8, 2))
	if subtitle:
		subtitle_label = make_label(
			header, subtitle, font=font_muted(), text_color=colors.text_muted, wraplength=760
		)
		subtitle_label.grid(row=1, column=0, pady=(0, 4))

	body = make_frame(card)
	body.grid(row=1, column=0, sticky="nsew", padx=48, pady=8)
	body.grid_columnconfigure(0, weight=1)

	footer = make_frame(card)
	footer.grid(row=2, column=0, sticky="ew", padx=40, pady=(8, 28))
	footer.grid_columnconfigure(1, weight=1)

	return Page(backdrop, card, header, body, footer, title_label, subtitle_label)


def footer_group(footer: ctk.CTkFrame, column: int) -> ctk.CTkFrame:
	"""A frame in the footer's left (0), centre (1) or right (2) column."""
	frame = make_frame(footer)
	frame.grid(row=0, column=column, sticky={0: "w", 1: "", 2: "e"}[column])
	return frame


def spread_rows(frame: ctk.CTkFrame, rows: int, *, content_weight: int = 0) -> None:
	"""Give the first and last row of *frame* the spare height (centres the rest)."""
	frame.grid_rowconfigure(0, weight=1)
	frame.grid_rowconfigure(rows + 1, weight=1)
	for row in range(1, rows + 1):
		frame.grid_rowconfigure(row, weight=content_weight)


def make_progress_bar(
	parent,
	*,
	root,
	width: int | None = None,
	height: int = 12,
	fg_color: str | None = None,
	progress_color: str | None = None,
	corner_radius: int | None = None,
) -> ctk.CTkProgressBar:
	"""Create a CTkProgressBar with shared animation helpers bound to the widget."""
	if progress_color is None:
		progress_color = get_button_style("primary").fg_color

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
	"BUTTON_SIZES",
	"Page",
	"accent_color",
	"attach_hover",
	"footer_group",
	"make_page",
	"pretty_morse",
	"resolve_background",
	"spread_rows",
	"make_font",
	"make_label",
	"make_button",
	"make_entry",
	"make_frame",
	"make_card",
	"make_progress_bar",
	"ButtonStyle",
	"get_button_style",
	# Keyboard navigation
	"setup_keyboard_navigation",
	"add_focus_highlight",
	"bind_escape_to_back",
	"unbind_escape",
	# Font presets
	"font_title",
	"font_subtitle",
	"font_body",
	"font_muted",
	"font_button",
	"font_button_large",
	"font_callout",
	"font_mono",
	"font_timer",
]
