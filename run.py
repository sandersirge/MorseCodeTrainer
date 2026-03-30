#!/usr/bin/env python
"""Unified entry point for the Morse Code Trainer application.

This file serves as the single entry point that works across:
- CLI execution: `python run.py`
- Editor execution: F5/Run button in VS Code
- PyInstaller builds: used by morsetrainer.spec

The canonical implementation lives in src.main.python.main.
"""
import sys
from pathlib import Path


def _setup_path() -> None:
    """Ensure project root is on sys.path for imports to work."""
    project_root = Path(__file__).resolve().parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def main() -> None:
    """Launch the Morse Code Trainer application."""
    _setup_path()
    from src.main.python.main import main as _main
    _main()


if __name__ == "__main__":
    main()
