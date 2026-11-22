"""A "choose one of two" screen used for the Õpe and Harjutused groups."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..strings import t
from .theme import get_colors
from .widgets import (
	accent_color,
	add_focus_highlight,
	font_body,
	font_mono,
	make_button,
	make_frame,
	make_label,
	make_page,
	setup_keyboard_navigation,
	spread_rows,
)


@dataclass(frozen=True)
class HubOption:
	label: str
	description: str
	open: Callable[[], None]
	symbol: str = "· —"


class HubView:
	"""Two large tiles side by side, each with a button and what it is for."""

	def __init__(
		self, root, *, title: str, subtitle: str, options: list[HubOption], back: Callable[[], None]
	) -> None:
		self.root = root
		self.title = title
		self.subtitle = subtitle
		self.options = options
		self.back = back

	def show(self) -> None:
		for widget in self.root.winfo_children():
			widget.destroy()
		colors = get_colors()
		page = make_page(
			self.root,
			title=self.title,
			subtitle=self.subtitle,
			back=(t("common.tagasi_avalehele"), self.back),
			relwidth=0.74,
		)
		# The tiles take the whole body height; their content is centred inside.
		page.footer.grid_remove()
		page.body.grid_configure(pady=(8, 32))
		page.body.grid_rowconfigure(0, weight=1)
		tiles = make_frame(page.body)
		tiles.grid(row=0, column=0, sticky="nsew", pady=(12, 8))
		tiles.grid_rowconfigure(0, weight=1)
		buttons = []
		for column, option in enumerate(self.options):
			tiles.grid_columnconfigure(column, weight=1, uniform="tile")
			tile = make_frame(
				tiles,
				fg_color=colors.section_bg,
				corner_radius=22,
				border_width=1,
				border_color=colors.card_border,
			)
			tile.grid(row=0, column=column, sticky="nsew", padx=14)
			tile.grid_columnconfigure(0, weight=1)
			spread_rows(tile, 3)
			make_label(tile, option.symbol, font=font_mono(52), text_color=accent_color()).grid(
				row=1, column=0, pady=(0, 18)
			)
			button = make_button(tile, option.label, command=option.open, size="lg", width=260)
			button.grid(row=2, column=0, padx=28, pady=(0, 14))
			make_label(
				tile,
				option.description,
				font=font_body(),
				text_color=colors.text_muted,
				wraplength=340,
			).grid(row=3, column=0, padx=28)
			add_focus_highlight(button)
			buttons.append(button)
		setup_keyboard_navigation(buttons)
		if buttons:
			buttons[0].focus_set()


__all__ = ["HubOption", "HubView"]
