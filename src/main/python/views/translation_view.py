from __future__ import annotations

from collections.abc import Callable
from tkinter import TclError

import customtkinter as ctk

from ..controllers.translation_controller import TranslationPresenter, TranslationState
from .theme import BACKDROP_BG, CARD_BG, CARD_BORDER, ERROR_TEXT, SECTION_BG, SUCCESS_TEXT, TEXT_MUTED, TEXT_PRIMARY
from .widgets import make_button, make_card, make_entry, make_font, make_frame, make_label, make_progress_bar


class TranslationView:
    """Encapsulates the translation training interface and interactions."""

    def __init__(
        self,
        root: ctk.CTk,
        clear_screen: Callable[[], None],
        on_home: Callable[[], None],
        on_reset: Callable[[], None],
        pygame_module,
        presenter: TranslationPresenter,
    ) -> None:
        self.root = root
        self.clear_screen = clear_screen
        self.on_home = on_home
        self.on_reset = on_reset
        self.pygame = pygame_module
        self.presenter = presenter

        self.mode: str | None = None
        self.title_text = ""
        self.title_label: ctk.CTkLabel | None = None
        self.progress_bar: ctk.CTkProgressBar | None = None
        self.progress_label: ctk.CTkLabel | None = None
        self.prompt_label: ctk.CTkLabel | None = None
        self._prompt_block: ctk.CTkFrame | None = None
        self.entry: ctk.CTkEntry | None = None
        self.feedback_label: ctk.CTkLabel | None = None
        self.hint_label: ctk.CTkLabel | None = None
        self.hint_button: ctk.CTkButton | None = None
        self.audio_button: ctk.CTkButton | None = None
        self.prev_button: ctk.CTkButton | None = None
        self.next_button: ctk.CTkButton | None = None
        self._failure_count = 0
        self._peak_progress_value = 0.0

        self._title_font = make_font(size=34, weight="bold")
        self._section_font = make_font(size=20)
        self._body_font = make_font(size=18)
        self._button_font = make_font(size=18, weight="bold")
        self._feedback_font = make_font(size=18, weight="semibold")
        self._hint_font = make_font(size=16)
        self._prompt_font_large = make_font(size=44, weight="bold", family="Consolas")
        self._prompt_font_medium = make_font(size=34, weight="bold", family="Consolas")
        self._entry_font = make_font(size=26, weight="bold", family="Consolas")

    def reset_ui(self) -> None:
        """Clear transient widget references so fresh views start clean."""

        self.mode = None
        self.title_text = ""
        self.title_label = None
        self.progress_bar = None
        self.progress_label = None
        self.prompt_label = None
        self._prompt_block = None
        self.entry = None
        self.feedback_label = None
        self.hint_label = None
        self.hint_button = None
        self.audio_button = None
        self.prev_button = None
        self.next_button = None
        self._failure_count = 0
        self._peak_progress_value = 0.0

    def show_menu(self) -> None:
        """Display the translation direction selector."""

        self.pygame.mixer.music.stop()
        self.reset_ui()
        self.clear_screen()
        self._set_root_background(BACKDROP_BG)

        backdrop = make_frame(self.root, fg_color=BACKDROP_BG)
        backdrop.pack(fill="both", expand=True)

        card = make_card(backdrop, fg_color=CARD_BG, border_color=CARD_BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.74, relheight=0.7)

        make_label(card, "Tõlkimise harjutamine", font=self._title_font).pack(pady=(36, 16))

        make_label(
            card,
            "Vali suund, milles soovid tõlkimist harjutada. Saad kasutada vihjeid ning vastuseid kontrollida.",
            font=self._section_font,
            text_color=TEXT_MUTED,
            wraplength=640,
        ).pack(pady=(0, 40))

        buttons = make_frame(card, fg_color="transparent")
        buttons.pack(expand=True)

        for idx, (label, callback) in enumerate(
            (
                ("Tekst → Morse", self.show_text_to_morse),
                ("Morse → tekst", self.show_morse_to_text),
            )
        ):
            make_button(
                buttons,
                text=label,
                command=callback,
                font=self._button_font,
                variant="primary",
                width=260,
                height=66,
                corner_radius=16,
            ).pack(pady=(0 if idx else 12, 18))

        make_button(
            card,
            text="Tagasi avalehele",
            command=self.on_home,
            font=self._button_font,
            variant="danger",
            width=220,
            height=44,
        ).pack(pady=(10, 28))

    def show_text_to_morse(self) -> None:
        self._start_mode("text_to_morse")

    def show_morse_to_text(self) -> None:
        self._start_mode("morse_to_text")

    def _start_mode(self, mode: str) -> None:
        state = self.presenter.start(mode)
        if state is None:
            self.clear_screen()
            self._set_root_background(BACKDROP_BG)

            backdrop = make_frame(self.root, fg_color=BACKDROP_BG)
            backdrop.pack(fill="both", expand=True)

            card = make_card(backdrop, fg_color=CARD_BG, border_color=CARD_BORDER)
            card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.56, relheight=0.4)

            make_label(card, "Andmeid pole", font=self._title_font).pack(pady=(36, 12))
            make_label(
                card,
                "Tõlketreeningu andmed puuduvad. Palun naase menüüsse ja vali muu režiim.",
                font=self._body_font,
                text_color=TEXT_MUTED,
                wraplength=520,
            ).pack(pady=(0, 32), padx=32)

            make_button(
                card,
                text="Tagasi",
                command=self.show_menu,
                font=self._button_font,
                variant="primary",
                width=200,
                height=44,
            ).pack()
            return

        self._show_translation_view(state)

    def _show_translation_view(self, state: TranslationState) -> None:
        previous_mode = self.mode
        rebuild = (
            self.prompt_label is None
            or self.progress_bar is None
            or self.prev_button is None
            or self.next_button is None
            or previous_mode != state.mode
        )

        self.mode = state.mode
        self.title_text = state.title
        self._failure_count = 0
        self.pygame.mixer.music.stop()

        if rebuild:
            self.reset_ui()
            self.mode = state.mode
            self.title_text = state.title
            self._build_translation_ui(state)
            return

        self._update_translation_content(state, animated=True)
        self.entry.focus()  # type: ignore[union-attr]

    def _build_translation_ui(self, state: TranslationState) -> None:
        self.clear_screen()
        self._set_root_background(BACKDROP_BG)

        backdrop = make_frame(self.root, fg_color=BACKDROP_BG)
        backdrop.pack(fill="both", expand=True)

        card = make_card(backdrop, fg_color=CARD_BG, border_color=CARD_BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.82, relheight=0.84)

        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(3, weight=1)

        self.title_label = make_label(card, state.title, font=self._title_font)
        self.title_label.grid(row=0, column=0, pady=(32, 12))

        self.progress_bar = make_progress_bar(
            card,
            root=self.root,
            width=560,
            height=14,
            progress_color=SUCCESS_TEXT,
        )
        self.progress_bar.grid(row=1, column=0, padx=48, pady=(0, 16), sticky="ew")

        self.progress_label = make_label(card, state.progress_text, font=self._body_font, text_color=TEXT_MUTED)
        self.progress_label.grid(row=2, column=0, padx=48, pady=(0, 24))

        self._prompt_block = make_frame(card, fg_color=SECTION_BG, corner_radius=24)
        self._prompt_block.grid(row=3, column=0, padx=48, pady=(0, 28), sticky="nsew")
        self._prompt_block.grid_rowconfigure(0, weight=1)
        self._prompt_block.grid_columnconfigure(0, weight=1)

        prompt_font = self._prompt_font_large if state.prompt_style == "large" else self._prompt_font_medium
        self.prompt_label = make_label(
            self._prompt_block,
            state.prompt,
            font=prompt_font,
            wraplength=420,
        )
        self.prompt_label.grid(row=0, column=0, padx=32, pady=28, sticky="nsew")
        self._prompt_block.update_idletasks()
        self.prompt_label.configure(wraplength=max(self._prompt_block.winfo_width() - 64, 420))

        self.entry = make_entry(
            card,
            font=self._entry_font,
            width=520,
            height=48,
            corner_radius=12,
        )
        self.entry.grid(row=4, column=0, pady=(0, 16))
        self.entry.bind("<Return>", self._on_translation_enter)

        self.feedback_label = make_label(card, "", font=self._feedback_font, text_color=TEXT_MUTED)
        self.feedback_label.grid(row=5, column=0, pady=(0, 12))

        self.hint_label = make_label(card, "", font=self._hint_font)
        self.hint_label.grid(row=6, column=0, pady=(0, 16))

        actions = make_frame(card, fg_color="transparent")
        actions.grid(row=7, column=0, pady=(0, 12))

        make_button(
            actions,
            text="Kontrolli vastust",
            command=self.check_translation_answer,
            font=self._button_font,
            variant="primary",
            width=200,
            height=44,
        ).grid(row=0, column=0, padx=12, pady=10)

        self.hint_button = make_button(
            actions,
            text="Näita vihjet",
            command=self.show_translation_hint,
            font=self._button_font,
            variant="primary",
            width=180,
            height=44,
        )
        self.hint_button.grid(row=0, column=1, padx=12, pady=10)

        self.audio_button = make_button(
            actions,
            text="Esita heli",
            command=self.play_translation_audio,
            font=self._button_font,
            variant="positive",
            width=180,
            height=44,
        )
        self.audio_button.grid(row=0, column=2, padx=12, pady=10)

        navigation = make_frame(card, fg_color="transparent")
        navigation.grid(row=8, column=0, pady=(0, 20))

        self.prev_button = make_button(
            navigation,
            text="Liigu tagasi",
            command=self.translation_previous,
            font=self._button_font,
            variant="muted",
            width=180,
            height=44,
        )
        self.prev_button.grid(row=0, column=0, padx=12, pady=10)

        self.next_button = make_button(
            navigation,
            text=state.next_label,
            command=self.translation_next,
            font=self._button_font,
            variant="secondary",
            width=200,
            height=44,
        )
        self.next_button.grid(row=0, column=1, padx=12, pady=10)

        make_button(
            card,
            text="Tagasi valikute juurde",
            command=self.show_menu,
            font=self._button_font,
            variant="danger",
            width=240,
            height=44,
        ).grid(row=9, column=0, pady=(0, 28))

        self._update_translation_content(state, animated=False)
        self.entry.focus()

    def _update_translation_content(self, state: TranslationState, *, animated: bool) -> None:
        if self.title_label:
            self.title_label.configure(text=state.title)

        if self.progress_bar:
            previous_peak = self._peak_progress_value
            current_value = max(0.0, min(100.0, state.progress_value))
            if current_value > previous_peak:
                self._peak_progress_value = current_value
            display_value = self._peak_progress_value / 100.0
            should_animate = animated and self._peak_progress_value > previous_peak
            self.progress_bar.set_progress(display_value, animated=should_animate)

        if self.progress_label:
            progress_text = f"{self._peak_progress_value:.1f}% läbitud"
            self.progress_label.configure(text=progress_text)

        if self.prompt_label:
            prompt_font = self._prompt_font_large if state.prompt_style == "large" else self._prompt_font_medium
            self.prompt_label.configure(text=state.prompt, font=prompt_font)

        if self._prompt_block and self.prompt_label:
            self._prompt_block.update_idletasks()
            self.prompt_label.configure(wraplength=max(self._prompt_block.winfo_width() - 64, 420))

        if self.entry:
            self.entry.delete(0, "end")

        if self.feedback_label:
            self._set_feedback("", True)

        if self.hint_label:
            self.hint_label.configure(text="")

        if self.hint_button:
            self.hint_button.configure(state="disabled")

        if self.audio_button:
            if state.audio_available:
                self.audio_button.configure(state="normal")
                self.audio_button.grid()
            else:
                self.audio_button.configure(state="disabled")
                self.audio_button.grid_remove()

        if self.prev_button:
            state_value = "normal" if state.has_previous else "disabled"
            self.prev_button.configure(state=state_value)

        if self.next_button:
            self.next_button.configure(text=state.next_label)

        self._failure_count = 0

    def translation_next(self) -> None:
        if not self.mode:
            return
        state = self.presenter.next()
        if state is None:
            self.show_completion()
            return
        self._show_translation_view(state)

    def translation_previous(self) -> None:
        if not self.mode:
            return
        state = self.presenter.previous()
        self._show_translation_view(state)

    def show_translation_hint(self) -> None:
        if not self.mode or not self.hint_label or not self.hint_button:
            return
        if self.hint_button.cget("state") == "disabled":
            return
        self.hint_label.configure(text=f"Vihje: {self.presenter.hint()}")

    def check_translation_answer(self) -> None:
        if not self.mode or not self.entry:
            return

        kasutaja = self.entry.get()
        on_oige, _ = self.presenter.check_answer(kasutaja)

        if on_oige:
            self._set_feedback("Õige vastus! Tubli töö.", True)
            if self.hint_label:
                self.hint_label.configure(text="")
            if self.hint_button:
                self.hint_button.configure(state="disabled")
            self._failure_count = 0
        else:
            self._failure_count += 1
            self._set_feedback("Vale vastus. Proovi uuesti!", False)
            if self._failure_count >= 5 and self.hint_button:
                self.hint_button.configure(state="normal")
                if self.hint_label:
                    self.hint_label.configure(text="Vihje on saadaval, kui soovid.")

    def play_translation_audio(self) -> None:
        audio_path = self.presenter.audio_path()
        if not audio_path:
            self._set_feedback("Sellele kirjele helifaili pole.", False)
            return
        try:
            self.pygame.mixer.music.load(audio_path)
            self.pygame.mixer.music.play()
            self._set_feedback("Helifail esitatakse.", True)
        except self.pygame.error:
            self._set_feedback("Helifaili ei õnnestunud esitada.", False)

    def _set_feedback(self, text: str, success: bool) -> None:
        if not self.feedback_label:
            return
        värv = SUCCESS_TEXT if success else ERROR_TEXT
        self.feedback_label.configure(text=text, text_color=värv)

    def _on_translation_enter(self, _event: object) -> None:
        self.check_translation_answer()

    def show_completion(self) -> None:
        """Display the completion message and reset sessions for a fresh run."""

        self.pygame.mixer.music.stop()
        self.clear_screen()
        self.on_reset()
        self._set_root_background(BACKDROP_BG)

        backdrop = make_frame(self.root, fg_color=BACKDROP_BG)
        backdrop.pack(fill="both", expand=True)

        card = make_card(backdrop, fg_color=CARD_BG, border_color=CARD_BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.62, relheight=0.52)

        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        make_label(card, "Lõpp", font=self._title_font).grid(row=0, column=0, pady=(36, 24))

        message_block = make_frame(card, fg_color=SECTION_BG, corner_radius=28)
        message_block.grid(row=1, column=0, padx=36, pady=(0, 36), sticky="nsew")
        message_block.grid_rowconfigure(0, weight=1)
        message_block.grid_columnconfigure(0, weight=1)

        message_label = make_label(
            message_block,
            "Tubli! Jõudsid lõppu. Vajuta nupul 'OK!', et liikuda tagasi eelmisele lehele.",
            font=make_font(size=22, weight="bold"),
            text_color=TEXT_MUTED,
        )
        message_label.grid(row=0, column=0, padx=32, pady=28, sticky="nsew")
        message_block.update_idletasks()
        message_label.configure(wraplength=max(message_block.winfo_width() - 64, 360))

        button_row = make_frame(card, fg_color="transparent")
        button_row.grid(row=2, column=0, pady=(0, 32))

        make_button(
            button_row,
            text="OK",
            command=self.show_menu,
            font=self._button_font,
            variant="positive",
            width=200,
            height=48,
        ).pack()

        self.reset_ui()

    def _set_root_background(self, color: str) -> None:
        try:
            self.root.configure(fg_color=color)
        except TclError:
            try:
                self.root.configure(bg=color)
            except TclError:
                pass
