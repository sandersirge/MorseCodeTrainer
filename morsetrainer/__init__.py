"""Morse Code Trainer - Entry point for Briefcase packaging."""
from src.main.python.application import build_application


def main():
    """Launch the Morse Code Trainer application."""
    application = build_application()
    application.run()


if __name__ == "__main__":
    main()
