"""Audio controls section for the sandbox view."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from tkinter import TclError

import customtkinter as ctk

from ..controllers.translation_sandbox_controller import SandboxState
from ..services.audio_settings import MAX_FREQUENCY_HZ, MAX_WPM, MIN_FREQUENCY_HZ, MIN_WPM
from .theme import get_colors
from .widgets import (
	font_button_large,
	font_callout,
	make_button,
	make_card,
	make_font,
	make_frame,
	make_label,
)

# Progress bar accent — fixed blue regardless of theme
_SLIDER_PROGRESS_COLOR = "#2563eb"


@dataclass
class SliderBinding:
	slider: ctk.CTkSlider
	value_label: ctk.CTkLabel
	value_from_state: Callable[[SandboxState], float]
	label_from_state: Callable[[SandboxState], str]


class AudioSection:
	"""Right-side audio controls with playback helpers."""

	def __init__(
		self,
		parent,
		*,
		root,
		audio_player,
		on_play: Callable[[], None],
		on_save: Callable[[], None],
		on_save_as: Callable[[], None],
		on_volume_change: Callable[[float], None],
		on_wpm_change: Callable[[int], None],
		on_effective_wpm_change: Callable[[int], None],
		on_pitch_change: Callable[[float], None],
		on_home: Callable[[], None],
		on_audio_error: Callable[[str], None],
	) -> None:
		self.root = root
		self.audio = audio_player
		self.on_play = on_play
		self.on_save = on_save
		self.on_save_as = on_save_as
		self.on_volume_change = on_volume_change
		self.on_wpm_change = on_wpm_change
		self.on_effective_wpm_change = on_effective_wpm_change
		self.on_pitch_change = on_pitch_change
		self.on_home = on_home
		self.on_audio_error = on_audio_error

		_ac = get_colors()
		self.container = make_card(
			parent, fg_color=_ac.section_bg, border_color=_ac.card_border, corner_radius=24
		)
		self.container.grid_propagate(False)
		self.container.columnconfigure(0, weight=1)

		self._title_font = font_callout()
		self._body_font = make_font(size=18, weight="bold")
		self._button_font = font_button_large()
		self._hint_font = make_font(size=16, weight="bold")

		self.play_audio_button: ctk.CTkButton | None = None
		self.stop_audio_button: ctk.CTkButton | None = None
		self.save_audio_button: ctk.CTkButton | None = None
		self.save_audio_as_button: ctk.CTkButton | None = None

		self._slider_bindings: dict[str, SliderBinding] = {}
		self._updating_sliders = False
		self._playback_poll_job: str | None = None
		self._is_audio_playing = False

		self._build()

	def _build(self) -> None:
		header_panel = make_frame(self.container, fg_color="transparent")
		header_panel.grid(row=0, column=0, padx=32, pady=(28, 18))
		make_label(
			header_panel,
			"Helisätted ja salvestus",
			font=self._title_font,
			text_color=get_colors().text_muted,
		).pack()
		make_label(
			header_panel,
			"Kehtivad kõigis harjutustes. Kui üldine kiirus on väiksem, jäävad\n"
			"tähed kiireks, aga vahed pikenevad (Farnsworthi meetod).",
			font=make_font(size=14),
			text_color=get_colors().text_placeholder,
			justify="center",
		).pack(pady=(6, 0))
		if not self.audio.available:
			make_label(
				header_panel,
				"Heliseadet ei leitud: esitamine pole võimalik, salvestamine töötab.",
				font=make_font(size=14, weight="bold"),
				text_color=get_colors().error_text,
				justify="center",
			).pack(pady=(6, 0))

		sliders_panel = make_frame(self.container, fg_color="transparent")
		sliders_panel.grid(row=1, column=0, padx=32, sticky="nsew")
		sliders_panel.columnconfigure((0, 1, 2, 3), weight=1)

		self._build_slider(
			sliders_panel,
			column=0,
			key="volume",
			title="Helitugevus\n",
			from_value=0,
			to_value=100,
			number_of_steps=100,
			command=self._handle_volume_slider,
			value_from_state=lambda state: int(round(state.volume * 100)),
			label_from_state=lambda state: f"{int(round(state.volume * 100))}%",
		)
		self._build_slider(
			sliders_panel,
			column=1,
			key="wpm",
			title="Tähtede\nkiirus",
			from_value=MIN_WPM,
			to_value=MAX_WPM,
			number_of_steps=MAX_WPM - MIN_WPM,
			command=self._handle_wpm_slider,
			value_from_state=lambda state: state.wpm,
			label_from_state=lambda state: f"{state.wpm} WPM",
		)
		self._build_slider(
			sliders_panel,
			column=2,
			key="effective_wpm",
			title="Üldine\nkiirus",
			from_value=MIN_WPM,
			to_value=MAX_WPM,
			number_of_steps=MAX_WPM - MIN_WPM,
			command=self._handle_effective_wpm_slider,
			value_from_state=lambda state: state.effective_wpm,
			label_from_state=lambda state: f"{state.effective_wpm} WPM",
		)
		self._build_slider(
			sliders_panel,
			column=3,
			key="pitch",
			title="Helikõrgus\n",
			from_value=MIN_FREQUENCY_HZ,
			to_value=MAX_FREQUENCY_HZ,
			number_of_steps=int((MAX_FREQUENCY_HZ - MIN_FREQUENCY_HZ) // 10),
			command=self._handle_pitch_slider,
			value_from_state=lambda state: int(round(state.pitch_hz)),
			label_from_state=lambda state: f"{int(round(state.pitch_hz))} Hz",
		)

		playback_panel = make_frame(self.container, fg_color="transparent")
		playback_panel.grid(row=2, column=0, padx=32, pady=(30, 18), sticky="ew")
		playback_panel.columnconfigure((0, 1), weight=1)

		self.play_audio_button = make_button(
			playback_panel,
			text="Esita heli",
			command=self.on_play,
			font=self._button_font,
			variant="positive",
			height=44,
		)
		self.play_audio_button.grid(row=0, column=0, padx=(0, 12), sticky="ew")

		self.stop_audio_button = make_button(
			playback_panel,
			text="Peata heli",
			command=self.stop_playback,
			font=self._button_font,
			variant="danger",
			height=44,
		)
		self.stop_audio_button.grid(row=0, column=1, padx=(12, 0), sticky="ew")

		save_panel = make_frame(self.container, fg_color="transparent")
		save_panel.grid(row=3, column=0, padx=32, sticky="ew")
		save_panel.columnconfigure(0, weight=1)

		self.save_audio_button = make_button(
			save_panel,
			text="Salvesta heli",
			command=self.on_save,
			font=self._button_font,
			variant="secondary",
			height=44,
		)
		self.save_audio_button.grid(row=0, column=0, sticky="ew", pady=(0, 12))

		self.save_audio_as_button = make_button(
			save_panel,
			text="Salvesta nimega...",
			command=self.on_save_as,
			font=self._button_font,
			variant="secondary",
			height=44,
		)
		self.save_audio_as_button.grid(row=1, column=0, sticky="ew")

		navigation_panel = make_frame(self.container, fg_color="transparent")
		navigation_panel.grid(row=4, column=0, padx=32, pady=(28, 28), sticky="ew")
		navigation_panel.columnconfigure(0, weight=1)

		make_button(
			navigation_panel,
			text="Tagasi avalehele",
			command=self._handle_home,
			font=self._button_font,
			variant="danger",
			height=44,
		).grid(row=0, column=0, sticky="ew")

		for row in range(5):
			self.container.grid_rowconfigure(row, weight=0)
		self.container.grid_rowconfigure(1, weight=1)

		self.mark_audio_playing(False)

	def _build_slider(
		self,
		parent,
		*,
		column: int,
		key: str,
		title: str,
		from_value: float,
		to_value: float,
		number_of_steps: int,
		command,
		value_from_state: Callable[[SandboxState], float],
		label_from_state: Callable[[SandboxState], str],
	) -> None:
		column_frame = make_frame(parent, fg_color="transparent")
		column_frame.grid(row=0, column=column, padx=12, sticky="nsew")
		column_frame.columnconfigure(0, weight=1)

		make_label(
			column_frame,
			title,
			font=self._body_font,
			text_color=get_colors().text_muted,
			justify="center",
		).grid(row=0, column=0, pady=(0, 12))
		slider = ctk.CTkSlider(
			column_frame,
			from_=from_value,
			to=to_value,
			number_of_steps=number_of_steps,
			command=command,
			orientation="vertical",
			fg_color=get_colors().card_border,
			progress_color=_SLIDER_PROGRESS_COLOR,
		)
		slider.grid(row=1, column=0, sticky="ns", pady=6)

		value_label = make_label(
			column_frame, "", font=self._hint_font, text_color=get_colors().text_muted
		)
		value_label.grid(row=2, column=0, pady=(12, 0))

		self._slider_bindings[key] = SliderBinding(
			slider=slider,
			value_label=value_label,
			value_from_state=value_from_state,
			label_from_state=label_from_state,
		)

	def render(self, state: SandboxState) -> None:
		self._sync_sliders(state)
		audio_ready = state.audio_ready and state.audio_morse is not None

		for button in (self.save_audio_button, self.save_audio_as_button):
			if button is not None:
				button.configure(state="normal" if audio_ready else "disabled")
		if self.play_audio_button is not None:
			can_play = audio_ready and self.audio.available
			self.play_audio_button.configure(state="normal" if can_play else "disabled")

		if not audio_ready:
			self.mark_audio_playing(False)
		elif self.stop_audio_button is not None and not self._is_audio_playing:
			self.stop_audio_button.configure(state="disabled")

	def _sync_sliders(self, state: SandboxState) -> None:
		if not self._slider_bindings:
			return
		self._updating_sliders = True
		try:
			for binding in self._slider_bindings.values():
				binding.slider.set(binding.value_from_state(state))
				binding.value_label.configure(text=binding.label_from_state(state))
		finally:
			self._updating_sliders = False

	def play_audio(self, morse: str) -> bool:
		if self.audio.play_morse(morse):
			self.mark_audio_playing(True)
			return True
		self.mark_audio_playing(False)
		self.on_audio_error("Heli ei saa esitada.")
		return False

	def stop_playback(self) -> None:
		self.audio.stop()
		self.mark_audio_playing(False)

	def mark_audio_playing(self, is_playing: bool) -> None:
		self._is_audio_playing = is_playing
		if self.stop_audio_button is not None:
			try:
				exists = self.stop_audio_button.winfo_exists()
			except TclError:
				exists = False

			if exists:
				self.stop_audio_button.configure(state="normal" if is_playing else "disabled")
			else:
				self.stop_audio_button = None

		if is_playing:
			if self._playback_poll_job is None:
				self._playback_poll_job = self.root.after(200, self._poll_playback_status)
		else:
			if self._playback_poll_job is not None:
				self.root.after_cancel(self._playback_poll_job)
				self._playback_poll_job = None

	def _poll_playback_status(self) -> None:
		self._playback_poll_job = None
		if self.audio.is_busy():
			self._playback_poll_job = self.root.after(200, self._poll_playback_status)
		else:
			self.mark_audio_playing(False)

	def _handle_volume_slider(self, value: float) -> None:
		if self._updating_sliders:
			return
		self.on_volume_change(value / 100.0)

	def _handle_wpm_slider(self, value: float) -> None:
		if self._updating_sliders:
			return
		self.on_wpm_change(int(round(value)))

	def _handle_effective_wpm_slider(self, value: float) -> None:
		if self._updating_sliders:
			return
		self.on_effective_wpm_change(int(round(value)))

	def _handle_pitch_slider(self, value: float) -> None:
		if self._updating_sliders:
			return
		self.on_pitch_change(float(value))

	def _handle_home(self) -> None:
		self.stop_playback()
		self.on_home()


__all__ = ["AudioSection", "SliderBinding"]
