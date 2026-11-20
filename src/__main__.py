"""Fallback entry point for IDE execution.

Allows running as `python -m src` when the project root is on sys.path.
The primary entry point is `run.py` (used by PyInstaller).
"""

import sys
from pathlib import Path


def main() -> None:
	"""Put the project root on sys.path, then start the app."""
	project_root = Path(__file__).resolve().parent.parent
	if str(project_root) not in sys.path:
		sys.path.insert(0, str(project_root))
	from src.main.python.main import main as run_app

	run_app()


if __name__ == "__main__":
	main()
