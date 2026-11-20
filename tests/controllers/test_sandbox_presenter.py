"""Tests for TranslationSandboxPresenter controller."""

from pathlib import Path

import pytest

from morsetrainer.controllers.translation_sandbox_controller import (
	SandboxState,
	TranslationSandboxPresenter,
	default_output_dir,
)
from morsetrainer.exceptions import InvalidModeError, NoAudioContentError
from morsetrainer.services.audio_settings import AudioSettingsStore
from morsetrainer.strings import t


@pytest.fixture
def presenter():
	"""Create a fresh TranslationSandboxPresenter."""
	return TranslationSandboxPresenter()


class TestTranslationSandboxPresenterInit:
	"""Tests for TranslationSandboxPresenter initialization."""

	def test_init_default_mode(self, presenter):
		assert presenter._mode == "text_to_morse"

	def test_init_empty_input_output(self, presenter):
		assert presenter._input_text == ""
		assert presenter._output_text == ""

	def test_init_no_error(self, presenter):
		assert presenter._error_message is None


class TestTranslationSandboxPresenterCurrentState:
	"""Tests for current_state method."""

	def test_returns_sandbox_state(self, presenter):
		state = presenter.current_state()
		assert isinstance(state, SandboxState)

	def test_state_reflects_mode(self, presenter):
		state = presenter.current_state()
		assert state.mode == "text_to_morse"
		assert state.mode_label == "Tekst → Morse"


class TestTranslationSandboxPresenterToggleMode:
	"""Tests for toggle_mode method."""

	def test_toggle_changes_mode(self, presenter):
		presenter.toggle_mode()
		assert presenter._mode == "morse_to_text"

	def test_toggle_back_to_original(self, presenter):
		presenter.toggle_mode()
		presenter.toggle_mode()
		assert presenter._mode == "text_to_morse"

	def test_toggle_clears_input_output(self, presenter):
		presenter._input_text = "test"
		presenter._output_text = "result"
		presenter.toggle_mode()
		assert presenter._input_text == ""
		assert presenter._output_text == ""

	def test_toggle_clears_error(self, presenter):
		presenter._error_message = "error"
		presenter.toggle_mode()
		assert presenter._error_message is None


class TestTranslationSandboxPresenterSetMode:
	"""Tests for set_mode method."""

	def test_set_mode_text_to_morse(self, presenter):
		presenter.set_mode("text_to_morse")
		state = presenter.current_state()
		assert state.mode == "text_to_morse"

	def test_set_mode_morse_to_text(self, presenter):
		presenter.set_mode("morse_to_text")
		state = presenter.current_state()
		assert state.mode == "morse_to_text"

	def test_set_mode_invalid_raises(self, presenter):
		with pytest.raises(InvalidModeError):
			presenter.set_mode("invalid_mode")

	def test_set_mode_same_mode_no_change(self, presenter):
		presenter._input_text = "keep this"
		presenter.set_mode("text_to_morse")  # same as default
		assert presenter._input_text == "keep this"

	def test_set_mode_different_clears_input(self, presenter):
		presenter._input_text = "clear this"
		presenter.set_mode("morse_to_text")
		assert presenter._input_text == ""


class TestTranslationSandboxPresenterTranslate:
	"""Tests for translate method."""

	def test_translate_text_to_morse(self, presenter):
		state = presenter.translate("A")
		assert state.output_text == ".-"

	def test_translate_morse_to_text(self, presenter):
		presenter.set_mode("morse_to_text")
		state = presenter.translate(".-")
		assert state.output_text == "A"

	def test_translate_empty_clears_output(self, presenter):
		presenter.translate("A")  # populate output
		state = presenter.translate("")
		assert state.output_text == ""

	def test_translate_whitespace_only_clears_output(self, presenter):
		presenter.translate("A")
		state = presenter.translate("   ")
		assert state.output_text == ""

	def test_translate_invalid_character_sets_error(self, presenter):
		state = presenter.translate("©")
		assert state.error_message is not None
		assert state.error_message == t("error.unsupported_character", char="©")

	def test_translate_stores_input(self, presenter):
		presenter.translate("HELLO")
		assert presenter._input_text == "HELLO"


class TestTranslationSandboxPresenterAudio:
	"""Audio is ready whenever there is valid Morse to play or save."""

	def test_no_audio_without_content(self, presenter):
		state = presenter.current_state()
		assert not state.audio_ready
		assert state.audio_morse is None

	def test_text_translation_makes_audio_ready(self, presenter):
		state = presenter.translate("SOS")
		assert state.audio_ready
		assert state.audio_morse == "... --- ..."

	def test_morse_input_is_normalized_for_audio(self, presenter):
		presenter.set_mode("morse_to_text")
		state = presenter.translate(" ...  /  ---  ")
		assert state.audio_morse == "...   ---"

	def test_error_clears_audio(self, presenter):
		presenter.translate("SOS")
		state = presenter.translate("#")
		assert not state.audio_ready


class TestTranslationSandboxPresenterClearAudio:
	"""Tests for clear_audio method."""

	def test_clear_audio_resets_audio(self, presenter):
		presenter.translate("A")
		state = presenter.clear_audio()
		assert not state.audio_ready


class TestTranslationSandboxPresenterSaveAudio:
	"""Tests for save_audio methods (written straight to WAV, no temp files)."""

	def test_save_audio_without_content_raises(self, tmp_path):
		presenter = TranslationSandboxPresenter(output_dir=tmp_path)
		with pytest.raises(NoAudioContentError):
			presenter.save_audio_to_output()

	def test_save_audio_as_without_content_raises(self, presenter, tmp_path):
		with pytest.raises(NoAudioContentError):
			presenter.save_audio_as(tmp_path / "output.wav")

	def test_save_audio_as_appends_wav_extension(self, presenter, tmp_path):
		presenter.translate("A")
		state, path = presenter.save_audio_as(tmp_path / "output")
		assert path.suffix == ".wav"
		assert path.is_file()
		assert state.audio_ready  # still playable after saving

	def test_save_to_output_numbers_files(self, tmp_path):
		presenter = TranslationSandboxPresenter(output_dir=tmp_path)
		presenter.translate("A")
		_, first = presenter.save_audio_to_output()
		_, second = presenter.save_audio_to_output()
		assert first.name == "tõlge1.wav"
		assert second.name == "tõlge2.wav"
		assert first.is_file() and second.is_file()

	def test_default_output_dir_is_in_user_home(self):
		assert Path.home() in default_output_dir().parents


class TestTranslationSandboxPresenterUpdateSettings:
	"""Tests for update_* methods (they change the shared settings store)."""

	def test_update_volume(self, presenter):
		state = presenter.update_volume(0.75)
		assert state.volume == 0.75

	def test_update_volume_clamps(self, presenter):
		state = presenter.update_volume(1.5)  # Over max
		assert state.volume == 1.0

	def test_update_wpm(self, presenter):
		state = presenter.update_wpm(25)
		assert state.wpm == 25

	def test_update_effective_wpm(self, presenter):
		presenter.update_wpm(25)
		state = presenter.update_effective_wpm(12)
		assert state.effective_wpm == 12

	def test_update_pitch(self, presenter):
		state = presenter.update_pitch(500.0)
		assert state.pitch_hz == 500.0

	def test_settings_are_shared_through_store(self):
		store = AudioSettingsStore()
		presenter = TranslationSandboxPresenter(store)
		presenter.update_pitch(700.0)
		assert store.settings.frequency_hz == 700.0


class TestSandboxState:
	"""Tests for SandboxState dataclass."""

	def test_state_is_frozen(self):
		state = SandboxState(
			mode="text_to_morse",
			mode_label="Tekst → Morse",
			input_label="Tekst",
			output_label="Morse",
			input_text="",
			output_text="",
			error_message=None,
			audio_ready=False,
			audio_morse=None,
			volume=0.5,
			wpm=20,
			effective_wpm=15,
			pitch_hz=600.0,
		)
		with pytest.raises(AttributeError):
			state.mode = "morse_to_text"
