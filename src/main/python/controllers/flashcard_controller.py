from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

from ..model.flashcard_session import FlashcardSession


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
    audio_path: Optional[str]
    progress_text: str
    has_previous: bool
    next_label: str
    show_audio_button: bool


class FlashcardPresenter:
    """Coordinates flashcard session state for the UI."""

    def __init__(
        self,
        sessions: Mapping[str, FlashcardSession],
        audio_map: Mapping[str, str],
    ) -> None:
        self._sessions = {name: session for name, session in sessions.items()}
        self._audio_map = dict(audio_map)
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
        session.reset()
        self._active_category = category
        self._showing_back = False
        return self._build_state(session)

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
        audio_path = self._audio_map.get(card.front)
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
            audio_path=audio_path,
            progress_text=f"{progress_value:.1f}% läbitud",
            has_previous=not is_first,
            next_label="Lõpeta treening" if is_last else "Liigu edasi",
            show_audio_button=self._showing_back and audio_path is not None,
        )

    def _require_session(self) -> FlashcardSession:
        if self._active_category is None:
            raise RuntimeError("Flashcard category not initialised")
        return self._sessions[self._active_category]