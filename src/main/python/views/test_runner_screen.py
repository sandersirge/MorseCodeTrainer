from __future__ import annotations

import time
from collections.abc import Callable

import customtkinter as ctk

from ..controllers.test_controller import TestPresenter, TestQuestionState
from ..model.test_session import TestSummary
from .test_shared import prepare_backdrop
from .theme import get_colors, register_theme_callback
from .widgets import (
	make_button,
	make_card,
	make_entry,
	make_font,
	make_frame,
	make_label,
	make_progress_bar,
)


class TestRunnerScreen:
	"""Handles the timed test execution, submission, and results screens."""

	def __init__(
		self,
		root: ctk.CTk,
		clear_screen: Callable[[], None],
		presenter: TestPresenter,
		pygame_module,
		*,
		on_review: Callable[[TestSummary], None],
		on_exit_to_menu: Callable[[], None],
	) -> None:
		self.root = root
		self.clear_screen = clear_screen
		self.presenter = presenter
		self.pygame = pygame_module
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

		self._title_font = make_font(size=32, weight="bold")
		self._subtitle_font = make_font(size=20, weight="bold")
		self._body_font = make_font(size=18)
		self._muted_font = make_font(size=16)
		self._question_font = make_font(size=34, weight="bold", family="Consolas")
		self._button_font = make_font(size=18, weight="bold", family="Segoe UI Semibold")
		self._timer_font = make_font(size=24, weight="bold", family="JetBrains Mono")

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

		register_theme_callback(self._apply_colors)

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
		backdrop = prepare_backdrop(self.root)
		colors = get_colors()

		card = make_card(backdrop, fg_color=colors.card_bg, border_color=colors.card_border)
		card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.82, relheight=0.82)

		card.grid_rowconfigure(1, weight=1)
		card.grid_columnconfigure(0, weight=1)

		make_label(card, "Tulemused", font=self._title_font, text_color=colors.text_primary).grid(
			row=0, column=0, pady=(36, 16)
		)

		result_frame = make_frame(card, fg_color=colors.section_bg, corner_radius=24)
		result_frame.grid(row=1, column=0, padx=48, pady=(0, 28), sticky="nsew")
		result_frame.grid_columnconfigure(0, weight=1)

		make_label(
			result_frame,
			summary.score_text,
			font=self._body_font,
			wraplength=620,
		).grid(row=0, column=0, padx=32, pady=(32, 12))

		make_label(
			result_frame,
			summary.grade_text,
			font=self._subtitle_font,
		).grid(row=1, column=0, padx=32, pady=8)

		make_label(
			result_frame,
			summary.feedback,
			font=self._body_font,
			wraplength=620,
			justify="center",
		).grid(row=2, column=0, padx=32, pady=(8, 18))

		speeds = make_frame(result_frame, fg_color="transparent")
		speeds.grid(row=3, column=0, pady=(6, 24))
		speeds.grid_columnconfigure((0, 1), weight=1)

		make_label(
			speeds,
			f"Sõnade kiirus: {summary.word_speed} sõna/min",
			font=self._muted_font,
			text_color=colors.text_muted,
		).grid(row=0, column=0, padx=12)

		make_label(
			speeds,
			f"Lausete kiirus: {summary.sentence_speed} lauset/min",
			font=self._muted_font,
			text_color=colors.text_muted,
		).grid(row=0, column=1, padx=12)

		button_row = make_frame(card, fg_color="transparent")
		button_row.grid(row=2, column=0, pady=(0, 32))

		make_button(
			button_row,
			text="Vaata vastuseid",
			command=self._review_answers,
			font=self._button_font,
			variant="primary",
			width=220,
			height=48,
		).grid(row=0, column=0, padx=12)

		make_button(
			button_row,
			text="Tagasi menüüsse",
			command=self.on_exit_to_menu,
			font=self._button_font,
			variant="muted",
			width=220,
			height=48,
		).grid(row=0, column=1, padx=12)

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
			self.progress_percent_label.configure(text="0.0% läbitud")
		else:
			self.progress_percent_label = None

		if _alive(self.counter_label):
			self.counter_label.configure(text="Küsimus 0/0")
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
		self._backdrop = prepare_backdrop(self.root)
		colors = get_colors()

		self._card = make_card(
			self._backdrop, fg_color=colors.card_bg, border_color=colors.card_border
		)
		self._card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.86, relheight=0.82)

		self._card.grid_rowconfigure(1, weight=1)
		self._card.grid_columnconfigure(0, weight=1)

		self._header = make_frame(self._card, fg_color="transparent")
		self._header.grid(row=0, column=0, pady=(32, 18), padx=48, sticky="ew")
		self._header.grid_columnconfigure((0, 1, 2), weight=1)

		self.progress_bar = make_progress_bar(
			self._header,
			root=self.root,
			width=520,
			height=14,
			progress_color=colors.success_text,
		)
		self.progress_bar.grid(row=0, column=0, columnspan=3, sticky="ew")

		self.progress_percent_label = make_label(
			self._header, "", font=self._body_font, text_color=colors.text_muted, justify="left"
		)
		self.progress_percent_label.grid(row=1, column=0, sticky="w", pady=(12, 0))

		self.counter_label = make_label(
			self._header, "", font=self._body_font, text_color=colors.text_primary
		)
		self.counter_label.grid(row=1, column=1, pady=(12, 0))

		self.stopwatch_label = make_label(
			self._header,
			self.current_time,
			font=self._timer_font,
			text_color=colors.text_primary,
			justify="right",
		)
		self.stopwatch_label.grid(row=1, column=2, sticky="e", pady=(12, 0))

		self._question_frame = make_frame(self._card, fg_color=colors.section_bg, corner_radius=24)
		self._question_frame.grid(row=1, column=0, padx=48, pady=(0, 24), sticky="nsew")
		self._question_frame.grid_columnconfigure(0, weight=1)
		self._question_frame.grid_rowconfigure(0, weight=1)
		self._question_frame.grid_rowconfigure(1, weight=0)

		self.question_label = make_label(
			self._question_frame,
			"",
			font=self._question_font,
			text_color=colors.text_primary,
			wraplength=780,
		)
		self.question_label.grid(row=0, column=0, padx=36, pady=(36, 24), sticky="nsew")

		input_row = make_frame(self._question_frame, fg_color="transparent")
		input_row.grid(row=1, column=0, padx=36, pady=(0, 24), sticky="ew")
		input_row.grid_columnconfigure(0, weight=1)

		self.answer_entry = make_entry(
			input_row,
			font=self._question_font,
			width=620,
			corner_radius=12,
			placeholder_text="Sisesta vastus siia",
		)
		self.answer_entry.grid(row=0, column=0, sticky="ew")
		self.answer_entry.bind("<Return>", self._handle_submit)

		self._action_row = make_frame(self._card, fg_color="transparent")
		self._action_row.grid(row=2, column=0, pady=(0, 32))

		self.prev_button = make_button(
			self._action_row,
			text="Liigu tagasi",
			command=self._previous_question,
			font=self._button_font,
			variant="muted",
			width=200,
			height=48,
		)
		self.prev_button.grid(row=0, column=0, padx=12)

		self.next_button = make_button(
			self._action_row,
			text="Liigu edasi",
			command=self._next_question,
			font=self._button_font,
			variant="primary",
			width=220,
			height=48,
		)
		self.next_button.grid(row=0, column=1, padx=12)

		make_button(
			self._action_row,
			text="Katkesta test",
			command=self._cancel_test,
			font=self._button_font,
			variant="danger",
			width=220,
			height=48,
		).grid(row=0, column=2, padx=12)

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
			progress_text = f"{self._peak_progress_value:.1f}% läbitud"
			self.progress_percent_label.configure(text=progress_text)

		if self.counter_label:
			self.counter_label.configure(text=f"Küsimus {state.question_number}/{state.total}")

		if self.question_label:
			self.question_label.configure(text=state.prompt)

		if self.answer_entry:
			self.answer_entry.delete(0, "end")
			self.answer_entry.insert(0, state.existing_answer or "")
			self.answer_entry.focus()

		if self.prev_button:
			prev_state = "normal" if state.has_previous else "disabled"
			self.prev_button.configure(state=prev_state)

		if self.next_button:
			next_label = "Liigu edasi" if state.has_next else "Lõpeta test"
			self.next_button.configure(text=next_label)

	def _apply_colors(self) -> None:
		"""Update all widget colors to match the current theme without rebuilding."""
		if not self._built:
			return
		colors = get_colors()

		# Backdrop
		if self._backdrop:
			self._backdrop.configure(fg_color=colors.backdrop_bg)

		# Card
		if self._card:
			self._card.configure(fg_color=colors.card_bg, border_color=colors.card_border)

		# Question frame
		if self._question_frame:
			self._question_frame.configure(fg_color=colors.section_bg)

		# Labels
		if self.progress_percent_label:
			self.progress_percent_label.configure(text_color=colors.text_muted)
		if self.counter_label:
			self.counter_label.configure(text_color=colors.text_primary)
		if self.stopwatch_label:
			self.stopwatch_label.configure(text_color=colors.text_primary)
		if self.question_label:
			self.question_label.configure(text_color=colors.text_primary)

		# Progress bar
		if self.progress_bar:
			self.progress_bar.configure(progress_color=colors.success_text)

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
