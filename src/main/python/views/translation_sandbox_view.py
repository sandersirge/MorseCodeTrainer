from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from tkinter import TclError, filedialog, messagebox

import customtkinter as ctk

from ..controllers.translation_sandbox_controller import (
    SandboxState,
    TranslationSandboxPresenter,
)
from .theme import BACKDROP_BG, CARD_BG, CARD_BORDER, TEXT_MUTED, TEXT_PRIMARY
from .translation_sandbox_sections import AudioSection, TranslationSection
from .widgets import font_body, font_title


def _prepare_backdrop(root) -> ctk.CTkFrame:
    try:
        root.configure(fg_color=BACKDROP_BG)
    except TclError:
        try:
            root.configure(bg=BACKDROP_BG)
        except TclError:
            pass
    backdrop = ctk.CTkFrame(root, fg_color=BACKDROP_BG)
    backdrop.pack(fill="both", expand=True)
    return backdrop


class TranslationSandboxView:
    """Interactive sandbox for ad-hoc Morse translations and audio."""

    def __init__(
        self,
        *,
        root,
        clear_screen: Callable[[], None],
        on_home: Callable[[], None],
        pygame_module,
        presenter: TranslationSandboxPresenter,
    ) -> None:
        self.root = root
        self.clear_screen = clear_screen
        self.on_home = on_home
        self.pygame = pygame_module
        self.presenter = presenter

        self.translation_section: TranslationSection | None = None
        self.audio_section: AudioSection | None = None

    def show(self) -> None:
        if self.audio_section is not None:
            self.audio_section.stop_playback()
        self.clear_screen()

        state = self.presenter.current_state()
        self._build_layout()
        if state is not None:
            self._render_state(state)

    # Layout -----------------------------------------------------------------

    def _build_layout(self) -> None:
        backdrop = _prepare_backdrop(self.root)

        card = ctk.CTkFrame(
            backdrop,
            fg_color=CARD_BG,
            corner_radius=28,
            border_width=1,
            border_color=CARD_BORDER,
        )
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.86)
        card.grid_columnconfigure((0, 1), weight=1)
        card.grid_rowconfigure(2, weight=1)

        self._title_font = font_title()
        self._body_font = font_body()

        ctk.CTkLabel(card, text="Sandbox tõlkimine", font=self._title_font, text_color=TEXT_PRIMARY).grid(
            row=0, column=0, columnspan=2, pady=(36, 16)
        )

        ctk.CTkLabel(
            card,
            text=(
                "Katseta erinevaid tõlkesuundi, muuda helisätteid ning salvesta tulemused."
            ),
            font=self._body_font,
            text_color=TEXT_MUTED,
            wraplength=780,
            justify="center",
        ).grid(row=1, column=0, columnspan=2, padx=64, pady=(0, 24))

        self.translation_section = TranslationSection(
            card,
            on_select_mode=self._on_select_mode,
            on_translate=self._on_translate,
            on_clear=self._on_clear,
        )
        self.translation_section.container.grid(row=2, column=0, sticky="nsew", padx=(40, 18), pady=(0, 36))

        self.audio_section = AudioSection(
            card,
            root=self.root,
            pygame_module=self.pygame,
            on_play=self._on_play_audio,
            on_save=self._on_save_audio,
            on_save_as=self._on_save_audio_as,
            on_volume_change=self._handle_volume_change,
            on_speed_change=self._handle_speed_change,
            on_pitch_change=self._handle_pitch_change,
            on_home=self.on_home,
            on_audio_error=self._show_error,
        )
        self.audio_section.container.grid(row=2, column=1, sticky="nsew", padx=(18, 40), pady=(0, 36))

    # Rendering ---------------------------------------------------------------

    def _render_state(self, state: SandboxState) -> None:
        if self.translation_section is not None:
            self.translation_section.render(state)
        if self.audio_section is not None:
            self.audio_section.render(state)

    # Event handlers ---------------------------------------------------------

    def _on_select_mode(self, mode_key: str) -> None:
        if self.audio_section is not None:
            self.audio_section.stop_playback()
        state = self.presenter.set_mode(mode_key)
        self._render_state(state)

    def _on_translate(self) -> None:
        if self.translation_section is None:
            return
        if self.audio_section is not None:
            self.audio_section.stop_playback()
        text = self.translation_section.read_input_text()
        state = self.presenter.translate(text)
        self._render_state(state)

    def _on_clear(self) -> None:
        if self.translation_section is None:
            return
        if self.audio_section is not None:
            self.audio_section.stop_playback()
        self.translation_section.clear_input()
        state = self.presenter.translate("")
        self._render_state(state)
        self.translation_section.focus_input()

    def _on_play_audio(self) -> None:
        if self.audio_section is None:
            return
        state = self.presenter.current_state()
        if state is None or state.audio_path is None:
            return
        self.audio_section.play_audio(state.audio_path)

    def _on_save_audio(self) -> None:
        if self.audio_section is not None:
            self.audio_section.stop_playback()
        try:
            _, saved_path = self.presenter.save_audio_to_output()
        except ValueError as exc:
            self._show_error(str(exc))
            return
        if self.translation_section is not None:
            self.translation_section.clear_input()
        state = self.presenter.translate("")
        self._render_state(state)
        if self.translation_section is not None:
            self.translation_section.focus_input()
        messagebox.showinfo("Helifail salvestatud", f"Fail salvestatud:\n{saved_path}")

    def _on_save_audio_as(self) -> None:
        if self.audio_section is not None:
            self.audio_section.stop_playback()
        state = self.presenter.current_state()
        if state is None or state.audio_path is None:
            return
        initial_path = Path(state.audio_path)
        selection = filedialog.asksaveasfilename(
            title="Salvesta helifail",
            defaultextension=".wav",
            filetypes=[
                ("WAV helifail", "*.wav"),
                ("Kõik failid", "*.*"),
            ],
            initialdir=str(initial_path.parent),
            initialfile=initial_path.name,
        )
        if not selection:
            return
        try:
            _, saved_path = self.presenter.save_audio_as(Path(selection))
        except ValueError as exc:
            self._show_error(str(exc))
            return
        if self.translation_section is not None:
            self.translation_section.clear_input()
        state = self.presenter.translate("")
        self._render_state(state)
        if self.translation_section is not None:
            self.translation_section.focus_input()
        messagebox.showinfo("Helifail salvestatud", f"Fail salvestatud:\n{saved_path}")

    def _handle_volume_change(self, volume: float) -> None:
        if self.audio_section is not None:
            self.audio_section.stop_playback()
        state = self.presenter.update_volume(volume)
        self._render_state(state)

    def _handle_speed_change(self, unit_duration_ms: int) -> None:
        if self.audio_section is not None:
            self.audio_section.stop_playback()
        state = self.presenter.update_speed(unit_duration_ms)
        self._render_state(state)

    def _handle_pitch_change(self, frequency_hz: float) -> None:
        if self.audio_section is not None:
            self.audio_section.stop_playback()
        state = self.presenter.update_pitch(frequency_hz)
        self._render_state(state)

    def _show_error(self, message: str) -> None:
        if self.translation_section is not None:
            self.translation_section.set_error(message)


__all__ = ["TranslationSandboxView"]
