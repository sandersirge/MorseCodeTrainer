"""Allow running as `python -m morsetrainer`.

This is a thin wrapper that delegates to the canonical entry point
at src.main.python.main.
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
