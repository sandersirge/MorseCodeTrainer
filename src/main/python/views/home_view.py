from __future__ import annotations

from collections.abc import Callable
from tkinter import TclError

import customtkinter as ctk

from .theme import BACKDROP_BG, CARD_BG, CARD_BORDER, SECTION_BG, TEXT_MUTED
from .widgets import make_button, make_card, make_font, make_frame, make_label


class HomeView:
    """Renders the landing screen using shared widget helpers."""

    def __init__(
        self,
        root,
        clear_screen: Callable[[], None],
        *,
        on_tutvustus: Callable[[], None],
        on_flashcards: Callable[[], None],
        on_translation: Callable[[], None],
        on_translation_sandbox: Callable[[], None],
        on_test: Callable[[], None],
        on_exit: Callable[[], None],
    ) -> None:
        self.root = root
        self.clear_screen = clear_screen
        self.on_tutvustus = on_tutvustus
        self.on_flashcards = on_flashcards
        self.on_translation = on_translation
        self.on_translation_sandbox = on_translation_sandbox
        self.on_test = on_test
        self.on_exit = on_exit
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self._hero_frame: ctk.CTkFrame | None = None

    def show(self) -> None:
        self.clear_screen()
        try:
            self.root.configure(fg_color=BACKDROP_BG)
        except TclError:
            try:
                self.root.configure(bg=BACKDROP_BG)
            except TclError:
                pass

        backdrop = make_frame(self.root, fg_color=BACKDROP_BG)
        backdrop.pack(fill="both", expand=True)

        hero = make_card(backdrop, fg_color=CARD_BG, border_color=CARD_BORDER)
        hero.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.62, relheight=0.62)
        self._hero_frame = hero

        make_label(hero, "Morsekoodi rakendus", font_size=38, weight="bold").pack(pady=(36, 8))

        make_label(
            hero,
            "Programm morsekoodi õppimiseks, harjutamiseks ja testimiseks ning tõlkimiseks.",
            font_size=18,
            text_color=TEXT_MUTED,
        ).pack(pady=(0, 24))

        buttons_frame = make_frame(hero, fg_color="transparent")
        buttons_frame.pack(pady=(0, 24))

        menu_items = [
            ("Tutvustus", self.on_tutvustus),
            ("Õpe", self.on_flashcards),
            ("Harjutused", self.on_translation),
            ("Test", self.on_test),
            ("Sandbox", self.on_translation_sandbox),
        ]

        for label, callback in menu_items:
            make_button(
                buttons_frame,
                text=label,
                command=callback,
                font_size=20,
                variant="primary",
                width=240,
                height=48,
                corner_radius=14,
            ).pack(pady=10)

        footer = make_frame(hero, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=28, pady=28)

        make_button(
            footer,
            text="Välju programmist",
            command=self.on_exit,
            font_size=18,
            variant="danger",
            width=220,
            height=44,
            corner_radius=14,
        ).pack(side="right")


class IntroductionView:
    """Displays the introduction content using shared helpers."""

    def __init__(
        self,
        root,
        clear_screen: Callable[[], None],
        *,
        on_back: Callable[[], None],
    ) -> None:
        self.root = root
        self.clear_screen = clear_screen
        self.on_back = on_back

    def show(self) -> None:
        self.clear_screen()
        try:
            self.root.configure(fg_color=BACKDROP_BG)
        except TclError:
            try:
                self.root.configure(bg=BACKDROP_BG)
            except TclError:
                pass

        backdrop = make_frame(self.root, fg_color=BACKDROP_BG)
        backdrop.pack(fill="both", expand=True)

        card = make_card(backdrop, fg_color=CARD_BG, border_color=CARD_BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.68, relheight=0.68)

        make_label(card, "Tutvustus", font_size=34, weight="bold").pack(pady=(36, 24))

        first_block = make_frame(card, fg_color=SECTION_BG, corner_radius=28)
        first_block.pack(padx=36, pady=(0, 36), fill="x")

        first_text = make_label(
            first_block,
            (
                "Morsekood mõõdab aega 'ühikutes': punkt kestab ühe ühiku, kriips kolm ühikut. "
                "Sümboli sees eraldab kahe signaali vahelist pausi ühe ühiku pikkune vaikuse segment. "
                "Sümbolite vahel hoitakse kolme ühiku pikkust pausi ja sõnade vahel seitset ühikut. "
                "Tekstina kirjutades tähistatakse signaale punktide ja sidekriipsudega (näiteks . ja -). Ühe ühiku pikkune paus "
                "pole kuvatud, sümbolite vahe tähistatakse ühe tühiku abil ning sõnade vahel on kolm tühikut tühja ala."
            ),
            font_size=20,
            weight="bold",
            text_color=TEXT_MUTED,
            justify="left",
            anchor="w",
        )
        first_text.pack(padx=36, pady=28, fill="x")
        first_block.update_idletasks()
        first_text.configure(wraplength=first_block.winfo_width() - 72)

        second_block = make_frame(card, fg_color=SECTION_BG, corner_radius=28)
        second_block.pack(padx=36, pady=(0, 36), fill="x")

        second_text = make_label(
            second_block,
            (
                "Õpe võimaldab Flashcard meetodi abil süsteemselt läbi käia tähed, numbrid ja kirjavahemärgid ning kuulata nende helinäiteid. "
                "Tõlkimises saab harjutada keerulisemaid näiteid mõlemas suunas: tekst → morse ja morse → tekst; "
                "lisaks saab vihjeid ja kontrollida vastuseid. Testis käivitatakse taimeriga töö, mille lõpus saab põhjaliku tagasiside ning võimaluse vastused üle vaadata."
            ),
            font_size=20,
            weight="bold",
            text_color=TEXT_MUTED,
            justify="left",
            anchor="w",
        )
        second_text.pack(padx=36, pady=28, fill="x")
        second_block.update_idletasks()
        second_text.configure(wraplength=second_block.winfo_width() - 72)

        button_row = make_frame(card, fg_color="transparent")
        button_row.pack(pady=(0, 36))

        make_button(
            button_row,
            text="Tagasi avalehele",
            command=self.on_back,
            font_size=18,
            variant="danger",
            width=220,
            height=44,
            corner_radius=14,
        ).pack()