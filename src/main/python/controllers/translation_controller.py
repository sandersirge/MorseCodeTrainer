from __future__ import annotations

from dataclasses import dataclass

from ..exceptions import SessionNotInitializedError
from ..model.translation_session import TranslationSession
from ..strings import t
from ..utils.morse_translator import normalize_morse


@dataclass(frozen=True)
class TranslationState:
	"""Snapshot of translation training state for rendering in the view."""

	mode: str
	title: str
	prompt: str
	index: int
	total: int
	progress_value: float
	progress_step: float
	is_first: bool
	is_last: bool
	audio_morse: str | None
	progress_text: str
	has_previous: bool
	next_label: str
	prompt_style: str
	audio_available: bool


class TranslationPresenter:
	"""Encapsulates translation-session behaviour for the UI layer."""

	_TITLES = {
		"text_to_morse": t("common.tekst_morse"),
		"morse_to_text": t("common.morse_tekst"),
	}

	def __init__(
		self,
		morse_session: TranslationSession,
		text_session: TranslationSession,
	) -> None:
		self._sessions = {
			"morse_to_text": morse_session,
			"text_to_morse": text_session,
		}
		self._active_mode: str | None = None

	def reset(self) -> None:
		"""Reset sessions so a fresh training run can begin."""

		for session in self._sessions.values():
			session.reset()
		self._active_mode = None

	def start(self, mode: str) -> TranslationState | None:
		"""Prepare state for the requested mode, or None if data missing."""

		session = self._sessions[mode]
		if session.total == 0:
			return None
		if session.index >= session.total:
			session.index = max(0, session.total - 1)
		self._active_mode = mode
		return self._build_state(session, mode)

	def current_state(self) -> TranslationState | None:
		"""Return the active mode state without mutating session order."""

		if self._active_mode is None:
			return None
		return self._build_state(self._require_session(), self._active_mode)

	def next(self) -> TranslationState | None:
		"""Advance to the next item, returning None when run completes."""

		session = self._require_session()
		if session.is_last():
			return None
		session.move_next()
		return self._build_state(session, self._active_mode)

	def previous(self) -> TranslationState:
		"""Step backwards while staying within valid bounds."""

		session = self._require_session()
		session.move_previous()
		return self._build_state(session, self._active_mode)

	def hint(self) -> str:
		"""Return the answer for the active prompt."""

		session = self._require_session()
		return session.current_answer()

	def check_answer(self, user_input: str) -> tuple[bool, str]:
		"""Validate the provided answer and return the correctness flag."""

		session = self._require_session()
		correct = session.current_answer().strip()
		given = user_input.strip()

		if self._active_mode == "text_to_morse":
			# Same letters and the same word breaks; how a word gap is typed
			# (3 spaces, "/", newline) doesn't matter.
			normalized_given = normalize_morse(given)
			is_correct = bool(normalized_given) and normalized_given == normalize_morse(correct)
		else:
			is_correct = bool(given) and " ".join(given.upper().split()) == " ".join(
				correct.upper().split()
			)

		return is_correct, correct

	def audio_morse(self) -> str | None:
		"""The Morse to play for the active prompt (only when the prompt is Morse)."""

		if self._active_mode != "morse_to_text":
			return None
		return self._require_session().current_prompt()

	def title_for_mode(self, mode: str) -> str:
		return self._TITLES[mode]

	def _build_state(self, session: TranslationSession, mode: str) -> TranslationState:
		total = session.total
		index = session.index
		if total > 1:
			progress_step = 100.0 / (total - 1)
			progress_value = index * progress_step
		else:
			progress_step = 100.0
			progress_value = 100.0 if index else 0.0

		prompt = session.current_prompt()
		audio_morse = prompt if mode == "morse_to_text" else None
		is_first = session.is_first()
		is_last = session.is_last()
		prompt_style = "large" if mode == "text_to_morse" else "medium"

		return TranslationState(
			mode=mode,
			title=self._TITLES[mode],
			prompt=prompt,
			index=index,
			total=total,
			progress_value=progress_value,
			progress_step=progress_step,
			is_first=is_first,
			is_last=is_last,
			audio_morse=audio_morse,
			progress_text=t("common.progress", percent=progress_value),
			has_previous=not is_first,
			next_label=t("common.lopeta_treening") if is_last else t("common.liigu_edasi"),
			prompt_style=prompt_style,
			audio_available=audio_morse is not None,
		)

	def _require_session(self) -> TranslationSession:
		if self._active_mode is None:
			raise SessionNotInitializedError("Translation mode not initialised")
		return self._sessions[self._active_mode]
