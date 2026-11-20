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
	add_focus_highlight,
	make_button,
	make_card,
	make_frame,
	make_label,
	setup_keyboard_navigation,
)

# Colour emoji can crash Tk on Linux/X11 ("BadLength" in XRender), so Linux
# gets plain labels.
_USE_EMOJI = not sys.platform.startswith("linux")
_LABEL_LIGHT = t("home.theme_light_emoji") if _USE_EMOJI else t("home.theme_light")
_LABEL_DARK = t("home.theme_dark_emoji") if _USE_EMOJI else t("home.theme_dark")


class HomeView:
	"""Renders the landing screen using shared widget helpers."""

	def __init__(
		self,
		root,
		nav: Navigator,
	) -> None:
		self.root = root
		self.nav = nav
		# Start in the operating system's light/dark mode (darkdetect ships with
		# CustomTkinter); the toggle on this screen still switches it freely.
		initial_mode = system_appearance_mode()
		ctk.set_appearance_mode(initial_mode)
		ctk.set_default_color_theme("blue")
		set_appearance_mode(initial_mode)

		# Widget references – built once, repainted on theme change
		self._built = False
		self._backdrop: ctk.CTkFrame | None = None
		self._hero: ctk.CTkFrame | None = None
		self._header_frame: ctk.CTkFrame | None = None
		self._theme_segmented: ctk.CTkSegmentedButton | None = None
		self._title_label: ctk.CTkLabel | None = None
		self._subtitle_label: ctk.CTkLabel | None = None
		self._buttons_frame: ctk.CTkFrame | None = None
		self._nav_buttons: list[ctk.CTkButton] = []
		self._footer: ctk.CTkFrame | None = None
		self._exit_btn: ctk.CTkButton | None = None

	def _on_theme_selected(self, selected: str) -> None:
		"""Handle theme selection from segmented button – repaints in-place."""
		mode = "dark" if selected == _LABEL_DARK else "light"
		set_appearance_mode(mode)
		self.root.after_idle(self._apply_colors)

	def _build(self) -> None:
		"""Create the widget tree once."""
		self._backdrop = make_frame(self.root, fg_color="transparent")
		self._backdrop.pack(fill="both", expand=True)

		self._hero = make_card(self._backdrop, fg_color="transparent", border_width=0)
		self._hero.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.62, relheight=0.62)

		# Header row with theme toggle
		self._header_frame = make_frame(self._hero, fg_color="transparent")
		self._header_frame.pack(fill="x", padx=28, pady=(16, 0))

		colors = get_colors()
		if get_appearance_mode() == "light":
			unselected_bg = "#e2e8f0"
			selected_bg = "#3b82f6"
		else:
			unselected_bg = colors.entry_bg
			selected_bg = "#3b82f6"

		self._theme_segmented = ctk.CTkSegmentedButton(
			self._header_frame,
			values=[_LABEL_LIGHT, _LABEL_DARK],
			command=self._on_theme_selected,
			font=ctk.CTkFont(size=18, weight="bold"),
			width=220,
			height=42,
			corner_radius=12,
			fg_color=colors.section_bg,
			selected_color=selected_bg,
			selected_hover_color="#2563eb",
			unselected_color=unselected_bg,
			unselected_hover_color="#64748b",
			text_color=colors.text_primary,
		)
		self._theme_segmented.set(_LABEL_DARK if get_appearance_mode() == "dark" else _LABEL_LIGHT)
		self._theme_segmented.pack(side="right")
		add_focus_highlight(self._theme_segmented)

		self._title_label = make_label(
			self._hero, t("home.morsekoodi_rakendus"), font_size=38, weight="bold"
		)
		self._title_label.pack(pady=(20, 8))

		self._subtitle_label = make_label(
			self._hero,
			t("home.programm_morsekoodi_oppimiseks_harjutamiseks"),
			font_size=18,
			weight="bold",
		)
		self._subtitle_label.pack(pady=(0, 24))

		self._buttons_frame = make_frame(self._hero, fg_color="transparent")
		self._buttons_frame.pack(pady=(0, 24))

		# Two columns: learning on the left, practice and tools on the right.
		menu_items = [
			(t("home.tutvustus"), self.nav.introduction),
			(t("home.ope"), self.nav.flashcards),
			(t("home.koch"), self.nav.koch),
			(t("home.harjutused"), self.nav.translation),
			(t("home.test"), self.nav.test),
			(t("home.keyer"), self.nav.keyer),
			(t("home.sandbox"), self.nav.translation_sandbox),
		]

		rows = (len(menu_items) + 1) // 2
		for index, (label, callback) in enumerate(menu_items):
			btn = make_button(
				self._buttons_frame,
				text=label,
				command=callback,
				font_size=20,
				variant="primary",
				width=240,
				height=48,
				corner_radius=14,
			)
			btn.grid(row=index % rows, column=index // rows, padx=12, pady=8)
			add_focus_highlight(btn)
			self._nav_buttons.append(btn)

		self._footer = make_frame(self._hero, fg_color="transparent")
		self._footer.pack(side="bottom", fill="x", padx=28, pady=28)

		self._exit_btn = make_button(
			self._footer,
			text=t("home.valju_programmist"),
			command=self.nav.exit,
			font_size=18,
			variant="danger",
			width=220,
			height=44,
			corner_radius=14,
		)
		self._exit_btn.pack(side="right")
		add_focus_highlight(self._exit_btn, focus_color="#dc2626")

		all_widgets = [self._theme_segmented, *self._nav_buttons, self._exit_btn]
		setup_keyboard_navigation(all_widgets)

		if self._nav_buttons:
			try:
				self._nav_buttons[0].focus_set()
			except TclError:
				pass

		self._built = True

	def _apply_colors(self) -> None:
		"""Update all widget colors to match the current theme without rebuilding."""
		if not self._built:
			return
		colors = get_colors()

		# Root / backdrop
		try:
			self.root.configure(fg_color=colors.backdrop_bg)
		except TclError:
			pass
		self._backdrop.configure(fg_color=colors.backdrop_bg)

		# Hero card
		self._hero.configure(
			fg_color=colors.card_bg, border_color=colors.card_border, border_width=1
		)

		# Labels
		self._title_label.configure(text_color=colors.text_primary)
		self._subtitle_label.configure(text_color=colors.text_muted)

		# Segmented button – selected must stand out clearly from unselected
		if get_appearance_mode() == "light":
			unselected_bg = "#e2e8f0"
			unselected_hover = "#cbd5e1"
			selected_bg = "#3b82f6"
			selected_hover = "#2563eb"
		else:
			unselected_bg = colors.entry_bg
			unselected_hover = "#2d3f5e"
			selected_bg = "#3b82f6"
			selected_hover = "#2563eb"

		self._theme_segmented.configure(
			fg_color=colors.section_bg,
			selected_color=selected_bg,
			selected_hover_color=selected_hover,
			unselected_color=unselected_bg,
			unselected_hover_color=unselected_hover,
			text_color=colors.text_primary,
		)
		self._theme_segmented.set(_LABEL_DARK if get_appearance_mode() == "dark" else _LABEL_LIGHT)

	def _clear_content(self) -> None:
		"""Destroy this view's children without touching other views."""
		for w in self.root.winfo_children():
			w.destroy()

	def show(self) -> None:
		self._clear_content()
		self._built = False
		self._nav_buttons = []

		try:
			self.root.configure(fg_color=get_colors().backdrop_bg)
		except TclError:
			pass

		self._build()
		self._apply_colors()


class IntroductionView:
	"""Displays the introduction content using shared helpers."""

	def __init__(
		self,
		root,
		nav: Navigator,
	) -> None:
		self.root = root
		self.nav = nav

	def _clear_content(self) -> None:
		"""Destroy this view's children without touching other views."""
		for w in self.root.winfo_children():
			w.destroy()

	def show(self) -> None:
		self._clear_content()
		colors = get_colors()

		try:
			self.root.configure(fg_color=colors.backdrop_bg)
		except TclError:
			try:
				self.root.configure(bg=colors.backdrop_bg)
			except TclError:
				pass

		backdrop = make_frame(self.root, fg_color=colors.backdrop_bg)
		backdrop.pack(fill="both", expand=True)

		card = make_card(backdrop, fg_color=colors.card_bg, border_color=colors.card_border)
		card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.68, relheight=0.68)

		make_label(
			card, t("home.tutvustus"), font_size=34, weight="bold", text_color=colors.text_primary
		).pack(pady=(36, 24))

		first_block = make_frame(card, fg_color=colors.section_bg, corner_radius=28)
		first_block.pack(padx=36, pady=(0, 36), fill="x")

		first_text = make_label(
			first_block,
			(t("home.morsekood_moodab_aega_uhikutes")),
			font_size=20,
			weight="bold",
			text_color=colors.text_muted,
			justify="left",
			anchor="w",
		)
		first_text.pack(padx=36, pady=28, fill="x")
		first_block.update_idletasks()
		first_text.configure(wraplength=first_block.winfo_width() - 72)

		second_block = make_frame(card, fg_color=colors.section_bg, corner_radius=28)
		second_block.pack(padx=36, pady=(0, 36), fill="x")

		second_text = make_label(
			second_block,
			(t("home.ope_voimaldab_flashcard_meetodi")),
			font_size=20,
			weight="bold",
			text_color=colors.text_muted,
			justify="left",
			anchor="w",
		)
		second_text.pack(padx=36, pady=28, fill="x")
		second_block.update_idletasks()
		second_text.configure(wraplength=second_block.winfo_width() - 72)

		button_row = make_frame(card, fg_color="transparent")
		button_row.pack(pady=(0, 36))

		back_btn = make_button(
			button_row,
			text=t("common.tagasi_avalehele"),
			command=self.nav.home,
			font_size=18,
			variant="danger",
			width=220,
			height=44,
			corner_radius=14,
		)
		back_btn.pack()
		add_focus_highlight(back_btn, focus_color="#dc2626")
		setup_keyboard_navigation([back_btn])
		self.root.after(100, back_btn.focus_set)
