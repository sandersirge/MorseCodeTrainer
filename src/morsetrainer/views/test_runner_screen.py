from __future__ import annotations

import time
from collections.abc import Callable

import customtkinter as ctk

from ..controllers.protocols import TestPresenterProtocol
from ..controllers.test_controller import TestQuestionState
from ..model.test_session import TestSummary
from ..strings import t
from .theme import get_colors
from .widgets import (
	accent_color,
	font_body,
	font_mono,
	font_muted,
	footer_group,
	make_button,
	make_entry,
	make_font,
	make_frame,
	make_label,
	make_page,
	make_progress_bar,
	pretty_morse,
	spread_rows,
)


class TestRunnerScreen:
	"""Handles the timed test execution, submission, and results screens."""

	def __init__(
		self,
		root: ctk.CTk,
		clear_screen: Callable[[], None],
		presenter: TestPresenterProtocol,
		audio_player,
		*,
		on_review: Callable[[TestSummary], None],
		on_exit_to_menu: Callable[[], None],
	) -> None:
		self.root = root
		self.clear_screen = clear_screen
		self.presenter = presenter
		self.audio = audio_player
		self.on_review = on_review
		self.on_exit_to_menu = on_exit_to_menu

		self.summary: TestSummary | None = None
		self.timer_running = False
		self.timer_job: str | None = None
		self.hours = 0
		self.minutes = 0
		self.seconds = 0
		self.current_time = "00:00:00"
		self.question_started_at = time.time()

		self._grade_font = make_font(size=34, weight="bold")
		self._question_font = font_mono(34)
		self._timer_font = font_mono(24)

		self._built = False
		self._backdrop: ctk.CTkFrame | None = None
		self._card: ctk.CTkFrame | None = None
		self._header: ctk.CTkFrame | None = None
		self._question_frame: ctk.CTkFrame | None = None
		self._action_row: ctk.CTkFrame | None = None
		self.progress_bar: ctk.CTkProgressBar | None = None
		self.progress_percent_label: ctk.CTkLabel | None = None
		self.counter_label: ctk.CTkLabel | None = None
		self.stopwatch_label: ctk.CTkLabel | None = None
		self.question_label: ctk.CTkLabel | None = None
		self.answer_entry: ctk.CTkEntry | None = None
		self.prev_button: ctk.CTkButton | None = None
		self.next_button: ctk.CTkButton | None = None
		self._peak_progress_value = 0.0

	def reset(self) -> None:
		self.presenter.reset()
		self.summary = None
		self._reset_runtime_fields()

	def begin(self) -> None:
		self._reset_runtime_fields()
		self.clear_screen()
		try:
			state = self.presenter.current_state()
		except RuntimeError:
			self.on_exit_to_menu()
			return
		self._ensure_layout()
		self._apply_question_state(state)
		self.question_started_at = time.time()
		self._start_timer()

	def show_results(self, summary: TestSummary) -> None:
		self.summary = summary
		self.clear_screen()
		colors = get_colors()
		page = make_page(self.root, title=t("test.tulemused"), relwidth=0.72)
		spread_rows(page.body, 1)
		result = make_frame(page.body, fg_color=colors.section_bg, corner_radius=24)
		result.grid(row=1, column=0, sticky="ew")
		result.grid_columnconfigure(0, weight=1)
		# Grade first and biggest, then score, feedback and speeds.
		make_label(
			result, summary.grade_text, font=self._grade_font, text_color=accent_color()
		).grid(row=0, column=0, padx=32, pady=(34, 6))
		make_label(result, summary.score_text, font=font_body()).grid(row=1, column=0, pady=(0, 14))
		make_label(
			result, summary.feedback, font=font_body(), text_color=colors.text_muted, wraplength=640
		).grid(row=2, column=0, padx=32, pady=(0, 18))
		speeds = make_frame(result)
		speeds.grid(row=3, column=0, pady=(0, 30))
		for column, text in enumerate(
			(
				t("test.word_speed", speed=summary.word_speed),
				t("test.sentence_speed", speed=summary.sentence_speed),
			)
		):
			make_label(speeds, text, font=font_muted(), text_color=colors.text_muted).grid(
				row=0, column=column, padx=16
			)

		left, right = footer_group(page.footer, 0), footer_group(page.footer, 2)
		make_button(
			left, t("test.tagasi_menuusse"), command=self.on_exit_to_menu, variant="secondary"
		).grid(row=0, column=0)
		make_button(right, t("test.vaata_vastuseid"), command=self._review_answers, size="lg").grid(
			row=0, column=0
		)

	def _reset_runtime_fields(self) -> None:
		self.timer_running = False
		self.timer_job = None
		self.hours = 0
		self.minutes = 0
		self.seconds = 0
		self.current_time = "00:00:00"
		self.question_started_at = time.time()
		self._peak_progress_value = 0.0
		self._built = False

		def _alive(widget) -> bool:
			return widget is not None and bool(widget.winfo_exists())

		if not _alive(self._backdrop):
			self._backdrop = None
		if not _alive(self._card):
			self._card = None
		if not _alive(self._header):
			self._header = None
		if not _alive(self._question_frame):
			self._question_frame = None
		if not _alive(self._action_row):
			self._action_row = None

		if _alive(self.progress_bar):
			self.progress_bar.set_progress(0.0, animated=False)
		else:
			self.progress_bar = None

		if _alive(self.progress_percent_label):
			self.progress_percent_label.configure(text=t("test.progress_zero"))
		else:
			self.progress_percent_label = None

		if _alive(self.counter_label):
			self.counter_label.configure(text=t("test.question_zero"))
		else:
			self.counter_label = None

		if _alive(self.stopwatch_label):
			self.stopwatch_label.configure(text="00:00:00")
		else:
			self.stopwatch_label = None

		if _alive(self.question_label):
			self.question_label.configure(text="")
		else:
			self.question_label = None

		if _alive(self.answer_entry):
			self.answer_entry.delete(0, "end")
		else:
			self.answer_entry = None

	def _review_answers(self) -> None:
		if not self.summary:
			return
		self.on_review(self.summary)

	def _show_question(self, state: TestQuestionState | None) -> None:
		if state is None:
			return

		self.question_started_at = time.time()
		if not self._ensure_layout():
			return
		self._apply_question_state(state)

	def _ensure_layout(self) -> bool:
		if self._built and self.question_label and self.question_label.winfo_exists():
			return True

		self.clear_screen()
		colors = get_colors()
		page = make_page(self.root, title=t("test.testi_ennast"))
		self._card = page.card

		# Progress, question counter and stopwatch in one header row.
		self._header = make_frame(page.header)
		self._header.grid(row=2, column=0, sticky="ew", padx=40, pady=(10, 0))
		self._header.grid_columnconfigure((0, 1, 2), weight=1)
		self.progress_bar = make_progress_bar(
			self._header, root=self.root, height=10, progress_color=colors.success_text
		)
		self.progress_bar.grid(row=0, column=0, columnspan=3, sticky="ew")
		self.progress_percent_label = make_label(
			self._header, "", font=font_body(), text_color=colors.text_muted
		)
		self.progress_percent_label.grid(row=1, column=0, sticky="w", pady=(8, 0))
		self.counter_label = make_label(self._header, "", font=font_body())
		self.counter_label.grid(row=1, column=1, pady=(8, 0))
		self.stopwatch_label = make_label(
			self._header, self.current_time, font=self._timer_font, text_color=accent_color()
		)
		self.stopwatch_label.grid(row=1, column=2, sticky="e", pady=(8, 0))

		# The question takes the spare height; the answer field sits under it.
		page.body.grid_rowconfigure(0, weight=1)
		self._question_frame = make_frame(page.body, fg_color=colors.section_bg, corner_radius=24)
		self._question_frame.grid(row=0, column=0, sticky="nsew", pady=(8, 16))
		self.question_label = make_label(
			self._question_frame, "", font=self._question_font, wraplength=900
		)
		self.question_label.place(relx=0.5, rely=0.5, anchor="center")
		self.answer_entry = make_entry(
			page.body,
			font=self._question_font,
			width=720,
			corner_radius=12,
			placeholder_text=t("test.sisesta_vastus_siia"),
		)
		self.answer_entry.grid(row=1, column=0)
		self.answer_entry.bind("<Return>", self._handle_submit)
		self.answer_entry.bind("<KP_Enter>", self._handle_submit)

		left, center, right = (footer_group(page.footer, c) for c in (0, 1, 2))
		make_button(
			left, t("test.katkesta_test"), command=self._cancel_test, variant="danger"
		).grid(row=0, column=0)
		self.prev_button = make_button(
			center, t("common.liigu_tagasi"), command=self._previous_question, variant="secondary"
		)
		self.prev_button.grid(row=0, column=0)
		self.next_button = make_button(
			right, t("common.liigu_edasi"), command=self._next_question, size="lg"
		)
		self.next_button.grid(row=0, column=0)

		self._built = True
		return True

	def _apply_question_state(self, state: TestQuestionState) -> None:
		if self.progress_bar:
			previous_peak = self._peak_progress_value
			current_value = max(0.0, min(100.0, state.progress_value))
			if current_value > previous_peak:
				self._peak_progress_value = current_value
			progress_ratio = self._peak_progress_value / 100.0
			should_animate = self._peak_progress_value > previous_peak
			self.progress_bar.set_progress(progress_ratio, animated=should_animate)

		if self.progress_percent_label:
			progress_text = t("common.progress", percent=self._peak_progress_value)
			self.progress_percent_label.configure(text=progress_text)

		if self.counter_label:
			self.counter_label.configure(
				text=t("common.question_counter", number=state.question_number, total=state.total)
			)

		if self.question_label:
			self.question_label.configure(text=pretty_morse(state.prompt))

		if self.answer_entry:
			self.answer_entry.delete(0, "end")
			self.answer_entry.insert(0, state.existing_answer or "")
			self.answer_entry.focus()

		if self.prev_button:
			prev_state = "normal" if state.has_previous else "disabled"
			self.prev_button.configure(state=prev_state)

		if self.next_button:
			next_label = t("common.liigu_edasi") if state.has_next else t("test.lopeta_test")
			self.next_button.configure(text=next_label)

	def _handle_submit(self, _event) -> None:
		self._capture_answer()
		self._next_question()

	def _capture_answer(self) -> None:
		if self.answer_entry is None:
			return
		value = self.answer_entry.get()
		self.presenter.record_answer(value, elapsed=self._elapsed_since_question())

	def _elapsed_since_question(self) -> float:
		return round(time.time() - self.question_started_at, 2)

	def _next_question(self) -> None:
		self._capture_answer()
		if not self.presenter.can_move_next():
			self._finalise_test()
			return
		state = self.presenter.move_next()
		self._show_question(state)

	def _previous_question(self) -> None:
		self._capture_answer()
		if not self.presenter.can_move_previous():
			return
		state = self.presenter.move_previous()
		self._show_question(state)

	def _cancel_test(self) -> None:
		self._stop_timer()
		self.on_exit_to_menu()

	def _finalise_test(self) -> None:
		self._stop_timer()
		summary = self.presenter.summary()
		self.show_results(summary)

	def _start_timer(self) -> None:
		if self.timer_running:
			return
		self.timer_running = True
		self._schedule_tick()

	def _schedule_tick(self) -> None:
		if not self.timer_running:
			return
		self.timer_job = self.root.after(1000, self._tick)

	def _tick(self) -> None:
		self.seconds += 1
		if self.seconds == 60:
			self.seconds = 0
			self.minutes += 1
		if self.minutes == 60:
			self.minutes = 0
			self.hours += 1

		self.current_time = f"{self.hours:02}:{self.minutes:02}:{self.seconds:02}"
		if self.stopwatch_label:
			self.stopwatch_label.configure(text=self.current_time)
		self._schedule_tick()

	def _stop_timer(self) -> None:
		self.timer_running = False
		if self.timer_job is not None:
			self.root.after_cancel(self.timer_job)
			self.timer_job = None
