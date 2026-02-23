from __future__ import annotations

from collections.abc import Callable
from tkinter import TclError
from tkinter import Tk
from tkinter import messagebox

import customtkinter as ctk

from ..controllers.flashcard_controller import FlashcardPresenter, FlashcardState
from .theme import BACKDROP_BG, CARD_BG, CARD_BORDER, SECTION_BG
from .widgets import make_button, make_card, make_font, make_frame, make_label, make_progress_bar


class FlashcardView:
    """Flashcard-based learning flows (Õpperežiim)."""

    def __init__(
        self,
        root: Tk,
        clear_screen: Callable[[], None],
        on_home: Callable[[], None],
        pygame_module,
        presenter: FlashcardPresenter,
    ) -> None:
        self.root = root
        self.clear_screen = clear_screen
        self.on_home = on_home
        self.pygame = pygame_module
        self.presenter = presenter
        self.state: FlashcardState | None = None
        self._rendered_category: str | None = None
        self.progress_bar: ctk.CTkProgressBar | None = None
        self.progress_label: ctk.CTkLabel | None = None
        self.display_label: ctk.CTkLabel | None = None
        self.prev_button: ctk.CTkButton | None = None
        self.next_button: ctk.CTkButton | None = None
        self.audio_button: ctk.CTkButton | None = None
        self._peak_progress_value = 0.0
        self._title_font = make_font(size=34, weight="bold")
        self._body_font = make_font(size=18)
        self._display_font = make_font(size=78, weight="bold", family="Consolas")
        self._button_font = make_font(size=18, weight="bold")
        self._large_button_font = make_font(size=20, weight="bold")
        self._message_font = make_font(size=22, weight="bold")
        self.reset_state()

    def reset_state(self) -> None:
        self.presenter.reset()
        self.state = None
        self._rendered_category = None
        self.progress_bar = None
        self.progress_label = None
        self.display_label = None
        self.prev_button = None
        self.next_button = None
        self.audio_button = None
        self._peak_progress_value = 0.0
        self.pygame.mixer.music.stop()

    # Menu -----------------------------------------------------------------

    def show_menu(self) -> None:
        """Display the flashcard learning menu."""

        self.reset_state()
        self.clear_screen()
        self._set_root_background(BACKDROP_BG)

        backdrop = make_frame(self.root, fg_color=BACKDROP_BG)
        backdrop.pack(fill="both", expand=True)

        card = make_card(backdrop, fg_color=CARD_BG, border_color=CARD_BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.72, relheight=0.7)

        make_label(card, "Sümbolitega tutvumine", font=self._title_font).pack(pady=(32, 12))
        make_label(
            card,
            "Vali kategooria, mida soovid õppida.",
            font=self._body_font,
            text_color="#cbd5f5",
            wraplength=640,
        ).pack(pady=(10, 40))

        buttons = make_frame(card, fg_color="transparent")
        buttons.pack(expand=True, pady=(0, 24))

        for text, callback in (
            ("Õpi tähti", self.show_letters),
            ("Õpi numbreid", self.show_numbers),
            ("Õpi kirjavahemärke", self.show_symbols),
        ):
            make_button(
                buttons,
                text=text,
                command=callback,
                font=self._large_button_font,
                variant="primary",
                width=260,
                height=66,
                corner_radius=16,
            ).pack(pady=14)

        make_button(
            card,
            text="Tagasi avalehele",
            command=self.on_home,
            font=self._button_font,
            variant="danger",
            width=220,
            height=44,
        ).pack(pady=(10, 24))

    # Category views -------------------------------------------------------

    def show_letters(self) -> None:
        self._start_category("tähed", "Tähekaartide andmed puuduvad.")

    def show_numbers(self) -> None:
        self._start_category("numbrid", "Numbrikaartide andmed puuduvad.")

    def show_symbols(self) -> None:
        self._start_category("märgid", "Kirjavahemärkide andmed puuduvad.")

    def _start_category(self, category: str, missing_message: str) -> None:
        state = self.presenter.start(category)
        if state is None:
            self._show_missing_data(missing_message)
            return
        self.state = state
        self._render_state()

    def _render_state(self) -> None:
        if not self.state:
            return
        state = self.state
        rebuild = (
            self.progress_bar is None
            or self.progress_label is None
            or self.display_label is None
            or self.prev_button is None
            or self.next_button is None
            or self._rendered_category != state.category
        )

        if rebuild:
            self._rendered_category = state.category
            self._build_flashcard_ui(state)
            return

        self._update_flashcard_content(state, animated=True)

    def _show_missing_data(self, message: str) -> None:
        self.clear_screen()
        self._set_root_background(BACKDROP_BG)

        backdrop = make_frame(self.root, fg_color=BACKDROP_BG)
        backdrop.pack(fill="both", expand=True)

        card = make_card(backdrop, fg_color=CARD_BG, border_color=CARD_BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.55, relheight=0.4)

        make_label(card, message, font=self._body_font, text_color="#fca5a5", wraplength=520).pack(pady=(40, 20), padx=32)

        make_button(
            card,
            text="Tagasi",
            command=self.show_menu,
            font=self._button_font,
            variant="primary",
            width=180,
            height=44,
        ).pack()

    def _build_flashcard_ui(self, state: FlashcardState) -> None:
        self.clear_screen()
        self._set_root_background(BACKDROP_BG)

        backdrop = make_frame(self.root, fg_color=BACKDROP_BG)
        backdrop.pack(fill="both", expand=True)

        card = make_card(backdrop, fg_color=CARD_BG, border_color=CARD_BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.78, relheight=0.78)

        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        self.progress_bar = make_progress_bar(
            card,
            root=self.root,
            width=520,
            height=14,
            progress_color="#22c55e",
        )
        self.progress_bar.grid(row=0, column=0, padx=48, pady=(32, 14), sticky="ew")

        self.progress_label = make_label(card, state.progress_text, font=self._body_font, text_color="#cbd5f5")
        self.progress_label.grid(row=1, column=0, padx=48, pady=(0, 24))

        display = make_frame(card, fg_color="#0f172a", corner_radius=20)
        display.grid(row=2, column=0, padx=48, pady=(0, 32), sticky="nsew")
        self.display_label = make_label(display, state.display_text, font=self._display_font)
        self.display_label.pack(expand=True, padx=40, pady=24)

        controls = make_frame(card, fg_color="transparent")
        controls.grid(row=3, column=0, pady=(0, 28))

        make_button(
            controls,
            text="Pööra kaarti",
            command=self.toggle_card,
            font=self._button_font,
            variant="primary",
            width=180,
            height=44,
        ).grid(row=0, column=0, padx=12, pady=10)

        self.prev_button = make_button(
            controls,
            text="Liigu tagasi",
            command=self.previous_card,
            font=self._button_font,
            variant="muted",
            width=180,
            height=44,
        )
        self.prev_button.grid(row=0, column=1, padx=12, pady=10)

        self.next_button = make_button(
            controls,
            text=state.next_label,
            command=self.next_card,
            font=self._button_font,
            variant="secondary",
            width=200,
            height=44,
        )
        self.next_button.grid(row=0, column=2, padx=12, pady=10)

        self.audio_button = make_button(
            controls,
            text="Kuula heli",
            command=self.play_flashcard_audio,
            font=self._button_font,
            variant="positive",
            width=180,
            height=44,
        )
        self.audio_button.grid(row=0, column=3, padx=12, pady=10)

        make_button(
            card,
            text="Tagasi valikute juurde",
            command=self.show_menu,
            font=self._button_font,
            variant="danger",
            width=240,
            height=44,
        ).grid(row=4, column=0, pady=(0, 24))

        self._update_flashcard_content(state, animated=False)

    def _update_flashcard_content(self, state: FlashcardState, *, animated: bool) -> None:
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

        if self.display_label:
            self.display_label.configure(text=state.display_text)

        if self.prev_button:
            prev_state = "normal" if state.has_previous else "disabled"
            self.prev_button.configure(state=prev_state)

        if self.next_button:
            self.next_button.configure(text=state.next_label)

        if self.audio_button:
            if state.show_audio_button:
                self.audio_button.configure(state="normal")
                self.audio_button.grid()
            else:
                self.audio_button.configure(state="disabled")
                self.audio_button.grid_remove()

    # Navigation -----------------------------------------------------------

    def toggle_card(self) -> None:
        if not self.state:
            return
        self.state = self.presenter.toggle()
        self._render_state()

    def previous_card(self) -> None:
        if not self.state:
            return
        self.state = self.presenter.previous()
        self._render_state()

    def next_card(self) -> None:
        if not self.state:
            return
        next_state = self.presenter.next()
        if next_state is None:
            self.flashcard_finish()
            return
        self.state = next_state
        self._render_state()

    def play_flashcard_audio(self) -> None:
        if not self.state or not self.state.audio_path:
            return
        try:
            self.pygame.mixer.music.stop()
            self.pygame.mixer.music.load(self.state.audio_path)
            self.pygame.mixer.music.play()
        except (FileNotFoundError, self.pygame.error):
            messagebox.showerror("Heli", "Helifaili ei õnnestunud esitada.")

    # Completion -----------------------------------------------------------

    def flashcard_finish(self) -> None:
        self.pygame.mixer.music.stop()
        self.reset_state()
        self.clear_screen()
        self._set_root_background(BACKDROP_BG)

        backdrop = make_frame(self.root, fg_color=BACKDROP_BG)
        backdrop.pack(fill="both", expand=True)

        card = make_card(backdrop, fg_color=CARD_BG, border_color=CARD_BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.62, relheight=0.52)

        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        make_label(card, "Lõpp", font=self._title_font).grid(row=0, column=0, pady=(36, 24))

        message_block = make_frame(card, fg_color=SECTION_BG, corner_radius=28)
        message_block.grid(row=1, column=0, padx=36, pady=(0, 36), sticky="nsew")
        message_block.grid_rowconfigure(0, weight=1)
        message_block.grid_columnconfigure(0, weight=1)

        message_label = make_label(
            message_block,
            "Tubli töö! Kõik kaardid on läbitud. Vajuta 'OK', et naasta valikute juurde.",
            font=self._message_font,
            text_color="#cbd5f5",
        )
        message_label.grid(row=0, column=0, padx=32, pady=28, sticky="nsew")
        message_block.update_idletasks()
        message_label.configure(wraplength=max(message_block.winfo_width() - 64, 360))

        button_row = make_frame(card, fg_color="transparent")
        button_row.grid(row=2, column=0, pady=(0, 36))

        make_button(
            button_row,
            text="OK",
            command=self.show_menu,
            font=self._large_button_font,
            variant="positive",
            width=200,
            height=48,
        ).pack()

    # Internal helpers ----------------------------------------------------

    def _set_root_background(self, color: str) -> None:
        try:
            self.root.configure(fg_color=color)
        except TclError:
            try:
                self.root.configure(bg=color)
            except TclError:
                pass
