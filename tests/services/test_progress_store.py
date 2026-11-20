"""Tests for the saved training progress."""

import json

from morsetrainer.services.audio_settings import AudioSettings
from morsetrainer.services.progress_store import ProgressStore, default_data_dir


class TestProgressStore:
	def test_record_and_reload(self, tmp_path):
		path = tmp_path / "progress.json"
		store = ProgressStore(path)
		store.record("k", True)
		store.record("K", False)
		store.record_many({"M": (3, 1)})
		store.set_koch_level(5)

		reloaded = ProgressStore(path)
		assert (reloaded.stats("K").correct, reloaded.stats("K").wrong) == (1, 1)
		assert reloaded.stats("m").attempts == 4
		assert reloaded.koch_level == 5

	def test_weakness(self, tmp_path):
		store = ProgressStore(tmp_path / "p.json")
		assert store.weakness("Q") == 0.5  # never practised
		for _ in range(10):
			store.record("E", True)
			store.record("Q", False)
		assert store.weakness("E") == 0.0
		assert store.weakness("Q") == 1.0
		assert store.weakest(["E", "Q", "X"], 1) == ["Q"]

	def test_one_lucky_answer_does_not_hide_a_character(self, tmp_path):
		store = ProgressStore(tmp_path / "p.json")
		store.record("H", True)
		assert 0 < store.weakness("H") < 0.5

	def test_audio_settings_round_trip(self, tmp_path):
		path = tmp_path / "p.json"
		ProgressStore(path).save_audio_settings(
			AudioSettings(wpm=25, effective_wpm=18, frequency_hz=700)
		)
		loaded = ProgressStore(path).audio_settings()
		assert loaded == AudioSettings(wpm=25, effective_wpm=18, frequency_hz=700)

	def test_corrupt_file_starts_fresh(self, tmp_path):
		path = tmp_path / "p.json"
		path.write_text("{not json", encoding="utf-8")
		store = ProgressStore(path)
		assert store.koch_level == 2
		store.record("A", True)  # and can write a valid file again
		assert json.loads(path.read_text(encoding="utf-8"))["characters"]["A"]["correct"] == 1

	def test_no_temp_file_left_behind(self, tmp_path):
		store = ProgressStore(tmp_path / "p.json")
		store.record("A", True)
		assert [p.name for p in tmp_path.iterdir()] == ["p.json"]

	def test_reset(self, tmp_path):
		store = ProgressStore(tmp_path / "p.json")
		store.record("A", False)
		store.set_koch_level(9)
		store.reset()
		assert store.stats("A").attempts == 0 and store.koch_level == 2

	def test_default_dir_is_per_user(self):
		assert default_data_dir().name == "MorseCodeTrainer"
