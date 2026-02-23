"""Shared fixtures for services tests."""
import pytest
import sys


@pytest.fixture
def mock_pygame(monkeypatch):
    """Mock pygame module for CI environments without audio."""
    mock_module = type(sys)("pygame")
    mock_module.mixer = type(sys)("mixer")
    mock_module.mixer.init = lambda: None
    mock_module.mixer.Sound = lambda x: type("Sound", (), {"play": lambda self: None, "stop": lambda self: None})()
    mock_module.error = Exception
    
    monkeypatch.setitem(sys.modules, "pygame", mock_module)
    return mock_module
