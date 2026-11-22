"""Koch-method listening lesson screen."""

from __future__ import annotations

import customtkinter as ctk

from ..controllers.koch_controller import KochPresenter, KochState
from ..navigator import Navigator
from ..strings import t
from .motion import tween_color
from .theme import get_colors
from .widgets import (
	accent_color,
	font_body,
	font_mono,
	footer_group,
	make_button,
	make_entry,
	make_frame,
	make_label,
	make_page,
	pretty_morse,
	spread_rows,
)


class KochView:
	"""Hear random groups of the unlocked characters, type them, level up at 90 %."""

	def __init__(self, *, root, nav: Navigator, audio_player, presenter: KochPresenter) -> None:
		self.root = root
		self.nav = nav
		self.audio = audio_player
		self.presenter = presenter
		self._mono_font = font_mono(30)
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
		page = make_page(
			self.root,
			title=t("koch.title"),
			subtitle=t("koch.intro"),
			back=(t("common.tagasi"), self._go_back),
		)
		# Three zones share the height: level, practice, result.
		for row in range(3):
			page.body.grid_rowconfigure(row, weight=1)

		level_zone = make_frame(page.body, fg_color=colors.section_bg, corner_radius=20)
		level_zone.grid(row=0, column=0, sticky="nsew", pady=(4, 10))
		level_zone.grid_columnconfigure(1, weight=1)
		spread_rows(level_zone, 3)
		make_button(
			level_zone,
			t("koch.level_down"),
			command=lambda: self._change_level(-1),
			variant="ghost",
			size="sm",
		).grid(row=1, column=0, rowspan=3, padx=(16, 0))
		self._labels["level"] = make_label(level_zone, "", font=font_body())
		self._labels["level"].grid(row=1, column=1)
		self._labels["chars"] = make_label(
			level_zone, "", font=self._mono_font, text_color=accent_color()
		)
		self._labels["chars"].grid(row=2, column=1, pady=4)
		self._labels["new"] = make_label(
			level_zone, "", font=font_body(), text_color=colors.text_muted
		)
		self._labels["new"].grid(row=3, column=1)
		make_button(
			level_zone,
			t("koch.level_up"),
			command=lambda: self._change_level(1),
			variant="ghost",
			size="sm",
		).grid(row=1, column=2, rowspan=3, padx=(0, 16))

		practice = make_frame(page.body)
		practice.grid(row=1, column=0, sticky="nsew")
		practice.grid_columnconfigure(0, weight=1)
		spread_rows(practice, 2)
		listen = make_frame(practice)
		listen.grid(row=1, column=0, pady=(0, 14))
		make_button(
			listen,
			t("koch.listen_new"),
			command=self._play_new_char,
			variant="secondary",
			width=200,
		).grid(row=0, column=0, padx=10)
		self._play_button = make_button(
			listen,
			t("koch.play_again"),
			command=self._play_exercise,
			variant="secondary",
			width=200,
		)
		self._play_button.grid(row=0, column=1, padx=10)
		self.entry = make_entry(
			practice, font=self._mono_font, width=680, placeholder_text=t("koch.entry_placeholder")
		)
		self.entry.grid(row=2, column=0)
		self.entry.bind("<Return>", lambda _e: self._check())
		self.entry.bind("<KP_Enter>", lambda _e: self._check())

		result = make_frame(page.body)
		result.grid(row=2, column=0, sticky="nsew")
		result.grid_columnconfigure(0, weight=1)
		spread_rows(result, 2)
		self._labels["result"] = make_label(result, "", font=font_body(), wraplength=860)
		self._labels["result"].grid(row=1, column=0, pady=(0, 6))
		self._labels["answer"] = make_label(result, "", font=self._mono_font, wraplength=860)
		self._labels["answer"].grid(row=2, column=0)

		left, center = footer_group(page.footer, 0), footer_group(page.footer, 1)
		make_button(
			left, t("koch.new_exercise"), command=self._new_exercise, variant="secondary"
		).grid(row=0, column=0)
		self._check_button = make_button(center, t("koch.check"), command=self._check, size="lg")
		self._check_button.grid(row=0, column=0)

	# Rendering ------------------------------------------------------------------

	def _render(self, state: KochState) -> None:
		colors = get_colors()
		self._labels["level"].configure(
			text=t("koch.level", level=state.level, max_level=state.max_level)
		)
		self._labels["chars"].configure(text=" ".join(state.characters))
		self._labels["new"].configure(
			text=t("koch.new_char", char=state.new_char, morse=pretty_morse(state.new_char_morse))
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
		self._labels["result"].configure(text=text)
		# The verdict fades in instead of popping up.
		tween_color(self._labels["result"], "text_color", colors.card_bg, color, 260)
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

	def _go_back(self) -> None:
		self.audio.stop()
		self.nav.learn_hub()


__all__ = ["KochView"]
