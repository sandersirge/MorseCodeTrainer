"""Navigation abstraction for screen routing.

Views receive a single Navigator instance instead of individual callback
arguments, making navigation intent explicit and adding a screen trivial.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Navigator:
	"""Named navigation callbacks shared across all views."""

	home: Callable[[], None]
	introduction: Callable[[], None]
	flashcards: Callable[[], None]
	translation: Callable[[], None]
	translation_sandbox: Callable[[], None]
	test: Callable[[], None]
	exit: Callable[[], None]
	reset_translation: Callable[[], None]
