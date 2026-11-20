"""Koch-method listening lesson screen."""

from __future__ import annotations

from tkinter import TclError

import customtkinter as ctk

from ..controllers.koch_controller import KochPresenter, KochState
from ..navigator import Navigator
from ..strings import t
from .theme import get_colors
from .widgets import (
	font_mono,
	make_button,
	make_card,
	make_entry,
	make_font,
	make_frame,
	make_label,
)


class KochView:
	"""Hear random groups of the unlocked characters, type them, level up at 90 %."""

	def __init__(self, *, root, nav: Navigator, audio_player, presenter: KochPresenter) -> None:
		self.root = root
		self.nav = nav
		self.audio = audio_player
		self.presenter = presenter
		self._title_font = make_font(size=34, weight="bold")
		self._body_font = make_font(size=18, weight="bold")
		self._hint_font = make_font(size=16)
		self._mono_font = font_mono(28)
		self._button_font = make_font(size=18, weight="bold")
		self.entry: ctk.CTkEntry | None = None
		self._labels: dict[str, ctk.CTkLabel] = {}
		self._play_button: ctk.CTkButton | None = None
		self._check_button: ctk.CTkButton | None = None

	def show(self) -> None:
		self.audio.stop()
		for widget in self.root.winfo_children():
			widget.destroy()
		self._build()
		self._render(self.presenter.current_state())

	# Layout -------------------------------------------------------------------

	def _build(self) -> None:
		colors = get_colors()
		try:
			self.root.configure(fg_color=colors.backdrop_bg)
		except TclError:
			pass
		backdrop = make_frame(self.root, fg_color=colors.backdrop_bg)
		backdrop.pack(fill="both", expand=True)
		card = make_card(backdrop, fg_color=colors.card_bg, border_color=colors.card_border)
		card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.86)

		make_label(card, t("koch.title"), font=self._title_font).pack(pady=(32, 8))
		make_label(
			card,
			t("koch.intro"),
			font=self._hint_font,
			text_color=colors.text_muted,
			wraplength=820,
		).pack(pady=(0, 18))

		self._labels["level"] = make_label(card, "", font=self._body_font)
		self._labels["level"].pack()
		self._labels["chars"] = make_label(card, "", font=self._mono_font)
		self._labels["chars"].pack(pady=(6, 4))
		self._labels["new"] = make_label(
			card, "", font=self._body_font, text_color=colors.text_muted
		)
		self._labels["new"].pack(pady=(0, 16))

		actions = make_frame(card)
		actions.pack(pady=(0, 14))
		make_button(
			actions,
			text=t("koch.listen_new"),
			command=self._play_new_char,
			font=self._button_font,
			variant="secondary",
			width=200,
		).grid(row=0, column=0, padx=8)
		make_button(
			actions,
			text=t("koch.new_exercise"),
			command=self._new_exercise,
			font=self._button_font,
			variant="primary",
			width=200,
		).grid(row=0, column=1, padx=8)
		self._play_button = make_button(
			actions,
			text=t("koch.play_again"),
			command=self._play_exercise,
			font=self._button_font,
			variant="positive",
			width=200,
		)
		self._play_button.grid(row=0, column=2, padx=8)

		self.entry = make_entry(
			card, font=self._mono_font, width=620, placeholder_text=t("koch.entry_placeholder")
		)
		self.entry.pack(pady=(4, 10))
		self.entry.bind("<Return>", lambda _e: self._check())
		self.entry.bind("<KP_Enter>", lambda _e: self._check())

		self._check_button = make_button(
			card,
			text=t("koch.check"),
			command=self._check,
			font=self._button_font,
			variant="primary",
			width=200,
		)
		self._check_button.pack(pady=(0, 10))

		self._labels["result"] = make_label(card, "", font=self._body_font, wraplength=820)
		self._labels["result"].pack(pady=(0, 6))
		self._labels["answer"] = make_label(card, "", font=self._mono_font, wraplength=820)
		self._labels["answer"].pack(pady=(0, 10))

		footer = make_frame(card)
		footer.pack(side="bottom", pady=(0, 24))
		make_button(
			footer,
			text=t("koch.level_down"),
			command=lambda: self._change_level(-1),
			font=self._button_font,
			variant="muted",
			width=150,
		).grid(row=0, column=0, padx=8)
		make_button(
			footer,
			text=t("koch.level_up"),
			command=lambda: self._change_level(1),
			font=self._button_font,
			variant="muted",
			width=150,
		).grid(row=0, column=1, padx=8)
		make_button(
			footer,
			text=t("common.tagasi_avalehele"),
			command=self._go_home,
			font=self._button_font,
			variant="danger",
			width=220,
		).grid(row=0, column=2, padx=8)

	# Rendering ------------------------------------------------------------------

	def _render(self, state: KochState) -> None:
		colors = get_colors()
		self._labels["level"].configure(
			text=t("koch.level", level=state.level, max_level=state.max_level)
		)
		self._labels["chars"].configure(text=" ".join(state.characters))
		self._labels["new"].configure(
			text=t("koch.new_char", char=state.new_char, morse=state.new_char_morse)
		)
		ready = state.has_exercise and self.audio.available
		if self._play_button is not None:
			self._play_button.configure(state="normal" if ready else "disabled")
		if self._check_button is not None:
			self._check_button.configure(state="normal" if state.has_exercise else "disabled")

		result = state.result
		if result is None:
			message = t("koch.no_audio") if not self.audio.available else t("koch.start_hint")
			self._labels["result"].configure(text=message, text_color=colors.text_muted)
			self._labels["answer"].configure(text="")
			return
		percent = round(result.accuracy * 100)
		if state.leveled_up:
			text = t("koch.passed_level_up", percent=percent, char=state.new_char)
		elif state.passed:
			text = t("koch.passed_all", percent=percent)
		else:
			text = t("koch.not_passed", percent=percent)
		color = colors.success_text if state.passed else colors.error_text
		self._labels["result"].configure(text=text, text_color=color)
		self._labels["answer"].configure(
			text=t("koch.correct_answer", text=self.presenter.exercise_text)
		)

	# Actions ----------------------------------------------------------------------

	def _new_exercise(self) -> None:
		state = self.presenter.new_exercise()
		if self.entry is not None:
			self.entry.delete(0, "end")
			self.entry.focus_set()
		self._render(state)
		self._play_exercise()

	def _play_exercise(self) -> None:
		morse = self.presenter.exercise_morse()
		if morse:
			self.audio.play_morse(morse)

	def _play_new_char(self) -> None:
		self.audio.play_morse(self.presenter.new_char_morse())

	def _check(self) -> None:
		if self.entry is None:
			return
		self.audio.stop()
		self._render(self.presenter.check(self.entry.get()))

	def _change_level(self, delta: int) -> None:
		self.audio.stop()
		if self.entry is not None:
			self.entry.delete(0, "end")
		self._render(self.presenter.change_level(delta))

	def _go_home(self) -> None:
		self.audio.stop()
		self.nav.home()


__all__ = ["KochView"]
