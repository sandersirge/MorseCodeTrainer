#!/usr/bin/env python
"""Entry point for running the Morse Code application."""
import sys
from pathlib import Path

# Add the src folder to path so imports work
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.main.python.main import main

if __name__ == "__main__":
    main()
