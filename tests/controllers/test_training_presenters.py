"""Koch, keyer, flashcard rating and random translation drills."""

import random

import pytest

from morsetrainer.controllers.flashcard_controller import FlashcardPresenter, card_character
from morsetrainer.controllers.keyer_controller import KeyerPresenter
from morsetrainer.controllers.koch_controller import KochPresenter
from morsetrainer.controllers.translation_controller import TranslationPresenter
from morsetrainer.exceptions import InvalidModeError
from morsetrainer.model.flashcard_session import Flashcard, FlashcardSession
from morsetrainer.model.translation_session import TranslationSession
from morsetrainer.services.audio_settings import AudioSettings, AudioSettingsStore
from morsetrainer.services.progress_store import ProgressStore


@pytest.fixture
def progress(tmp_path):
	return ProgressStore(tmp_path / "progress.json")


class TestKochPresenter:
	def test_starts_with_two_characters(self, progress):
		state = KochPresenter(progress).current_state()
		assert state.characters == ["K", "M"] and state.new_char == "M"
		assert not state.has_exercise

	def test_perfect_copy_unlocks_next_character(self, progress):
		presenter = KochPresenter(progress, random.Random(1))
		presenter.new_exercise()
		state = presenter.check(presenter.exercise_text.lower())
		assert state.leveled_up and state.passed
		assert progress.koch_level == 3
		assert state.new_char == "U"

	def test_poor_copy_stays_on_level_and_records_mistakes(self, progress):
		presenter = KochPresenter(progress, random.Random(2))
		presenter.new_exercise()
		state = presenter.check("")
		assert not state.passed and not state.leveled_up
		assert progress.koch_level == 2
		assert progress.stats("K").wrong + progress.stats("M").wrong > 0

	def test_exercise_morse_and_new_char_sound(self, progress):
		presenter = KochPresenter(progress, random.Random(3))
		assert presenter.exercise_morse() == ""
		presenter.new_exercise()
		assert set(presenter.exercise_morse()) <= {".", "-", " "}
		assert presenter.new_char_morse() == "--   --   --"

	def test_manual_level_change_is_clamped(self, progress):
		presenter = KochPresenter(progress)
		assert presenter.change_level(-5).level == 2
		assert presenter.change_level(+3).level == 5


class TestKeyerPresenter:
	def _presenter(self, progress):
		store = AudioSettingsStore(AudioSettings(wpm=20, effective_wpm=20))
		return KeyerPresenter(store, ["sos"], progress, random.Random(0))

	def test_target_is_uppercase_word(self, progress):
		state = self._presenter(progress).current_state()
		assert state.target == "SOS" and state.target_morse == "... --- ..."

	def test_correct_keying_is_accepted(self, progress):
		presenter = self._presenter(progress)
		unit, now = 0.06, 0.0
		for letter in ["...", "---", "..."]:
			for symbol in letter:
				presenter.key_down(now)
				now += unit if symbol == "." else 3 * unit
				presenter.key_up(now)
				now += unit
			now += 2 * unit
		presenter.tick(now + 1)
		state = presenter.check()
		assert state.checked and state.correct
		assert progress.stats("S").correct == 2

	def test_wrong_keying_is_rejected(self, progress):
		presenter = self._presenter(progress)
		presenter.key_down(0.0)
		presenter.key_up(0.06)
		presenter.tick(1.0)
		assert not presenter.check().correct

	def test_clear_and_new_target_reset_checked(self, progress):
		presenter = self._presenter(progress)
		presenter.check()
		assert not presenter.clear().checked
		assert not presenter.new_target().checked


class TestFlashcardRating:
	def _presenter(self, progress):
		cards = [Flashcard("A a", ".-"), Flashcard("B b", "-..."), Flashcard("C c", "-.-.")]
		return FlashcardPresenter({"tähed": FlashcardSession(cards)}, progress, random.Random(0))

	def test_card_character(self):
		assert card_character(Flashcard("Ä ä", ".-.-")) == "Ä"
		assert card_character(Flashcard("5", ".....")) == "5"

	def test_rating_only_on_back_side(self, progress):
		presenter = self._presenter(progress)
		assert not presenter.start("tähed").can_rate
		assert presenter.toggle().can_rate

	def test_rate_records_and_advances(self, progress):
		presenter = self._presenter(progress)
		first = presenter.start("tähed")
		presenter.toggle()
		after = presenter.rate(False)
		char = first.front_text.split()[0]
		assert progress.stats(char).wrong == 1
		assert after is not None and after.front_text != first.front_text

	def test_weak_cards_tend_to_come_first(self, progress):
		for _ in range(10):
			progress.record("C", False)
			progress.record("A", True)
			progress.record("B", True)
		firsts = []
		for seed in range(60):
			presenter = FlashcardPresenter(
				{
					"tähed": FlashcardSession(
						[Flashcard("A a", ".-"), Flashcard("B b", "-..."), Flashcard("C c", "-.-.")]
					)
				},
				progress,
				random.Random(seed),
			)
			firsts.append(presenter.start("tähed").front_text)
		assert firsts.count("C c") > 40


class TestTranslationRandomSource:
	def _presenter(self, progress):
		fixed = TranslationSession(prompts=["-- --- .-. ... ."], answers=["MORSE"])
		fixed_text = TranslationSession(prompts=["MORSE"], answers=["-- --- .-. ... ."])
		return TranslationPresenter(
			fixed, fixed_text, drill_factory=lambda: ["tere", "maja kodu"], progress=progress
		)

	def test_default_source_is_fixed(self, progress):
		presenter = self._presenter(progress)
		assert presenter.source == "fixed"
		assert presenter.start("text_to_morse").prompt == "MORSE"

	def test_random_source_builds_new_drill(self, progress):
		presenter = self._presenter(progress)
		presenter.set_source("random")
		state = presenter.start("text_to_morse")
		assert state.prompt == "tere" and state.total == 2
		assert presenter.check_answer("- . .-. .")[0] is True

	def test_reset_returns_to_fixed_items(self, progress):
		presenter = self._presenter(progress)
		presenter.set_source("random")
		presenter.start("morse_to_text")
		presenter.reset()
		presenter.set_source("fixed")
		assert presenter.start("morse_to_text").prompt == "-- --- .-. ... ."

	def test_first_attempt_is_scored_per_character(self, progress):
		presenter = self._presenter(progress)
		presenter.start("morse_to_text")
		presenter.check_answer("MORZE")
		presenter.check_answer("MORSE")  # second try is not counted again
		assert progress.stats("S").wrong == 1 and progress.stats("S").correct == 0
		assert progress.stats("M").correct == 1

	def test_unknown_source_raises(self, progress):
		with pytest.raises(InvalidModeError):
			self._presenter(progress).set_source("other")
