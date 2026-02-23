from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from ..controllers.test_controller import TestPresenter
from .theme import CARD_BG, CARD_BORDER, SECTION_BG, TEXT_MUTED
from .test_shared import prepare_backdrop
from .widgets import make_button, make_card, make_font, make_frame, make_label


class TestMenuScreen:
    """Landing experience for starting the timed test."""

    def __init__(
        self,
        root: ctk.CTk,
        clear_screen: Callable[[], None],
        presenter: TestPresenter,
        on_home: Callable[[], None],
        on_start: Callable[[], None],
    ) -> None:
        self.root = root
        self.clear_screen = clear_screen
        self.presenter = presenter
        self.on_home = on_home
        self.on_start = on_start

        self._title_font = make_font(size=34, weight="bold")
        self._body_font = make_font(size=18)
        self._callout_font = make_font(size=22, weight="bold", family="Segoe UI Semibold")
        self._button_font = make_font(size=18, weight="bold", family="Segoe UI Semibold")

    def show(self) -> None:
        if self.presenter.total_questions() == 0:
            self._show_empty_state()
            return

        self.clear_screen()
        backdrop = prepare_backdrop(self.root)

        card = make_card(backdrop, fg_color=CARD_BG, border_color=CARD_BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.72, relheight=0.7)

        card.grid_rowconfigure(0, weight=0)
        card.grid_rowconfigure(1, weight=1)
        card.grid_rowconfigure(2, weight=0)
        card.grid_columnconfigure(0, weight=1)

        make_label(card, "Testi ennast", font=self._title_font).grid(row=0, column=0, pady=(36, 10))

        info_container = make_frame(card, fg_color=SECTION_BG, corner_radius=20)
        info_container.grid(row=1, column=0, padx=48, pady=0, sticky="nsew")
        info_container.grid_rowconfigure(0, weight=1)
        info_container.grid_rowconfigure(3, weight=1)
        info_container.grid_columnconfigure(0, weight=1)

        make_label(
            info_container,
            (
                "Oled jõudnud testrežiimi juurde.\n\n"
                "Soorita taimeriga töö, et proovile panna oma morsekoodi oskused.\n\n"
                "Kui oled valmis, alusta testimist või pöördu tagasi kordama."
            ),
            font=self._callout_font,
            wraplength=620,
        ).grid(row=1, column=0, padx=32, pady=(34, 26))

        make_button(
            info_container,
            text="Alusta",
            command=self._show_confirmation,
            font=self._button_font,
            variant="primary",
            width=240,
            height=52,
            corner_radius=16,
        ).grid(row=2, column=0, pady=(8, 36))

        make_button(
            card,
            text="Tagasi avalehele",
            command=self.on_home,
            font=self._button_font,
            variant="danger",
            width=220,
            height=44,
        ).grid(row=2, column=0, pady=(24, 32))

    def _show_empty_state(self) -> None:
        self.clear_screen()
        backdrop = prepare_backdrop(self.root)

        card = make_card(backdrop, fg_color=CARD_BG, border_color=CARD_BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.44)

        make_label(card, "Testi andmed puuduvad", font=self._title_font).pack(pady=(36, 16))
        make_label(
            card,
            "Testrežiimi jaoks pole hetkel ühtegi küsimust saadaval. Palun naase avalehele.",
            font=self._body_font,
            text_color=TEXT_MUTED,
            wraplength=520,
        ).pack(pady=(0, 32), padx=36)

        make_button(
            card,
            text="Tagasi",
            command=self.on_home,
            font=self._button_font,
            variant="primary",
            width=200,
            height=44,
        ).pack()

    def _show_confirmation(self) -> None:
        self.clear_screen()
        backdrop = prepare_backdrop(self.root)

        card = make_card(backdrop, fg_color=CARD_BG, border_color=CARD_BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.64, relheight=0.5)
        card.grid_rowconfigure(0, weight=0)
        card.grid_rowconfigure(1, weight=1)
        card.grid_rowconfigure(2, weight=0)
        card.grid_columnconfigure(0, weight=1)

        make_label(card, "Kas oled valmis?", font=self._title_font).grid(row=0, column=0, pady=(36, 12))

        content = make_frame(card, fg_color="transparent")
        content.grid(row=1, column=0, padx=36, sticky="nsew")
        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(3, weight=1)
        content.grid_columnconfigure(0, weight=1)

        message_box = make_frame(content, fg_color=SECTION_BG, corner_radius=20)
        message_box.grid(row=1, column=0, sticky="ew", pady=(0, 28))
        message_box.grid_columnconfigure(0, weight=1)

        make_label(
            message_box,
            (
                "Testi alustades käivitub taimer ja lahkumine katkestab katse.\n"
                "Soovi korral saad veel kord üle vaadata teised õppemoodulid."
            ),
            font=self._callout_font,
            wraplength=560,
        ).grid(row=0, column=0, padx=28, pady=24, sticky="ew")

        buttons = make_frame(content, fg_color="transparent")
        buttons.grid(row=2, column=0)

        make_button(
            buttons,
            text="Jah, alusta testi",
            command=self.on_start,
            font=self._button_font,
            variant="primary",
            width=220,
            height=48,
        ).grid(row=0, column=0, padx=12, pady=10)

        make_button(
            buttons,
            text="Ei, soovi kordamist",
            command=self.show,
            font=self._button_font,
            variant="danger",
            width=220,
            height=48,
        ).grid(row=0, column=1, padx=12, pady=10)
