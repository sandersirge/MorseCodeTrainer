"""Straight-key practice: hold Space (or the pad) to send, see what was decoded."""

from __future__ import annotations

import time
from tkinter import TclError

import customtkinter as ctk

from ..controllers.keyer_controller import KeyerPresenter, KeyerState
from ..navigator import Navigator
from ..strings import t
from .motion import Animation, blend, tween_color
from .theme import get_colors
from .widgets import (
	accent_color,
	font_body,
	font_mono,
	font_muted,
	footer_group,
	make_button,
	make_frame,
	make_label,
	make_page,
	pretty_morse,
)

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
		self._target_font = font_mono(40)
		self._mono_font = font_mono(26)
		self._pad_label: ctk.CTkLabel | None = None
		self._pad_fade: Animation | None = None
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
		page = make_page(
			self.root,
			title=t("keyer.title"),
			subtitle=t("keyer.intro"),
			back=(t("common.tagasi"), self._go_back),
		)
		body = page.body
		# Target on top, the key pad fills the middle, what you sent below it.
		body.grid_rowconfigure(1, weight=1)
		target = make_frame(body)
		target.grid(row=0, column=0, pady=(4, 12))
		self._labels["target"] = make_label(target, "", font=self._target_font)
		self._labels["target"].pack()
		self._labels["target_morse"] = make_label(
			target, "", font=self._mono_font, text_color=colors.text_muted
		)
		self._labels["target_morse"].pack()

		self._pad = make_frame(
			body,
			fg_color=colors.section_bg,
			corner_radius=24,
			border_width=2,
			border_color=colors.card_border,
		)
		self._pad.grid(row=1, column=0, sticky="nsew", padx=40, pady=(0, 14))
		self._pad_label = make_label(
			self._pad, t("keyer.pad"), font=font_body(), text_color=colors.text_muted
		)
		self._pad_label.place(relx=0.5, rely=0.5, anchor="center")
		for widget in (self._pad, self._pad_label):
			widget.bind("<ButtonPress-1>", self._on_press)
			widget.bind("<ButtonRelease-1>", self._on_release)
			widget.configure(cursor="hand2")

		sent = make_frame(body)
		sent.grid(row=2, column=0, pady=(0, 4))
		self._labels["sent_morse"] = make_label(sent, "", font=self._mono_font, wraplength=860)
		self._labels["sent_morse"].pack()
		self._labels["sent_text"] = make_label(sent, "", font=self._target_font)
		self._labels["sent_text"].pack()
		self._labels["status"] = make_label(sent, "", font=font_body())
		self._labels["status"].pack(pady=(2, 0))
		self._labels["speed"] = make_label(
			sent, "", font=font_muted(), text_color=colors.text_muted
		)
		self._labels["speed"].pack(pady=(2, 0))

		left, center, right = (footer_group(page.footer, c) for c in (0, 1, 2))
		make_button(left, t("keyer.clear"), command=self._clear, variant="secondary").grid(
			row=0, column=0
		)
		make_button(center, t("keyer.check"), command=self._check, size="lg").grid(row=0, column=0)
		make_button(right, t("keyer.new_word"), command=self._new_word, variant="secondary").grid(
			row=0, column=0
		)

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
		"""Light the pad up while the key is down (fast fade, so keying feels direct)."""
		if self._pad is None:
			return
		colors = get_colors()
		lit = blend(colors.section_bg, accent_color(), 0.28)
		start, end = (colors.section_bg, lit) if active else (lit, colors.section_bg)
		try:
			self._pad.configure(border_color=accent_color() if active else colors.card_border)
			self._pad_fade = tween_color(self._pad, "fg_color", start, end, 60, self._pad_fade)
			self._pad_label.configure(fg_color=end if not active else lit)
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
		self._labels["target_morse"].configure(text=pretty_morse(state.target_morse))
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

	def _go_back(self) -> None:
		self.audio.stop_tone()
		self._unbind_keys()
		if self._tick_job is not None:
			self.root.after_cancel(self._tick_job)
			self._tick_job = None
		self.nav.practice_hub()


__all__ = ["KeyerView"]
