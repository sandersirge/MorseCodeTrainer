from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from ..model.test_session import TestResponse, TestSummary
from ..strings import t
from .motion import tween_color
from .theme import get_colors
from .widgets import (
	accent_color,
	font_body,
	font_mono,
	font_muted,
	footer_group,
	make_button,
	make_font,
	make_frame,
	make_label,
	make_page,
	pretty_morse,
	spread_rows,
)


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

		self._feedback_font = make_font(size=20, weight="bold")
		self._question_font = font_mono(30)

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
		colors = get_colors()
		page = make_page(
			self.root,
			title=t("review.labivaatus"),
			back=(t("test.tulemused"), self._return_to_results),
		)
		self.review_meta_label = make_label(
			page.header, "", font=font_body(), text_color=accent_color()
		)
		self.review_meta_label.grid(row=2, column=0, pady=(4, 0))

		# Question on top, then your answer, then the verdict; all share the height.
		page.body.grid_rowconfigure(0, weight=2)
		page.body.grid_rowconfigure(1, weight=3)
		question_box = make_frame(page.body, fg_color=colors.section_bg, corner_radius=20)
		question_box.grid(row=0, column=0, sticky="nsew", pady=(8, 12))
		self.review_question_label = make_label(
			question_box, "", font=self._question_font, wraplength=900
		)
		self.review_question_label.place(relx=0.5, rely=0.5, anchor="center")

		verdict = make_frame(page.body)
		verdict.grid(row=1, column=0, sticky="nsew")
		verdict.grid_columnconfigure(0, weight=1)
		spread_rows(verdict, 3)
		self.review_answer_label = make_label(
			verdict, "", font=font_body(), text_color=colors.text_muted
		)
		self.review_answer_label.grid(row=1, column=0, pady=(0, 12))
		self.review_feedback_label = make_label(
			verdict, "", font=self._feedback_font, wraplength=820
		)
		self.review_feedback_label.grid(row=2, column=0, pady=(0, 12))
		self.review_time_label = make_label(
			verdict, "", font=font_muted(), text_color=colors.text_muted
		)
		self.review_time_label.grid(row=3, column=0)

		left, right = footer_group(page.footer, 0), footer_group(page.footer, 2)
		self.review_prev_button = make_button(
			left, t("common.liigu_tagasi"), command=self._review_previous, variant="secondary"
		)
		self.review_prev_button.grid(row=0, column=0)
		self.review_next_button = make_button(
			right, t("common.liigu_edasi"), command=self._review_next, size="lg"
		)
		self.review_next_button.grid(row=0, column=0)

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
		answer_text = t("review.your_answer", answer=response.given or "—")

		points = response.score
		correct_text = response.expected
		if points == 0:
			feedback = t("review.wrong", points=points, expected=correct_text)
		elif points == 0.5:
			feedback = t("review.partial", points=points, expected=correct_text)
		else:
			feedback = t("review.correct", points=points, expected=correct_text)

		elapsed_text = t("review.time_spent", seconds=round(response.elapsed, 2))

		total = len(self.summary.responses) if self.summary else 0
		if self.review_meta_label:
			self.review_meta_label.configure(
				text=t("common.question_counter", number=position + 1, total=total)
			)
		if self.review_question_label:
			self.review_question_label.configure(text=pretty_morse(question_text))
		if self.review_answer_label:
			self.review_answer_label.configure(text=answer_text)
		if self.review_feedback_label:
			colors = get_colors()
			color = (
				colors.error_text
				if points == 0
				else accent_color()
				if points == 0.5
				else colors.success_text
			)
			self.review_feedback_label.configure(text=feedback)
			tween_color(self.review_feedback_label, "text_color", colors.card_bg, color, 220)
		if self.review_time_label:
			self.review_time_label.configure(text=elapsed_text)
		self._update_review_navigation(total)

	def _update_review_navigation(self, total: int) -> None:
		if self.review_prev_button is not None:
			prev_state = "normal" if self.review_index > 0 else "disabled"
			self.review_prev_button.configure(state=prev_state)
		if self.review_next_button is not None:
			label = (
				t("common.liigu_edasi")
				if total == 0 or self.review_index < total - 1
				else t("review.lopeta_labivaatus")
			)
			self.review_next_button.configure(text=label)

	def _show_complete(self) -> None:
		self.clear_screen()
		colors = get_colors()
		page = make_page(
			self.root, title=t("review.labivaatus_lopetatud"), relwidth=0.56, relheight=0.56
		)
		spread_rows(page.body, 2)
		make_label(
			page.body,
			t("review.oled_koik_kusimused_ule"),
			font=font_body(),
			text_color=colors.text_primary,
			wraplength=560,
		).grid(row=1, column=0, pady=(0, 24))
		make_button(
			page.body, t("review.lopeta_labivaatus"), command=self._return_to_results, size="lg"
		).grid(row=2, column=0)

	def _return_to_results(self) -> None:
		if self.summary is None:
			return
		self.on_back_to_results(self.summary)
