from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox

from ..controllers.protocols import SandboxPresenterProtocol
from ..controllers.translation_sandbox_controller import SandboxState
from ..exceptions import MorseTrainerError
from ..navigator import Navigator
from ..strings import t
from .audio_section import AudioSection
from .translation_section import TranslationSection
from .widgets import make_page


class TranslationSandboxView:
	"""Interactive sandbox for ad-hoc Morse translations and audio."""

	def __init__(
		self,
		*,
		root,
		nav: Navigator,
		audio_player,
		presenter: SandboxPresenterProtocol,
	) -> None:
		self.root = root
		self.nav = nav
		self.audio = audio_player
		self.presenter = presenter

		self.translation_section: TranslationSection | None = None
		self.audio_section: AudioSection | None = None

	def _clear_content(self) -> None:
		"""Destroy this view's children without touching other views."""
		for w in self.root.winfo_children():
			w.destroy()

	def show(self) -> None:
		if self.audio_section is not None:
			self.audio_section.stop_playback()
		self._clear_content()

		state = self.presenter.current_state()
		self._build_layout()
		if state is not None:
			self._render_state(state)

	# Layout -----------------------------------------------------------------

	def _build_layout(self) -> None:
		page = make_page(
			self.root,
			title=t("sandbox.sandbox_tolkimine"),
			subtitle=t("sandbox.katseta_erinevaid_tolkesuundi_muuda"),
			back=(t("common.tagasi_avalehele"), self._go_home),
			relwidth=0.92,
			relheight=0.92,
		)
		page.footer.grid_remove()
		page.body.grid_configure(padx=32, pady=(8, 28))
		page.body.grid_columnconfigure((0, 1), weight=1, uniform="half")
		page.body.grid_rowconfigure(0, weight=1)

		self.translation_section = TranslationSection(
			page.body,
			on_select_mode=self._on_select_mode,
			on_translate=self._on_translate,
			on_clear=self._on_clear,
		)
		self.translation_section.container.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

		self.audio_section = AudioSection(
			page.body,
			root=self.root,
			audio_player=self.audio,
			on_play=self._on_play_audio,
			on_save=self._on_save_audio,
			on_save_as=self._on_save_audio_as,
			on_volume_change=self._handle_volume_change,
			on_wpm_change=self._handle_wpm_change,
			on_effective_wpm_change=self._handle_effective_wpm_change,
			on_pitch_change=self._handle_pitch_change,
			on_home=self._go_home,
			on_audio_error=self._show_error,
		)
		self.audio_section.container.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

	def _go_home(self) -> None:
		if self.audio_section is not None:
			self.audio_section.stop_playback()
		self.nav.home()

	# Rendering ---------------------------------------------------------------

	def _render_state(self, state: SandboxState) -> None:
		if self.translation_section is not None:
			self.translation_section.render(state)
		if self.audio_section is not None:
			self.audio_section.render(state)

	# Event handlers ---------------------------------------------------------

	def _on_select_mode(self, mode_key: str) -> None:
		if self.audio_section is not None:
			self.audio_section.stop_playback()
		state = self.presenter.set_mode(mode_key)
		self._render_state(state)

	def _on_translate(self) -> None:
		if self.translation_section is None:
			return
		if self.audio_section is not None:
			self.audio_section.stop_playback()
		text = self.translation_section.read_input_text()
		state = self.presenter.translate(text)
		self._render_state(state)

	def _on_clear(self) -> None:
		if self.translation_section is None:
			return
		if self.audio_section is not None:
			self.audio_section.stop_playback()
		self.translation_section.clear_input()
		state = self.presenter.translate("")
		self._render_state(state)
		self.translation_section.focus_input()

	def _on_play_audio(self) -> None:
		if self.audio_section is None:
			return
		state = self.presenter.current_state()
		if state is None or state.audio_morse is None:
			return
		self.audio_section.play_audio(state.audio_morse)

	def _on_save_audio(self) -> None:
		if self.audio_section is not None:
			self.audio_section.stop_playback()
		try:
			_, saved_path = self.presenter.save_audio_to_output()
		except MorseTrainerError as exc:
			self._show_error(exc.user_message)
			return
		messagebox.showinfo(
			t("sandbox.helifail_salvestatud"),
			t("sandbox.file_saved", path=saved_path),
			parent=self.root,
		)

	def _on_save_audio_as(self) -> None:
		if self.audio_section is not None:
			self.audio_section.stop_playback()
		state = self.presenter.current_state()
		if state is None or not state.audio_ready:
			return
		suggested = self.presenter.suggested_save_path()
		initial_dir = suggested.parent if suggested.parent.is_dir() else Path.home()
		selection = filedialog.asksaveasfilename(
			parent=self.root,
			title=t("sandbox.salvesta_helifail"),
			defaultextension=".wav",
			# Only one filter: "*.*" filters misbehave in the macOS save dialog.
			filetypes=[(t("sandbox.wav_helifail"), "*.wav")],
			initialdir=str(initial_dir),
			initialfile=suggested.name,
		)
		if not selection:
			return
		try:
			_, saved_path = self.presenter.save_audio_as(Path(selection))
		except MorseTrainerError as exc:
			self._show_error(exc.user_message)
			return
		messagebox.showinfo(
			t("sandbox.helifail_salvestatud"),
			t("sandbox.file_saved", path=saved_path),
			parent=self.root,
		)

	def _handle_volume_change(self, volume: float) -> None:
		if self.audio_section is not None:
			self.audio_section.stop_playback()
		state = self.presenter.update_volume(volume)
		self._render_state(state)

	def _handle_wpm_change(self, wpm: int) -> None:
		if self.audio_section is not None:
			self.audio_section.stop_playback()
		state = self.presenter.update_wpm(wpm)
		self._render_state(state)

	def _handle_effective_wpm_change(self, effective_wpm: int) -> None:
		if self.audio_section is not None:
			self.audio_section.stop_playback()
		state = self.presenter.update_effective_wpm(effective_wpm)
		self._render_state(state)

	def _handle_pitch_change(self, frequency_hz: float) -> None:
		if self.audio_section is not None:
			self.audio_section.stop_playback()
		state = self.presenter.update_pitch(frequency_hz)
		self._render_state(state)

	def _show_error(self, message: str) -> None:
		if self.translation_section is not None:
			self.translation_section.set_error(message)


__all__ = ["TranslationSandboxView"]
