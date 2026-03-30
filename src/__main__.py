"""Entry point for Briefcase/BeeWare packaging.

Allows running as `python -m src` when the project root is on sys.path.
This entry point is designed for future BeeWare/Toga migration.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path for imports to work
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.main.python.main import main

if __name__ == "__main__":
    main()
