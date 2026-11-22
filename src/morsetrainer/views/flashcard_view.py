from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from ..controllers.flashcard_controller import FlashcardState
from ..controllers.protocols import FlashcardPresenterProtocol
from ..navigator import Navigator
from ..strings import t
from .motion import Animation, tween_color
from .theme import get_colors
from .widgets import (
	font_body,
	font_mono,
	footer_group,
	make_button,
	make_frame,
	make_label,
	make_page,
	make_progress_bar,
	pretty_morse,
	spread_rows,
)

_CATEGORY_TITLES = {
	"tähed": "flashcards.opi_tahti",
	"numbrid": "flashcards.opi_numbreid",
	"märgid": "flashcards.opi_kirjavahemarke",
}


class FlashcardView:
	"""Flashcards: choose a deck, flip cards, rate yourself, listen."""

	def __init__(
		self,
		root,
		nav: Navigator,
		audio_player,
		presenter: FlashcardPresenterProtocol,
	) -> None:
		self.root = root
		self.nav = nav
		self.audio = audio_player
		self.presenter = presenter
		self.state: FlashcardState | None = None
		self._display_font = font_mono(96)
		self._fade: Animation | None = None
		self.reset_state()

	def reset_state(self) -> None:
		self.presenter.reset()
		self.state = None
		self._built = False
		self._peak_progress_value = 0.0
		self.progress_bar: ctk.CTkProgressBar | None = None
		self.progress_label: ctk.CTkLabel | None = None
		self.display_label: ctk.CTkLabel | None = None
		self._display_frame: ctk.CTkFrame | None = None
		self.prev_button: ctk.CTkButton | None = None
		self.next_button: ctk.CTkButton | None = None
		self.audio_button: ctk.CTkButton | None = None
		self._rate_frame: ctk.CTkFrame | None = None
		self.audio.stop()

	def _clear_content(self) -> None:
		for widget in self.root.winfo_children():
			widget.destroy()

	# Menu -----------------------------------------------------------------

	def show_menu(self) -> None:
		"""Choose a deck: letters, numbers or punctuation."""
		self.reset_state()
		self._clear_content()
		page = make_page(
			self.root,
			title=t("flashcards.sumbolitega_tutvumine"),
			subtitle=t("flashcards.vali_kategooria_mida_soovid"),
			back=(t("common.tagasi"), self.nav.learn_hub),
			relwidth=0.7,
		)
		decks = (
			(t("flashcards.opi_tahti"), self.show_letters),
			(t("flashcards.opi_numbreid"), self.show_numbers),
			(t("flashcards.opi_kirjavahemarke"), self.show_symbols),
		)
		spread_rows(page.body, len(decks))
		for row, (label, callback) in enumerate(decks, start=1):
			make_button(page.body, label, command=callback, size="lg", width=320).grid(
				row=row, column=0, pady=10
			)

	# Category views -------------------------------------------------------

	def show_letters(self) -> None:
		self._start_category("tähed", t("flashcards.tahekaartide_andmed_puuduvad"))

	def show_numbers(self) -> None:
		self._start_category("numbrid", t("flashcards.numbrikaartide_andmed_puuduvad"))

	def show_symbols(self) -> None:
		self._start_category("märgid", t("flashcards.kirjavahemarkide_andmed_puuduvad"))

	def _start_category(self, category: str, missing_message: str) -> None:
		state = self.presenter.start(category)
		if state is None:
			self._show_message(missing_message, error=True)
			return
		self.state = state
		self._built = False
		self._render_state()

	def _render_state(self, *, fade: bool = False) -> None:
		if not self.state:
			return
		if not self._built:
			self._build_flashcard_ui(self.state)
		self._update_flashcard_content(self.state, animated=True, fade=fade)

	def _build_flashcard_ui(self, state: FlashcardState) -> None:
		self._clear_content()
		colors = get_colors()
		page = make_page(
			self.root,
			title=t(_CATEGORY_TITLES.get(state.category, "flashcards.sumbolitega_tutvumine")),
			back=(t("common.tagasi_valikute_juurde"), self.show_menu),
		)

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

		# Card face takes all the height; rating row sits right under it.
		page.body.grid_rowconfigure(0, weight=1)
		self._display_frame = make_frame(page.body, fg_color=colors.section_bg, corner_radius=24)
		self._display_frame.grid(row=0, column=0, sticky="nsew", pady=(8, 12))
		self.display_label = make_label(
			self._display_frame, state.display_text, font=self._display_font
		)
		self.display_label.place(relx=0.5, rely=0.5, anchor="center")
		# Clicking the card flips it, like a real card.
		for widget in (self._display_frame, self.display_label):
			widget.bind("<Button-1>", lambda _e: self.toggle_card(), add="+")
			widget.configure(cursor="hand2")

		self._rate_frame = make_frame(page.body)
		self._rate_frame.grid(row=1, column=0, pady=(0, 4))
		make_button(
			self._rate_frame,
			t("flashcards.knew_it"),
			command=lambda: self.rate_card(True),
			variant="positive",
			width=200,
		).grid(row=0, column=0, padx=10)
		make_button(
			self._rate_frame,
			t("flashcards.did_not_know"),
			command=lambda: self.rate_card(False),
			variant="danger",
			width=200,
		).grid(row=0, column=1, padx=10)

		left, center, right = (footer_group(page.footer, c) for c in (0, 1, 2))
		self.prev_button = make_button(
			left, t("common.liigu_tagasi"), command=self.previous_card, variant="secondary"
		)
		self.prev_button.grid(row=0, column=0)
		make_button(center, t("flashcards.poora_kaarti"), command=self.toggle_card, size="lg").grid(
			row=0, column=0
		)
		self.audio_button = make_button(
			center,
			t("flashcards.kuula_heli"),
			command=self.play_flashcard_audio,
			variant="secondary",
		)
		self.audio_button.grid(row=0, column=1, padx=(16, 0))
		self.next_button = make_button(
			right, state.next_label, command=self.next_card, variant="secondary"
		)
		self.next_button.grid(row=0, column=0)
		self._built = True

	def _update_flashcard_content(
		self, state: FlashcardState, *, animated: bool, fade: bool = False
	) -> None:
		colors = get_colors()
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
		if self.display_label:
			text = pretty_morse(state.display_text) if state.is_back_side else state.display_text
			self.display_label.configure(text=text)
			if fade:
				# Flip: the new side fades in from the card colour.
				self._fade = tween_color(
					self.display_label,
					"text_color",
					colors.section_bg,
					colors.text_primary,
					200,
					self._fade,
				)
		if self.prev_button:
			self.prev_button.configure(state="normal" if state.has_previous else "disabled")
		if self.next_button:
			self.next_button.configure(text=state.next_label)
		if self._rate_frame is not None:
			if state.can_rate:
				self._rate_frame.grid()
			else:
				self._rate_frame.grid_remove()
		if self.audio_button:
			if state.show_audio_button and self.audio.available:
				self.audio_button.grid()
			else:
				self.audio_button.grid_remove()

	# Navigation -----------------------------------------------------------

	def toggle_card(self) -> None:
		if not self.state:
			return
		self.state = self.presenter.toggle()
		self._render_state(fade=True)

	def previous_card(self) -> None:
		if not self.state:
			return
		self.state = self.presenter.previous()
		self._render_state(fade=True)

	def rate_card(self, knew_it: bool) -> None:
		if not self.state:
			return
		next_state = self.presenter.rate(knew_it)
		if next_state is None:
			self.flashcard_finish()
			return
		self.state = next_state
		self._render_state(fade=True)

	def next_card(self) -> None:
		if not self.state:
			return
		next_state = self.presenter.next()
		if next_state is None:
			self.flashcard_finish()
			return
		self.state = next_state
		self._render_state(fade=True)

	def play_flashcard_audio(self) -> None:
		if not self.state or not self.state.audio_morse:
			return
		if not self.audio.play_morse(self.state.audio_morse):
			messagebox.showerror(
				t("flashcards.heli"), t("common.heli_ei_onnestunud_esitada"), parent=self.root
			)

	# Completion -----------------------------------------------------------

	def flashcard_finish(self) -> None:
		self.audio.stop()
		self.reset_state()
		self._show_message(t("flashcards.tubli_too_koik_kaardid"), title=t("common.lopp"))

	def _show_message(self, message: str, *, title: str | None = None, error: bool = False) -> None:
		"""A small result page with one OK button back to the deck choice."""
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


__all__ = ["FlashcardView"]
