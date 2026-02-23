"""Tests for TranslationSandboxPresenter controller."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.main.python.controllers.translation_sandbox_controller import TranslationSandboxPresenter, SandboxState


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
        with pytest.raises(ValueError, match="Unsupported mode"):
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
        assert "Unsupported" in state.error_message

    def test_translate_stores_input(self, presenter):
        presenter.translate("HELLO")
        assert presenter._input_text == "HELLO"


class TestTranslationSandboxPresenterGenerateAudio:
    """Tests for generate_audio method."""

    def test_generate_audio_without_content_raises(self, presenter):
        with pytest.raises(ValueError, match="Morse content"):
            presenter.generate_audio()

    @patch("src.main.python.controllers.translation_sandbox_controller.synthesize_morse_audio")
    def test_generate_audio_with_content(self, mock_synth, presenter):
        mock_synth.return_value = Path("/tmp/audio.wav")
        presenter.translate("A")  # Creates morse content
        state = presenter.generate_audio()
        assert state.audio_ready or presenter._audio_path is not None

    @patch("src.main.python.controllers.translation_sandbox_controller.synthesize_morse_audio")
    def test_generate_audio_updates_settings(self, mock_synth, presenter):
        mock_synth.return_value = Path("/tmp/audio.wav")
        presenter.translate("A")
        presenter.generate_audio(frequency=600.0, unit_duration_ms=80, volume=0.8)
        assert presenter._audio_settings.frequency_hz == 600.0
        assert presenter._audio_settings.unit_duration_ms == 80
        assert presenter._audio_settings.volume == 0.8


class TestTranslationSandboxPresenterClearAudio:
    """Tests for clear_audio method."""

    def test_clear_audio_resets_path(self, presenter):
        presenter._audio_path = Path("/tmp/audio.wav")
        state = presenter.clear_audio()
        assert presenter._audio_path is None
        assert not state.audio_ready


class TestTranslationSandboxPresenterSaveAudio:
    """Tests for save_audio methods."""

    def test_save_audio_without_file_raises(self, presenter):
        with pytest.raises(ValueError):
            presenter.save_audio_to_output()

    def test_save_audio_as_without_file_raises(self, presenter):
        with pytest.raises(ValueError):
            presenter.save_audio_as(Path("/tmp/output.wav"))

    @patch("shutil.copy2")
    @patch.object(Path, "exists", return_value=True)
    @patch.object(Path, "mkdir")
    def test_save_audio_as_appends_wav_extension(self, mock_mkdir, mock_exists, mock_copy, presenter):
        presenter._audio_path = Path("/tmp/audio.wav")
        state, path = presenter.save_audio_as(Path("/tmp/output"))
        assert path.suffix == ".wav"


class TestTranslationSandboxPresenterUpdateSettings:
    """Tests for update_* methods."""

    def test_update_volume(self, presenter):
        state = presenter.update_volume(0.75)
        assert state.volume == 0.75

    def test_update_volume_clamps(self, presenter):
        state = presenter.update_volume(1.5)  # Over max
        assert state.volume == 1.0

    def test_update_speed(self, presenter):
        state = presenter.update_speed(100)
        assert state.speed_ms == 100

    def test_update_pitch(self, presenter):
        state = presenter.update_pitch(500.0)
        assert state.pitch_hz == 500.0


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
            audio_path=None,
            volume=0.5,
            speed_ms=60,
            pitch_hz=400.0,
        )
        with pytest.raises(AttributeError):
            state.mode = "morse_to_text"
