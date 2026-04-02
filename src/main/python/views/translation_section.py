"""Translation input/output section for the sandbox view."""

from __future__ import annotations

from collections.abc import Callable
from tkinter import TclError

import customtkinter as ctk

from ..controllers.translation_sandbox_controller import SandboxState
from .theme import get_colors
from .widgets import (
	font_button_large,
	font_callout,
	font_mono,
	make_button,
	make_card,
	make_font,
	make_frame,
	make_label,
)

# Accent colours used only within this component
_BUTTON_SEGMENT_HOVER = "#1d4ed8"


class TranslationSection:
	"""Left-side translation controls and text panes."""

	def __init__(
		self,
		parent,
		*,
		on_select_mode: Callable[[str], None],
		on_translate: Callable[[], None],
		on_clear: Callable[[], None],
	) -> None:
		self._on_select_mode = on_select_mode
		self._on_translate = on_translate
		self._on_clear = on_clear

		_c = get_colors()
		self.container = make_card(
			parent, fg_color=_c.section_bg, border_color=_c.card_border, corner_radius=24
		)
		self.container.columnconfigure(0, weight=1)

		self._title_font = font_callout()
		self._body_font = make_font(size=18, weight="bold")
		self._button_font = font_button_large()
		self._hint_font = make_font(size=16, weight="bold")
		self._mono_font = font_mono(size=21)

		self._input_placeholder_text = "Sisesta algtekst/morsekood siia..."
		self._output_placeholder_text = "Kliki tõlgi, et kuvada tulemus..."
		self._input_placeholder_active = False
		self._output_placeholder_active = False

		self.mode_selector: ctk.CTkSegmentedButton | None = None
		self._mode_value_var = ctk.StringVar(value="Tekst → Morse")
		self._label_to_mode = {
			"Tekst → Morse": "text_to_morse",
			"Morse → tekst": "morse_to_text",
		}
		self._suppress_mode_callback = False
		self.input_label: ctk.CTkLabel | None = None
		self.input_text: ctk.CTkTextbox | None = None
		self.output_label: ctk.CTkLabel | None = None
		self.output_text: ctk.CTkTextbox | None = None
		self.error_label: ctk.CTkLabel | None = None

		self._build()

	def _build(self) -> None:
		intro = make_label(
			self.container,
			"Sisesta tekst või morsekood ning vajuta 'Tõlgi'. Kasti tühjendamiseks kliki 'Puhasta'.",
			font=self._title_font,
			text_color=get_colors().text_muted,
			wraplength=420,
		)
		intro.grid(row=0, column=0, padx=32, pady=(28, 18))

		mode_card = make_frame(self.container, fg_color="transparent")
		mode_card.grid(row=1, column=0, padx=32, pady=(0, 26), sticky="ew")
		mode_card.columnconfigure(0, weight=1)

		make_label(
			mode_card,
			"Tõlkesuund",
			font=self._body_font,
			text_color=get_colors().text_muted,
			justify="left",
		).grid(row=0, column=0, pady=(0, 12))

		_sc = get_colors()
		self.mode_selector = ctk.CTkSegmentedButton(
			mode_card,
			values=list(self._label_to_mode.keys()),
			command=self._handle_mode_change,
			variable=self._mode_value_var,
			font=self._button_font,
			fg_color=_sc.entry_bg,
			selected_color=_sc.focus_ring,
			selected_hover_color=_BUTTON_SEGMENT_HOVER,
			unselected_color=_sc.entry_bg,
			unselected_hover_color=_sc.entry_border,
			text_color=_sc.text_primary,
		)
		self.mode_selector.grid(row=1, column=0, sticky="ew")

		input_section = make_frame(self.container, fg_color="transparent")
		input_section.grid(row=2, column=0, padx=32, pady=(0, 24), sticky="nsew")
		input_section.columnconfigure(0, weight=1)
		input_section.rowconfigure(1, weight=1)

		self.input_label = make_label(input_section, "", font=self._body_font, justify="left")
		self.input_label.grid(row=0, column=0, sticky="w")

		_tc = get_colors()
		self.input_text = ctk.CTkTextbox(
			input_section,
			font=self._mono_font,
			corner_radius=12,
			height=160,
			fg_color=_tc.entry_bg,
			border_width=1,
			border_color=_tc.card_border,
		)
		self.input_text.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
		self.input_text.configure(wrap="word")
		self.input_text.bind("<FocusIn>", self._handle_input_focus_in)
		self.input_text.bind("<FocusOut>", self._handle_input_focus_out)
		self.input_text.bind("<Key>", self._handle_input_keypress)
		self._show_input_placeholder()

		actions = make_frame(self.container, fg_color="transparent")
		actions.grid(row=3, column=0, pady=(0, 24))

		make_button(
			actions,
			text="Tõlgi",
			command=self._on_translate,
			font=self._button_font,
			variant="primary",
			width=160,
			height=44,
		).grid(row=0, column=0, padx=12)

		make_button(
			actions,
			text="Puhasta",
			command=self._on_clear,
			font=self._button_font,
			variant="muted",
			width=160,
			height=44,
		).grid(row=0, column=1, padx=12)

		output_section = make_frame(self.container, fg_color="transparent")
		output_section.grid(row=4, column=0, padx=32, pady=(0, 20), sticky="nsew")
		output_section.columnconfigure(0, weight=1)
		output_section.rowconfigure(1, weight=1)

		self.output_label = make_label(output_section, "", font=self._body_font, justify="left")
		self.output_label.grid(row=0, column=0, sticky="w")

		_oc = get_colors()
		self.output_text = ctk.CTkTextbox(
			output_section,
			font=self._mono_font,
			corner_radius=12,
			height=160,
			fg_color=_oc.entry_bg,
			border_width=1,
			border_color=_oc.card_border,
		)
		self.output_text.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
		self.output_text.configure(wrap="word")
		self.output_text.configure(state="disabled")
		self._show_output_placeholder()

		self.error_label = make_label(
			self.container,
			"",
			font=self._hint_font,
			text_color=get_colors().error_text,
			justify="left",
		)
		self.error_label.grid(row=5, column=0, padx=32, pady=(4, 24), sticky="w")

		for row in range(6):
			self.container.grid_rowconfigure(row, weight=0)
		self.container.grid_rowconfigure(2, weight=1)
		self.container.grid_rowconfigure(4, weight=1)

	def render(self, state: SandboxState) -> None:
		if self.mode_selector and state.mode_label in self._label_to_mode:
			self._suppress_mode_callback = True
			try:
				self.mode_selector.set(state.mode_label)
				self._mode_value_var.set(state.mode_label)
			finally:
				self._suppress_mode_callback = False
		if self.input_label:
			self.input_label.configure(text=state.input_label)
		if self.output_label:
			self.output_label.configure(text=state.output_label)

		if self.input_text is not None:
			if state.input_text.strip():
				self._set_input_text(state.input_text)
			else:
				self._show_input_placeholder()

		if self.output_text is not None:
			self._set_output_text(state.output_text)

		self.set_error(state.error_message)

	def read_input_text(self) -> str:
		if not self.input_text:
			return ""
		if self._input_placeholder_active:
			return ""
		return self.input_text.get("1.0", "end").rstrip("\n")

	def clear_input(self) -> None:
		if self.input_text is not None:
			self.input_text.delete("1.0", "end")
			self._show_input_placeholder()
			self.focus_input()

	def set_error(self, message: str | None) -> None:
		if self.error_label is not None:
			self.error_label.configure(text=message or "")

	def _handle_mode_change(self, selected_label: str) -> None:
		if self._suppress_mode_callback:
			return
		mode_key = self._label_to_mode.get(selected_label)
		if mode_key is None:
			return
		self._on_select_mode(mode_key)

	def _show_input_placeholder(self) -> None:
		if not self.input_text:
			return
		self._input_placeholder_active = True
		self.input_text.delete("1.0", "end")
		self.input_text.insert("1.0", self._input_placeholder_text)
		self.input_text.configure(text_color=get_colors().text_placeholder)

	def _set_input_text(self, value: str) -> None:
		if not self.input_text:
			return
		self._input_placeholder_active = False
		self.input_text.delete("1.0", "end")
		self.input_text.insert("1.0", value)
		self.input_text.configure(text_color=get_colors().text_primary)

	def _handle_input_focus_in(self, _event) -> None:
		if not self.input_text:
			return
		if self._input_placeholder_active:
			self.input_text.delete("1.0", "end")
			self.input_text.configure(text_color=get_colors().text_primary)
			self._input_placeholder_active = False

	def _handle_input_focus_out(self, _event) -> None:
		if not self.input_text:
			return
		if not self.input_text.get("1.0", "end").strip():
			self._show_input_placeholder()

	def _handle_input_keypress(self, _event) -> None:
		if not self.input_text:
			return
		if self._input_placeholder_active:
			self.input_text.delete("1.0", "end")
			self.input_text.configure(text_color=get_colors().text_primary)
			self._input_placeholder_active = False

	def focus_input(self) -> None:
		if self.input_text is not None:
			try:
				self.input_text.focus_set()
			except TclError:
				pass

	def _show_output_placeholder(self) -> None:
		if not self.output_text:
			return
		self.output_text.configure(state="normal")
		self.output_text.delete("1.0", "end")
		self.output_text.insert("1.0", self._output_placeholder_text)
		self.output_text.configure(text_color=get_colors().text_placeholder)
		self.output_text.configure(state="disabled")
		self._output_placeholder_active = True

	def _set_output_text(self, value: str) -> None:
		if not self.output_text:
			return
		self.output_text.configure(state="normal")
		self.output_text.delete("1.0", "end")
		if value.strip():
			self.output_text.insert("1.0", value)
			self.output_text.configure(text_color=get_colors().text_primary)
			self._output_placeholder_active = False
		else:
			self.output_text.insert("1.0", self._output_placeholder_text)
			self.output_text.configure(text_color=get_colors().text_placeholder)
			self._output_placeholder_active = True
		self.output_text.configure(state="disabled")


__all__ = ["TranslationSection"]
