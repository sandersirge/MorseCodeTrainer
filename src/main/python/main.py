from __future__ import annotations

from .application import build_application


def main() -> None:
    application = build_application()
    application.run()