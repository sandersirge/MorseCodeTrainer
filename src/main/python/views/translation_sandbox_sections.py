from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import customtkinter as ctk
from tkinter import TclError

from ..controllers.translation_sandbox_controller import SandboxState
from .theme import (
    CARD_BG,
    CARD_BORDER,
    ERROR_TEXT,
    SECTION_BG,
    TEXT_MUTED,
    TEXT_PLACEHOLDER,
    TEXT_PRIMARY,
)
from .widgets import (
    font_body,
    font_button_large,
    font_callout,
    font_mono,
    font_muted,
    make_button,
    make_card,
    make_font,
    make_frame,
    make_label,
)

# UI-specific colors not in theme (component styling)
BUTTON_PRIMARY = "#2563eb"
BUTTON_DARK_HOVER = "#141f33"
BUTTON_SEGMENT_BG = "#1a2740"
BUTTON_SEGMENT_SELECTED = "#1e40af"
BUTTON_SEGMENT_HOVER = "#1d4ed8"
TEXTBOX_BG = "#1d2739"
TEXT_ERROR = ERROR_TEXT


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

        self.container = make_card(parent, fg_color=SECTION_BG, border_color=CARD_BORDER, corner_radius=24)
        self.container.columnconfigure(0, weight=1)

        self._title_font = font_callout()
        self._body_font = font_body()
        self._button_font = font_button_large()
        self._hint_font = font_muted()
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
            text_color=TEXT_MUTED,
            wraplength=420,
        )
        intro.grid(row=0, column=0, padx=32, pady=(28, 18))

        mode_card = make_frame(self.container, fg_color="transparent")
        mode_card.grid(row=1, column=0, padx=32, pady=(0, 26), sticky="ew")
        mode_card.columnconfigure(0, weight=1)

        make_label(mode_card, "Tõlkesuund", font=self._body_font, text_color=TEXT_MUTED, justify="left").grid(
            row=0, column=0, pady=(0, 12)
        )

        self.mode_selector = ctk.CTkSegmentedButton(
            mode_card,
            values=list(self._label_to_mode.keys()),
            command=self._handle_mode_change,
            variable=self._mode_value_var,
            font=self._button_font,
            fg_color=BUTTON_SEGMENT_BG,
            selected_color=BUTTON_SEGMENT_SELECTED,
            selected_hover_color=BUTTON_SEGMENT_HOVER,
            unselected_color=BUTTON_SEGMENT_BG,
            unselected_hover_color=BUTTON_DARK_HOVER,
            text_color=TEXT_PRIMARY,
        )
        self.mode_selector.grid(row=1, column=0, sticky="ew")

        input_section = make_frame(self.container, fg_color="transparent")
        input_section.grid(row=2, column=0, padx=32, pady=(0, 24), sticky="nsew")
        input_section.columnconfigure(0, weight=1)
        input_section.rowconfigure(1, weight=1)

        self.input_label = make_label(input_section, "", font=self._body_font, justify="left")
        self.input_label.grid(row=0, column=0, sticky="w")

        self.input_text = ctk.CTkTextbox(
            input_section,
            font=self._mono_font,
            corner_radius=12,
            height=160,
            fg_color=TEXTBOX_BG,
            border_width=1,
            border_color=CARD_BORDER,
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

        self.output_text = ctk.CTkTextbox(
            output_section,
            font=self._mono_font,
            corner_radius=12,
            height=160,
            fg_color=TEXTBOX_BG,
            border_width=1,
            border_color=CARD_BORDER,
        )
        self.output_text.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        self.output_text.configure(wrap="word")
        self.output_text.configure(state="disabled")
        self._show_output_placeholder()

        self.error_label = make_label(
            self.container,
            "",
            font=self._hint_font,
            text_color=TEXT_ERROR,
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
        self.input_text.configure(text_color=TEXT_PLACEHOLDER)

    def _set_input_text(self, value: str) -> None:
        if not self.input_text:
            return
        self._input_placeholder_active = False
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", value)
        self.input_text.configure(text_color=TEXT_PRIMARY)

    def _handle_input_focus_in(self, _event) -> None:
        if not self.input_text:
            return
        if self._input_placeholder_active:
            self.input_text.delete("1.0", "end")
            self.input_text.configure(text_color=TEXT_PRIMARY)
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
            self.input_text.configure(text_color=TEXT_PRIMARY)
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
        self.output_text.configure(text_color=TEXT_PLACEHOLDER)
        self.output_text.configure(state="disabled")
        self._output_placeholder_active = True

    def _set_output_text(self, value: str) -> None:
        if not self.output_text:
            return
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        if value.strip():
            self.output_text.insert("1.0", value)
            self.output_text.configure(text_color=TEXT_PRIMARY)
            self._output_placeholder_active = False
        else:
            self.output_text.insert("1.0", self._output_placeholder_text)
            self.output_text.configure(text_color=TEXT_PLACEHOLDER)
            self._output_placeholder_active = True
        self.output_text.configure(state="disabled")


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
        pygame_module,
        on_play: Callable[[], None],
        on_save: Callable[[], None],
        on_save_as: Callable[[], None],
        on_volume_change: Callable[[float], None],
        on_speed_change: Callable[[int], None],
        on_pitch_change: Callable[[float], None],
        on_home: Callable[[], None],
        on_audio_error: Callable[[str], None],
    ) -> None:
        self.root = root
        self.pygame = pygame_module
        self.on_play = on_play
        self.on_save = on_save
        self.on_save_as = on_save_as
        self.on_volume_change = on_volume_change
        self.on_speed_change = on_speed_change
        self.on_pitch_change = on_pitch_change
        self.on_home = on_home
        self.on_audio_error = on_audio_error

        self.container = make_card(parent, fg_color=SECTION_BG, border_color=CARD_BORDER, corner_radius=24)
        self.container.grid_propagate(False)
        self.container.columnconfigure(0, weight=1)

        self._title_font = font_callout()
        self._body_font = font_body()
        self._button_font = font_button_large()
        self._hint_font = font_muted()

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
        header = make_label(
            self.container,
            "Helisätted ja salvestus",
            font=self._title_font,
            text_color=TEXT_MUTED,
        )
        header.grid(row=0, column=0, padx=32, pady=(28, 18))

        sliders_panel = make_frame(self.container, fg_color="transparent")
        sliders_panel.grid(row=1, column=0, padx=32, sticky="nsew")
        sliders_panel.columnconfigure((0, 1, 2), weight=1)

        self._build_slider(
            sliders_panel,
            column=0,
            key="volume",
            title="Helitugevus",
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
            key="speed",
            title="Kiirus",
            from_value=30,
            to_value=180,
            number_of_steps=30,
            command=self._handle_speed_slider,
            value_from_state=lambda state: state.speed_ms,
            label_from_state=lambda state: f"{state.speed_ms} ms",
        )
        self._build_slider(
            sliders_panel,
            column=2,
            key="pitch",
            title="Kõrgus",
            from_value=200,
            to_value=800,
            number_of_steps=60,
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

        make_label(column_frame, title, font=self._body_font, text_color=TEXT_MUTED, justify="center").grid(
            row=0, column=0, pady=(0, 12)
        )

        slider = ctk.CTkSlider(
            column_frame,
            from_=from_value,
            to=to_value,
            number_of_steps=number_of_steps,
            command=command,
            orientation="vertical",
            fg_color=CARD_BORDER,
            progress_color=BUTTON_PRIMARY,
        )
        slider.grid(row=1, column=0, sticky="ns", pady=6)

        value_label = make_label(column_frame, "", font=self._hint_font, text_color=TEXT_MUTED)
        value_label.grid(row=2, column=0, pady=(12, 0))

        self._slider_bindings[key] = SliderBinding(
            slider=slider,
            value_label=value_label,
            value_from_state=value_from_state,
            label_from_state=label_from_state,
        )

    def render(self, state: SandboxState) -> None:
        self._sync_sliders(state)
        audio_ready = state.audio_ready and state.audio_path is not None

        for button in (
            self.play_audio_button,
            self.save_audio_button,
            self.save_audio_as_button,
        ):
            if button is not None:
                button.configure(state="normal" if audio_ready else "disabled")

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

    def play_audio(self, audio_path: Path) -> bool:
        try:
            self.pygame.mixer.music.load(str(audio_path))
            self.pygame.mixer.music.play()
            self.mark_audio_playing(True)
            return True
        except self.pygame.error:
            self.mark_audio_playing(False)
            self.on_audio_error("Helifaili ei saa esitada.")
            return False

    def stop_playback(self) -> None:
        self.pygame.mixer.music.stop()
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
        if self.pygame.mixer.music.get_busy():
            self._playback_poll_job = self.root.after(200, self._poll_playback_status)
        else:
            self.mark_audio_playing(False)

    def _handle_volume_slider(self, value: float) -> None:
        if self._updating_sliders:
            return
        self.on_volume_change(value / 100.0)

    def _handle_speed_slider(self, value: float) -> None:
        if self._updating_sliders:
            return
        self.on_speed_change(int(round(value)))

    def _handle_pitch_slider(self, value: float) -> None:
        if self._updating_sliders:
            return
        self.on_pitch_change(float(value))

    def _handle_home(self) -> None:
        self.stop_playback()
        self.on_home()


__all__ = ["TranslationSection", "AudioSection"]
