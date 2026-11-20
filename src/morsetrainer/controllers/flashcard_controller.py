from __future__ import annotations

import random
from collections.abc import Mapping
from dataclasses import dataclass

from ..exceptions import SessionNotInitializedError
from ..model.flashcard_session import Flashcard, FlashcardSession
from ..model.training import weighted_order
from ..services.progress_store import ProgressStore
from ..strings import t


@dataclass(frozen=True)
class FlashcardState:
	"""Snapshot of the currently displayed flashcard."""

	category: str
	display_text: str
	front_text: str
	back_text: str
	is_back_side: bool
	progress_value: float
	is_first: bool
	is_last: bool
	audio_morse: str | None
	progress_text: str
	has_previous: bool
	next_label: str
	show_audio_button: bool
	can_rate: bool = False


def card_character(card: Flashcard) -> str:
	"""The character a card teaches ("A a" -> "A", "5" -> "5")."""
	return card.front.split()[0] if card.front.split() else card.front


class FlashcardPresenter:
	"""Coordinates flashcard session state for the UI.

	With a progress store, every run starts with the weakest characters more
	likely to come first, and the user can rate each card ("knew it" or not).
	"""

	def __init__(
		self,
		sessions: Mapping[str, FlashcardSession],
		progress: ProgressStore | None = None,
		rng: random.Random | None = None,
	) -> None:
		self._sessions = {name: session for name, session in sessions.items()}
		self._progress = progress
		self._rng = rng or random.Random()
		self._active_category: str | None = None
		self._showing_back = False

	def reset(self) -> None:
		for session in self._sessions.values():
			session.reset()
		self._active_category = None
		self._showing_back = False

	def start(self, category: str) -> FlashcardState | None:
		session = self._sessions.get(category)
		if session is None or session.is_empty():
			return None
		if self._progress is not None:
			progress = self._progress
			session.set_order(
				weighted_order(
					session.cards,
					lambda card: 0.2 + progress.weakness(card_character(card)),
					self._rng,
				)
			)
		session.reset()
		self._active_category = category
		self._showing_back = False
		return self._build_state(session)

	def rate(self, knew_it: bool) -> FlashcardState | None:
		"""Record whether the user knew the current card, then go to the next one."""
		session = self._require_session()
		if self._progress is not None:
			self._progress.record(card_character(session.current()), knew_it)
		return self.next()

	def toggle(self) -> FlashcardState:
		session = self._require_session()
		self._showing_back = not self._showing_back
		return self._build_state(session)

	def next(self) -> FlashcardState | None:
		session = self._require_session()
		if session.is_last():
			return None
		session.move_next()
		self._showing_back = False
		return self._build_state(session)

	def previous(self) -> FlashcardState:
		session = self._require_session()
		if session.move_previous():
			self._showing_back = False
		return self._build_state(session)

	def current_state(self) -> FlashcardState:
		session = self._require_session()
		return self._build_state(session)

	def _build_state(self, session: FlashcardSession) -> FlashcardState:
		card = session.current()
		display_text = card.back if self._showing_back else card.front
		progress_value = session.progress_percentage()
		is_first = session.is_first()
		is_last = session.is_last()
		return FlashcardState(
			category=self._active_category or "",
			display_text=display_text,
			front_text=card.front,
			back_text=card.back,
			is_back_side=self._showing_back,
			progress_value=progress_value,
			is_first=is_first,
			is_last=is_last,
			audio_morse=card.back,
			progress_text=t("common.progress", percent=progress_value),
			has_previous=not is_first,
			next_label=t("common.lopeta_treening") if is_last else t("common.liigu_edasi"),
			show_audio_button=self._showing_back,
			can_rate=self._showing_back and self._progress is not None,
		)

	def _require_session(self) -> FlashcardSession:
		if self._active_category is None:
			raise SessionNotInitializedError("Flashcard category not initialised")
		return self._sessions[self._active_category]
