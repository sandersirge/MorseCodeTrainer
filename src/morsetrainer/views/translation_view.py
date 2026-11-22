from __future__ import annotations

import customtkinter as ctk

from ..controllers.protocols import TranslationPresenterProtocol
from ..controllers.translation_controller import TranslationState
from ..navigator import Navigator
from ..strings import t
from .motion import Animation, tween_color
from .theme import get_colors
from .widgets import (
	font_body,
	font_mono,
	font_muted,
	footer_group,
	make_button,
	make_entry,
	make_frame,
	make_label,
	make_page,
	make_progress_bar,
	pretty_morse,
	spread_rows,
)

_HINT_AFTER_FAILURES = 5


class TranslationView:
	"""Translation drills: pick a direction and source, then translate item by item."""

	def __init__(
		self,
		root: ctk.CTk,
		nav: Navigator,
		audio_player,
		presenter: TranslationPresenterProtocol,
	) -> None:
		self.root = root
		self.nav = nav
		self.audio = audio_player
		self.presenter = presenter
		self._prompt_font_large = font_mono(44)
		self._prompt_font_medium = font_mono(34)
		self._entry_font = font_mono(26)
		self._feedback_fade: Animation | None = None
		self.reset_ui()

	def reset_ui(self) -> None:
		"""Clear transient widget references so fresh views start clean."""
		self._built = False
		self.mode: str | None = None
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

	def _clear_content(self) -> None:
		for widget in self.root.winfo_children():
			widget.destroy()

	# Menu ---------------------------------------------------------------------

	def show_menu(self) -> None:
		"""Choose the source (fixed sentences / random words) and the direction."""
		self.audio.stop()
		self.reset_ui()
		self._clear_content()
		colors = get_colors()
		page = make_page(
			self.root,
			title=t("translation.tolkimise_harjutamine"),
			subtitle=t("translation.vali_suund_milles_soovid"),
			back=(t("common.tagasi"), self.nav.practice_hub),
			relwidth=0.7,
		)
		spread_rows(page.body, 3)

		sources = {
			t("translation.source_fixed"): "fixed",
			t("translation.source_random"): "random",
		}
		source_toggle = ctk.CTkSegmentedButton(
			page.body,
			values=list(sources),
			command=lambda label: self.presenter.set_source(sources[label]),
			font=font_body(),
			height=40,
			corner_radius=12,
		)
		source_toggle.set(next(k for k, v in sources.items() if v == self.presenter.source))
		source_toggle.grid(row=1, column=0, pady=(0, 6))
		make_label(
			page.body,
			t("translation.source_hint"),
			font=font_muted(),
			text_color=colors.text_muted,
			wraplength=620,
		).grid(row=2, column=0, pady=(0, 36))

		directions = make_frame(page.body)
		directions.grid(row=3, column=0)
		for column, (label, callback) in enumerate(
			(
				(t("common.tekst_morse"), self.show_text_to_morse),
				(t("common.morse_tekst"), self.show_morse_to_text),
			)
		):
			make_button(directions, label, command=callback, size="lg", width=260).grid(
				row=0, column=column, padx=14
			)

	def show_text_to_morse(self) -> None:
		self._start_mode("text_to_morse")

	def show_morse_to_text(self) -> None:
		self._start_mode("morse_to_text")

	def _start_mode(self, mode: str) -> None:
		state = self.presenter.start(mode)
		if state is None:
			self._show_message(
				t("translation.tolketreeningu_andmed_puuduvad_palun"),
				title=t("translation.andmeid_pole"),
				error=True,
			)
			return
		self._show_translation_view(state)

	# Exercise -----------------------------------------------------------------

	def _show_translation_view(self, state: TranslationState) -> None:
		previous_mode = self.mode
		self.mode = state.mode
		self._failure_count = 0
		self.audio.stop()
		if not self._built:
			self._build_translation_ui(state)
			return
		if previous_mode != state.mode:
			self._peak_progress_value = 0.0
		self._update_translation_content(state, animated=True)
		if self.entry is not None:
			self.entry.focus()

	def _build_translation_ui(self, state: TranslationState) -> None:
		self._clear_content()
		colors = get_colors()
		page = make_page(
			self.root,
			title=state.title,
			back=(t("common.tagasi_valikute_juurde"), self.show_menu),
		)
		self.title_label = page.title_label

		progress = make_frame(page.header)
		progress.grid(row=2, column=0, sticky="ew", pady=(10, 0), padx=60)
		progress.grid_columnconfigure(0, weight=1)
		self.progress_bar = make_progress_bar(
			progress, root=self.root, height=10, progress_color=colors.success_text
		)
		self.progress_bar.grid(row=0, column=0, sticky="ew")
		self.progress_label = make_label(
			progress, state.progress_text, font=font_body(), text_color=colors.text_muted
		)
		self.progress_label.grid(row=1, column=0, pady=(6, 0))

		# Prompt takes the spare height; answer area sits below it.
		body = page.body
		body.grid_rowconfigure(0, weight=1)
		self._prompt_block = make_frame(body, fg_color=colors.section_bg, corner_radius=24)
		self._prompt_block.grid(row=0, column=0, sticky="nsew", pady=(8, 16))
		self.prompt_label = make_label(
			self._prompt_block, state.prompt, font=self._prompt_font_medium, wraplength=900
		)
		self.prompt_label.place(relx=0.5, rely=0.5, anchor="center")

		answer = make_frame(body)
		answer.grid(row=1, column=0)
		self.entry = make_entry(
			answer,
			font=self._entry_font,
			width=640,
			height=50,
			corner_radius=12,
			placeholder_text=t("translation.sisesta_morsekood_nt")
			if state.mode == "text_to_morse"
			else t("translation.sisesta_tekst"),
		)
		self.entry.grid(row=0, column=0, columnspan=3)
		self.entry.bind("<Return>", lambda _e: self.check_translation_answer())
		self.entry.bind("<KP_Enter>", lambda _e: self.check_translation_answer())
		self.feedback_label = make_label(answer, " ", font=font_body())
		self.feedback_label.grid(row=1, column=0, columnspan=3, pady=(10, 0))
		self.hint_label = make_label(answer, "", font=font_muted(), text_color=colors.text_muted)
		self.hint_label.grid(row=2, column=0, columnspan=3, pady=(4, 0))

		left, center, right = (footer_group(page.footer, c) for c in (0, 1, 2))
		self.prev_button = make_button(
			left, t("common.liigu_tagasi"), command=self.translation_previous, variant="secondary"
		)
		self.prev_button.grid(row=0, column=0)
		self.hint_button = make_button(
			center,
			t("translation.naita_vihjet"),
			command=self.show_translation_hint,
			variant="secondary",
			width=140,
		)
		self.hint_button.grid(row=0, column=0, padx=(0, 16))
		make_button(
			center,
			t("translation.kontrolli_vastust"),
			command=self.check_translation_answer,
			size="lg",
		).grid(row=0, column=1)
		self.audio_button = make_button(
			center,
			t("common.esita_heli"),
			command=self.play_translation_audio,
			variant="secondary",
			width=140,
		)
		self.audio_button.grid(row=0, column=2, padx=(16, 0))
		self.next_button = make_button(
			right, state.next_label, command=self.translation_next, variant="secondary"
		)
		self.next_button.grid(row=0, column=0)

		self._built = True
		self._update_translation_content(state, animated=False)
		self.entry.focus()

	def _update_translation_content(self, state: TranslationState, *, animated: bool) -> None:
		colors = get_colors()
		if self.title_label:
			self.title_label.configure(text=state.title)
		if self.progress_bar:
			current = max(0.0, min(100.0, state.progress_value))
			grew = current > self._peak_progress_value
			self._peak_progress_value = max(self._peak_progress_value, current)
			self.progress_bar.set_progress(
				self._peak_progress_value / 100.0, animated=animated and grew
			)
		if self.progress_label:
			self.progress_label.configure(
				text=t("common.progress", percent=self._peak_progress_value)
			)
		if self.prompt_label:
			font = (
				self._prompt_font_large
				if state.prompt_style == "large"
				else self._prompt_font_medium
			)
			self.prompt_label.configure(text=pretty_morse(state.prompt), font=font)
			if animated:
				tween_color(
					self.prompt_label, "text_color", colors.section_bg, colors.text_primary, 200
				)
		if self.entry:
			self.entry.delete(0, "end")
		self._set_feedback(" ", True)
		if self.hint_label:
			self.hint_label.configure(text="")
		if self.hint_button:
			self.hint_button.configure(state="disabled")
		if self.audio_button:
			if state.audio_available and self.audio.available:
				self.audio_button.grid()
			else:
				self.audio_button.grid_remove()
		if self.prev_button:
			self.prev_button.configure(state="normal" if state.has_previous else "disabled")
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
		self._show_translation_view(self.presenter.previous())

	def show_translation_hint(self) -> None:
		if not self.mode or not self.hint_label or not self.hint_button:
			return
		if self.hint_button.cget("state") == "disabled":
			return
		self.hint_label.configure(text=t("translation.hint", answer=self.presenter.hint()))

	def check_translation_answer(self) -> None:
		if not self.mode or not self.entry:
			return
		correct, _ = self.presenter.check_answer(self.entry.get())
		if correct:
			self._set_feedback(t("translation.oige_vastus_tubli_too"), True)
			if self.hint_label:
				self.hint_label.configure(text="")
			if self.hint_button:
				self.hint_button.configure(state="disabled")
			self._failure_count = 0
			return
		self._failure_count += 1
		self._set_feedback(t("translation.vale_vastus_proovi_uuesti"), False)
		if self._failure_count >= _HINT_AFTER_FAILURES and self.hint_button:
			self.hint_button.configure(state="normal")
			if self.hint_label:
				self.hint_label.configure(text=t("translation.vihje_on_saadaval_kui"))

	def play_translation_audio(self) -> None:
		morse = self.presenter.audio_morse()
		if not morse:
			self._set_feedback(t("translation.sellele_kirjele_heli_pole"), False)
			return
		if self.audio.play_morse(morse):
			self._set_feedback(t("translation.heli_esitatakse"), True)
		else:
			self._set_feedback(t("common.heli_ei_onnestunud_esitada"), False)

	def _set_feedback(self, text: str, success: bool) -> None:
		"""Feedback fades in from the card colour so it doesn't flash."""
		if not self.feedback_label:
			return
		colors = get_colors()
		color = colors.success_text if success else colors.error_text
		self.feedback_label.configure(text=text)
		self._feedback_fade = tween_color(
			self.feedback_label, "text_color", colors.card_bg, color, 220, self._feedback_fade
		)

	# Completion ---------------------------------------------------------------

	def show_completion(self) -> None:
		"""Show the finish message and reset sessions for a fresh run."""
		self.audio.stop()
		self.nav.reset_translation()
		self.reset_ui()
		self._show_message(t("translation.tubli_joudsid_loppu_vajuta"), title=t("common.lopp"))

	def _show_message(self, message: str, *, title: str, error: bool = False) -> None:
		self._clear_content()
		colors = get_colors()
		page = make_page(self.root, title=title, relwidth=0.56, relheight=0.56)
		spread_rows(page.body, 2)
		make_label(
			page.body,
			message,
			font=font_body(),
			text_color=colors.error_text if error else colors.text_primary,
			wraplength=560,
		).grid(row=1, column=0, pady=(0, 24))
		make_button(page.body, t("common.ok"), command=self.show_menu, size="lg", width=200).grid(
			row=2, column=0
		)


__all__ = ["TranslationView"]
