from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from ..model.test_session import TestResponse, TestSummary
from .theme import CARD_BG, CARD_BORDER, SECTION_BG, TEXT_MUTED
from .test_shared import prepare_backdrop
from .widgets import make_button, make_card, make_font, make_frame, make_label


class TestReviewScreen:
    """Displays per-question breakdown after completing the test."""

    def __init__(
        self,
        root: ctk.CTk,
        clear_screen: Callable[[], None],
        on_back_to_results: Callable[[TestSummary], None],
    ) -> None:
        self.root = root
        self.clear_screen = clear_screen
        self.on_back_to_results = on_back_to_results

        self.summary: TestSummary | None = None
        self.review_index = 0

        self._title_font = make_font(size=32, weight="bold")
        self._body_font = make_font(size=18)
        self._muted_font = make_font(size=16)
        self._callout_font = make_font(size=22, weight="bold", family="Segoe UI Semibold")
        self._counter_font = make_font(size=26, weight="bold", family="Segoe UI Semibold")
        self._feedback_font = make_font(size=20, weight="bold")
        self._question_font = make_font(size=30, weight="bold", family="Consolas")
        self._button_font = make_font(size=18, weight="bold", family="Segoe UI Semibold")

        self.review_meta_label: ctk.CTkLabel | None = None
        self.review_question_label: ctk.CTkLabel | None = None
        self.review_answer_label: ctk.CTkLabel | None = None
        self.review_feedback_label: ctk.CTkLabel | None = None
        self.review_time_label: ctk.CTkLabel | None = None
        self.review_prev_button: ctk.CTkButton | None = None
        self.review_next_button: ctk.CTkButton | None = None

    def reset(self) -> None:
        self.summary = None
        self.review_index = 0
        self.review_meta_label = None
        self.review_question_label = None
        self.review_answer_label = None
        self.review_feedback_label = None
        self.review_time_label = None
        self.review_prev_button = None
        self.review_next_button = None

    def show(self, summary: TestSummary) -> None:
        self.summary = summary
        responses = summary.responses
        if not responses:
            self._return_to_results()
            return

        self.review_index = 0
        self.clear_screen()
        backdrop = prepare_backdrop(self.root)

        card = make_card(backdrop, fg_color=CARD_BG, border_color=CARD_BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.84, relheight=0.84)

        header_box = make_frame(card, fg_color=SECTION_BG, corner_radius=20)
        header_box.pack(pady=(36, 18), padx=36, fill="x")
        header_box.grid_columnconfigure(0, weight=1)
        make_label(header_box, "Läbivaatus", font=self._callout_font).grid(row=0, column=0, pady=(20, 8))
        self.review_meta_label = make_label(header_box, "", font=self._counter_font)
        self.review_meta_label.grid(row=1, column=0, pady=(0, 18))

        question_container = make_frame(card, fg_color=SECTION_BG, corner_radius=20)
        question_container.pack(fill="both", expand=True, padx=32, pady=(0, 24))
        question_container.grid_columnconfigure(0, weight=1)
        question_container.grid_rowconfigure(2, weight=1)

        self.review_question_label = make_label(
            question_container,
            "",
            font=self._question_font,
            wraplength=780,
            justify="center",
        )
        self.review_question_label.grid(row=0, column=0, padx=32, pady=(36, 18), sticky="n")

        self.review_answer_label = make_label(
            question_container,
            "",
            font=self._body_font,
            justify="center",
        )
        self.review_answer_label.grid(row=1, column=0, padx=32, sticky="n")

        self.review_feedback_label = make_label(
            question_container,
            "",
            font=self._feedback_font,
            wraplength=760,
            justify="center",
        )
        self.review_feedback_label.grid(row=2, column=0, padx=32, pady=(24, 12), sticky="nsew")

        self.review_time_label = make_label(
            question_container,
            "",
            font=self._muted_font,
            text_color=TEXT_MUTED,
        )
        self.review_time_label.grid(row=3, column=0, padx=32, pady=(0, 24), sticky="s")

        action_row = make_frame(card, fg_color="transparent")
        action_row.pack(pady=(0, 36))
        action_row.grid_columnconfigure((0, 1), weight=1)

        self.review_prev_button = make_button(
            action_row,
            text="Liigu tagasi",
            command=self._review_previous,
            font=self._button_font,
            variant="muted",
            width=220,
            height=52,
        )
        self.review_prev_button.grid(row=0, column=0, padx=12)

        self.review_next_button = make_button(
            action_row,
            text="Liigu edasi",
            command=self._review_next,
            font=self._button_font,
            variant="primary",
            width=220,
            height=52,
        )
        self.review_next_button.grid(row=0, column=1, padx=12)

        self._update_review_display(responses[0], 0)

    def _review_previous(self) -> None:
        if self.summary is None or self.review_index <= 0:
            return

        self.review_index -= 1
        response = self.summary.responses[self.review_index]
        self._update_review_display(response, self.review_index)

    def _review_next(self) -> None:
        if self.summary is None:
            return

        self.review_index += 1
        if self.review_index >= len(self.summary.responses):
            self._show_complete()
            return

        response = self.summary.responses[self.review_index]
        self._update_review_display(response, self.review_index)

    def _update_review_display(self, response: TestResponse, position: int) -> None:
        question_text = response.prompt
        answer_text = f"Sinu vastus oli: {response.given or '—'}"

        points = response.score
        correct_text = response.expected
        if points == 0:
            feedback = (
                f"See oli vale. Said küsimuse eest {points} punkti.\n\n"
                f"Õige vastus oli hoopis\n{correct_text}."
            )
        elif points == 0.5:
            feedback = (
                f"See oli osaliselt õige. Said küsimuse eest {points} punkti.\n\n"
                f"Õige vastus oli tegelikult\n{correct_text}."
            )
        else:
            feedback = (
                f"See oli täiesti õige. Said küsimuse eest {points} punkti.\n\n"
                f"Õige vastus oli tõepoolest\n{correct_text}."
            )

        elapsed_text = f"Sul kulus küsimuse tõlkimiseks aega {round(response.elapsed, 2)} sekundit."

        total = len(self.summary.responses) if self.summary else 0
        if self.review_meta_label:
            self.review_meta_label.configure(text=f"Küsimus {position + 1}/{total}")
        if self.review_question_label:
            self.review_question_label.configure(text=question_text)
        if self.review_answer_label:
            self.review_answer_label.configure(text=answer_text)
        if self.review_feedback_label:
            self.review_feedback_label.configure(text=feedback)
        if self.review_time_label:
            self.review_time_label.configure(text=elapsed_text)
        self._update_review_navigation(total)

    def _update_review_navigation(self, total: int) -> None:
        if self.review_prev_button is not None:
            prev_state = "normal" if self.review_index > 0 else "disabled"
            self.review_prev_button.configure(state=prev_state)
        if self.review_next_button is not None:
            label = "Liigu edasi" if total == 0 or self.review_index < total - 1 else "Lõpeta läbivaatus"
            self.review_next_button.configure(text=label)

    def _show_complete(self) -> None:
        self.clear_screen()
        backdrop = prepare_backdrop(self.root)

        card = make_card(backdrop, fg_color=CARD_BG, border_color=CARD_BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.68, relheight=0.58)
        card.grid_rowconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=0)
        card.grid_rowconfigure(2, weight=0)
        card.grid_rowconfigure(3, weight=0)
        card.grid_rowconfigure(4, weight=1)
        card.grid_columnconfigure(0, weight=1)

        header_box = make_frame(card, fg_color=SECTION_BG, corner_radius=20)
        header_box.grid(row=1, column=0, padx=36, pady=(0, 16), sticky="ew")
        make_label(header_box, "Läbivaatus lõpetatud", font=self._callout_font).pack(pady=20)

        info_box = make_frame(card, fg_color=SECTION_BG, corner_radius=20)
        info_box.grid(row=2, column=0, padx=36, pady=(0, 12), sticky="ew")
        make_label(
            info_box,
            (
                "Oled kõik küsimused üle vaadanud.\n"
                "Naase tulemuste lehele, et näha kokkuvõtet."
            ),
            font=self._body_font,
            wraplength=500,
        ).pack(padx=28, pady=24)

        button_row = make_frame(card, fg_color="transparent")
        button_row.grid(row=3, column=0, pady=(0, 24))

        make_button(
            button_row,
            text="Lõpeta läbivaatus",
            command=self._return_to_results,
            font=self._button_font,
            variant="primary",
            width=240,
            height=48,
        ).pack()

    def _return_to_results(self) -> None:
        if self.summary is None:
            return
        self.on_back_to_results(self.summary)

