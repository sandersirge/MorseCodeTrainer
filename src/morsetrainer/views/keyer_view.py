"""Straight-key practice: hold Space (or the pad) to send, see what was decoded."""

from __future__ import annotations

import time
from tkinter import TclError

import customtkinter as ctk

from ..controllers.keyer_controller import KeyerPresenter, KeyerState
from ..navigator import Navigator
from ..strings import t
from .theme import get_colors
from .widgets import font_mono, make_button, make_card, make_font, make_frame, make_label

# Holding a key auto-repeats. Windows repeats only KeyPress (the decoder ignores
# those); X11 sends KeyRelease+KeyPress pairs, so a release only counts if no
# press follows within this many milliseconds.
_RELEASE_DEBOUNCE_MS = 30
_TICK_MS = 40


class KeyerView:
	"""Key timing is measured here and decoded by the presenter."""

	def __init__(self, *, root, nav: Navigator, audio_player, presenter: KeyerPresenter) -> None:
		self.root = root
		self.nav = nav
		self.audio = audio_player
		self.presenter = presenter
		self._title_font = make_font(size=34, weight="bold")
		self._body_font = make_font(size=18, weight="bold")
		self._hint_font = make_font(size=16)
		self._target_font = font_mono(40)
		self._mono_font = font_mono(26)
		self._button_font = make_font(size=18, weight="bold")
		self._labels: dict[str, ctk.CTkLabel] = {}
		self._pad: ctk.CTkFrame | None = None
		self._pending_release: str | None = None
		self._release_time = 0.0
		self._tick_job: str | None = None
		self._bindings: list[tuple[str, str]] = []

	def show(self) -> None:
		self.audio.stop()
		for widget in self.root.winfo_children():
			widget.destroy()
		self._build()
		self._bind_keys()
		self._render(self.presenter.clear())
		self._schedule_tick()

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

		make_label(card, t("keyer.title"), font=self._title_font).pack(pady=(32, 8))
		make_label(
			card,
			t("keyer.intro"),
			font=self._hint_font,
			text_color=colors.text_muted,
			wraplength=820,
		).pack(pady=(0, 16))

		self._labels["target"] = make_label(card, "", font=self._target_font)
		self._labels["target"].pack()
		self._labels["target_morse"] = make_label(
			card, "", font=self._mono_font, text_color=colors.text_muted
		)
		self._labels["target_morse"].pack(pady=(0, 14))

		self._pad = make_frame(
			card,
			fg_color=colors.section_bg,
			corner_radius=24,
			border_width=2,
			border_color=colors.card_border,
		)
		self._pad.pack(fill="x", padx=120, pady=(0, 14), ipady=18)
		pad_label = make_label(
			self._pad, t("keyer.pad"), font=self._body_font, text_color=colors.text_muted
		)
		pad_label.pack(expand=True, pady=18)
		for widget in (self._pad, pad_label):
			widget.bind("<ButtonPress-1>", self._on_press)
			widget.bind("<ButtonRelease-1>", self._on_release)

		self._labels["sent_morse"] = make_label(card, "", font=self._mono_font, wraplength=860)
		self._labels["sent_morse"].pack(pady=(0, 4))
		self._labels["sent_text"] = make_label(card, "", font=self._target_font)
		self._labels["sent_text"].pack(pady=(0, 4))
		self._labels["status"] = make_label(card, "", font=self._body_font)
		self._labels["status"].pack(pady=(0, 6))
		self._labels["speed"] = make_label(
			card, "", font=self._hint_font, text_color=colors.text_muted
		)
		self._labels["speed"].pack(pady=(0, 10))

		footer = make_frame(card)
		footer.pack(side="bottom", pady=(0, 24))
		for column, (text, command, variant) in enumerate(
			(
				(t("keyer.check"), self._check, "primary"),
				(t("keyer.clear"), self._clear, "muted"),
				(t("keyer.new_word"), self._new_word, "secondary"),
				(t("common.tagasi_avalehele"), self._go_home, "danger"),
			)
		):
			make_button(
				footer,
				text=text,
				command=command,
				font=self._button_font,
				variant=variant,
				width=180,
			).grid(row=0, column=column, padx=8)

	# Key handling -----------------------------------------------------------------

	def _bind_keys(self) -> None:
		top = self.root.winfo_toplevel()
		self._unbind_keys()
		for sequence, handler in (
			("<KeyPress-space>", self._on_press),
			("<KeyRelease-space>", self._on_release),
		):
			self._bindings.append((sequence, top.bind(sequence, handler, add="+")))

	def _unbind_keys(self) -> None:
		top = self.root.winfo_toplevel()
		for sequence, binding_id in self._bindings:
			try:
				top.unbind(sequence, binding_id)
			except TclError:
				pass
		self._bindings.clear()

	def _active(self) -> bool:
		try:
			return bool(self.root.winfo_ismapped())
		except TclError:
			return False

	def _on_press(self, _event=None) -> str | None:
		if not self._active():
			return None
		now = time.monotonic()
		if self._pending_release is not None:
			# Auto-repeat on X11: the "release" was not real, the key is still held.
			self.root.after_cancel(self._pending_release)
			self._pending_release = None
			return "break"
		if not self.presenter.is_key_down:
			self.presenter.key_down(now)
			self.audio.start_tone()
			self._set_pad_active(True)
		return "break"

	def _on_release(self, _event=None) -> str | None:
		if not self._active():
			return None
		self._release_time = time.monotonic()
		if self._pending_release is None:
			self._pending_release = self.root.after(_RELEASE_DEBOUNCE_MS, self._finish_release)
		return "break"

	def _finish_release(self) -> None:
		self._pending_release = None
		self.presenter.key_up(self._release_time)
		self.audio.stop_tone()
		self._set_pad_active(False)
		self._render(self.presenter.current_state())

	def _set_pad_active(self, active: bool) -> None:
		if self._pad is None:
			return
		colors = get_colors()
		try:
			self._pad.configure(border_color=colors.focus_ring if active else colors.card_border)
		except TclError:
			pass

	def _schedule_tick(self) -> None:
		if self._tick_job is not None:
			self.root.after_cancel(self._tick_job)
		self._tick_job = self.root.after(_TICK_MS, self._tick)

	def _tick(self) -> None:
		self._tick_job = None
		if not self._active():
			self._unbind_keys()
			return
		self.presenter.tick(time.monotonic())
		self._render(self.presenter.current_state())
		self._schedule_tick()

	# Rendering ----------------------------------------------------------------------

	def _render(self, state: KeyerState) -> None:
		colors = get_colors()
		self._labels["target"].configure(text=t("keyer.target", word=state.target))
		self._labels["target_morse"].configure(text=state.target_morse)
		self._labels["sent_morse"].configure(text=state.sent_morse or " ")
		self._labels["sent_text"].configure(text=state.sent_text or " ")
		if state.checked:
			self._labels["status"].configure(
				text=t("keyer.correct") if state.correct else t("keyer.wrong"),
				text_color=colors.success_text if state.correct else colors.error_text,
			)
		else:
			self._labels["status"].configure(text=" ")
		speed = t("keyer.speed", wpm=state.wpm)
		if state.estimated_wpm:
			speed += "  ·  " + t("keyer.your_speed", wpm=state.estimated_wpm)
		self._labels["speed"].configure(text=speed)

	# Actions ------------------------------------------------------------------------

	def _check(self) -> None:
		self._render(self.presenter.check())

	def _clear(self) -> None:
		self._render(self.presenter.clear())

	def _new_word(self) -> None:
		self._render(self.presenter.new_target())

	def _go_home(self) -> None:
		self.audio.stop_tone()
		self._unbind_keys()
		if self._tick_job is not None:
			self.root.after_cancel(self._tick_job)
			self._tick_job = None
		self.nav.home()


__all__ = ["KeyerView"]
