#!/usr/bin/env python
"""Start the Morse Code Trainer from a source checkout.

- `python run.py` / the Run button in an IDE
- PyInstaller (`morsetrainer.spec`) builds from this file

When the package is installed (`pip install -e .`), `morse-trainer` or
`python -m morsetrainer` do the same thing.
"""

import sys
from pathlib import Path


def main() -> None:
	"""Put ``src/`` on sys.path, then start the app."""
	src = Path(__file__).resolve().parent / "src"
	if src.is_dir() and str(src) not in sys.path:
		sys.path.insert(0, str(src))
	from morsetrainer.main import main as run_app

	run_app()


if __name__ == "__main__":
	main()
