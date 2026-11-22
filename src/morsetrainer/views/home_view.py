from __future__ import annotations

import sys
from tkinter import TclError

import customtkinter as ctk

from ..navigator import Navigator
from ..strings import t
from .theme import (
	get_appearance_mode,
	get_colors,
	set_appearance_mode,
	system_appearance_mode,
)
from .widgets import (
	accent_color,
	add_focus_highlight,
	font_callout,
	font_muted,
	make_button,
	make_font,
	make_frame,
	make_label,
	make_page,
	setup_keyboard_navigation,
)

# Colour emoji can crash Tk on Linux/X11 ("BadLength" in XRender), so Linux
# gets plain labels.
_USE_EMOJI = not sys.platform.startswith("linux")
_LABEL_LIGHT = t("home.theme_light_emoji") if _USE_EMOJI else t("home.theme_light")
_LABEL_DARK = t("home.theme_dark_emoji") if _USE_EMOJI else t("home.theme_dark")


def _clear(root) -> None:
	for widget in root.winfo_children():
		widget.destroy()


class HomeView:
	"""Landing screen: five main entries, spread over the full card height."""

	def __init__(self, root, nav: Navigator) -> None:
		self.root = root
		self.nav = nav
		# Start in the operating system's light/dark mode (darkdetect ships with
		# CustomTkinter); the toggle on this screen still switches it freely.
		initial_mode = system_appearance_mode()
		ctk.set_appearance_mode(initial_mode)
		ctk.set_default_color_theme("blue")
		set_appearance_mode(initial_mode)
		self._nav_buttons: list[ctk.CTkButton] = []

	def _on_theme_selected(self, selected: str) -> None:
		set_appearance_mode("dark" if selected == _LABEL_DARK else "light")
		# Rebuild so every colour (buttons, pattern, card) follows the new theme.
		self.root.after_idle(self.show)

	def show(self) -> None:
		_clear(self.root)
		self._nav_buttons = []
		colors = get_colors()
		page = make_page(
			self.root,
			title=t("home.morsekoodi_rakendus"),
			subtitle=t("home.programm_morsekoodi_oppimiseks_harjutamiseks"),
			relwidth=0.62,
		)

		theme_toggle = ctk.CTkSegmentedButton(
			page.header,
			values=[_LABEL_LIGHT, _LABEL_DARK],
			command=self._on_theme_selected,
			font=font_muted(),
			height=34,
			corner_radius=10,
			fg_color=colors.section_bg,
			selected_color="#2563eb",
			selected_hover_color="#1d4ed8",
			unselected_color=colors.section_bg,
			unselected_hover_color=colors.entry_bg,
			text_color=colors.text_primary,
		)
		theme_toggle.set(_LABEL_DARK if get_appearance_mode() == "dark" else _LABEL_LIGHT)
		theme_toggle.place(relx=1.0, y=0, anchor="ne")

		menu = [
			(t("home.tutvustus"), t("home.caption_intro"), self.nav.introduction),
			(t("home.ope"), t("home.caption_learn"), self.nav.learn_hub),
			(t("home.harjutused"), t("home.caption_practice"), self.nav.practice_hub),
			(t("home.test"), t("home.caption_test"), self.nav.test),
			(t("home.sandbox"), t("home.caption_sandbox"), self.nav.translation_sandbox),
		]
		# Each entry gets an equal share of the height, so the menu fills the card.
		column = make_frame(page.body)
		column.grid(row=0, column=0, sticky="nsew", pady=(8, 0))
		column.grid_columnconfigure(0, weight=1)
		page.body.grid_rowconfigure(0, weight=1)
		for index, (label, caption, callback) in enumerate(menu):
			column.grid_rowconfigure(index, weight=1)
			item = make_frame(column)
			item.grid(row=index, column=0)
			button = make_button(
				item, label, command=callback, variant="primary", size="lg", width=300
			)
			button.pack()
			make_label(item, caption, font=font_muted(), text_color=colors.text_muted).pack(
				pady=(4, 0)
			)
			add_focus_highlight(button)
			self._nav_buttons.append(button)

		exit_button = make_button(
			page.footer,
			t("home.valju_programmist"),
			command=self.nav.exit,
			variant="ghost",
			size="sm",
		)
		exit_button.grid(row=0, column=2, sticky="e")
		setup_keyboard_navigation([*self._nav_buttons, exit_button])
		try:
			self._nav_buttons[0].focus_set()
		except TclError:
			pass


class IntroductionView:
	"""How Morse timing works, and what each mode is for."""

	def __init__(self, root, nav: Navigator) -> None:
		self.root = root
		self.nav = nav
		self._text_font = make_font(size=20)

	def show(self) -> None:
		_clear(self.root)
		colors = get_colors()
		page = make_page(
			self.root,
			title=t("home.tutvustus"),
			back=(t("common.tagasi_avalehele"), self.nav.home),
			relwidth=0.74,
		)
		page.footer.grid_remove()
		page.body.grid_configure(pady=(8, 32))
		# Two blocks share the height; text is larger and centred in each block.
		for row, (heading, text) in enumerate(
			(
				(t("intro.timing_heading"), t("home.morsekood_moodab_aega_uhikutes")),
				(t("intro.modes_heading"), t("home.ope_voimaldab_flashcard_meetodi")),
			)
		):
			page.body.grid_rowconfigure(row, weight=1)
			block = make_frame(page.body, fg_color=colors.section_bg, corner_radius=20)
			block.grid(row=row, column=0, sticky="nsew", pady=10)
			inner = make_frame(block)
			inner.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92)
			make_label(
				inner, heading, font=font_callout(), text_color=accent_color(), anchor="w"
			).pack(fill="x", pady=(0, 8))
			make_label(
				inner,
				text,
				font=self._text_font,
				text_color=colors.text_primary,
				justify="left",
				anchor="w",
				wraplength=980,
			).pack(fill="x")


__all__ = ["HomeView", "IntroductionView"]
