from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from ..controllers.protocols import TestPresenterProtocol
from ..strings import t
from .theme import get_colors
from .widgets import (
	font_body,
	font_callout,
	make_button,
	make_frame,
	make_label,
	make_page,
	spread_rows,
)


class TestMenuScreen:
	"""Start screen of the timed test, with a confirmation step."""

	def __init__(
		self,
		root: ctk.CTk,
		clear_screen: Callable[[], None],
		presenter: TestPresenterProtocol,
		on_home: Callable[[], None],
		on_start: Callable[[], None],
	) -> None:
		self.root = root
		self.clear_screen = clear_screen
		self.presenter = presenter
		self.on_home = on_home
		self.on_start = on_start

	def show(self) -> None:
		if self.presenter.total_questions() == 0:
			self._show_empty_state()
			return
		self.clear_screen()
		page = make_page(
			self.root,
			title=t("test.testi_ennast"),
			back=(t("common.tagasi_avalehele"), self.on_home),
			relwidth=0.66,
			relheight=0.8,
		)
		self._message_with_actions(
			page,
			t("test.oled_joudnud_testreziimi_juurde"),
			[(t("test.alusta"), self._show_confirmation, "primary")],
		)

	def _show_empty_state(self) -> None:
		self.clear_screen()
		page = make_page(
			self.root,
			title=t("test.testi_andmed_puuduvad"),
			relwidth=0.56,
			relheight=0.5,
		)
		self._message_with_actions(
			page,
			t("test.testreziimi_jaoks_pole_hetkel"),
			[(t("common.tagasi"), self.on_home, "primary")],
			error=True,
		)

	def _show_confirmation(self) -> None:
		self.clear_screen()
		page = make_page(
			self.root,
			title=t("test.kas_oled_valmis"),
			back=(t("common.tagasi"), self.show),
			relwidth=0.62,
			relheight=0.66,
		)
		self._message_with_actions(
			page,
			t("test.testi_alustades_kaivitub_taimer"),
			[
				(t("test.ei_soovi_kordamist"), self.show, "secondary"),
				(t("test.jah_alusta_testi"), self.on_start, "primary"),
			],
		)

	def _message_with_actions(
		self,
		page,
		message: str,
		actions: list[tuple[str, Callable[[], None], str]],
		*,
		error: bool = False,
	) -> None:
		"""Message tile centred in the body, actions in a row under it."""
		colors = get_colors()
		spread_rows(page.body, 2)
		tile = make_frame(page.body, fg_color=colors.section_bg, corner_radius=20)
		tile.grid(row=1, column=0, sticky="ew", pady=(0, 36))
		make_label(
			tile,
			message,
			font=font_callout() if not error else font_body(),
			text_color=colors.error_text if error else colors.text_primary,
			wraplength=620,
		).pack(padx=32, pady=32)
		row = make_frame(page.body)
		row.grid(row=2, column=0)
		for column, (label, callback, variant) in enumerate(actions):
			make_button(row, label, command=callback, variant=variant, size="lg", width=220).grid(
				row=0, column=column, padx=12
			)


__all__ = ["TestMenuScreen"]
