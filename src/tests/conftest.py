"""Shared fixtures for pytest."""
import pytest
import sys
from pathlib import Path

# Ensure src.main.python package is importable (add project root)
project_root = Path(__file__).parent.parent.parent  # MorseCodeProgram/
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.main.python.model.flashcard_session import Flashcard, FlashcardSession
from src.main.python.model.translation_session import TranslationSession
from src.main.python.model.test_session import TestSession


@pytest.fixture
def sample_flashcards():
    """Create sample flashcard data."""
    return [
        Flashcard(front="A", back=".-"),
        Flashcard(front="B", back="-..."),
        Flashcard(front="C", back="-.-."),
    ]


@pytest.fixture
def flashcard_session(sample_flashcards):
    """Create a FlashcardSession with sample data."""
    return FlashcardSession(sample_flashcards)


@pytest.fixture
def empty_flashcard_session():
    """Create an empty FlashcardSession."""
    return FlashcardSession()


@pytest.fixture
def sample_prompts():
    """Sample prompts for translation/test sessions."""
    return ["HELLO", "WORLD", "TEST"]


@pytest.fixture
def sample_answers():
    """Sample answers corresponding to prompts."""
    return [".... . .-.. .-.. ---", ".-- --- .-. .-.. -..", "- . ... -"]


@pytest.fixture
def translation_session(sample_prompts, sample_answers):
    """Create a TranslationSession with sample data."""
    return TranslationSession(prompts=sample_prompts, answers=sample_answers)


@pytest.fixture
def test_session(sample_prompts, sample_answers):
    """Create a TestSession with sample data (no shuffle)."""
    return TestSession(prompts=sample_prompts, answers=sample_answers)


@pytest.fixture
def test_session_no_shuffle(sample_prompts, sample_answers, monkeypatch):
    """Create a TestSession with shuffle disabled."""
    monkeypatch.setattr("random.shuffle", lambda x: None)
    session = TestSession(prompts=sample_prompts, answers=sample_answers)
    return session
