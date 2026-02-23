from __future__ import annotations

from typing import Optional

from ..application import Application, build_application

__all__ = ["MorseApp", "build_application"]


class MorseApp:
    """Thin wrapper retained for legacy entry points."""

    def __init__(self) -> None:
        self._app: Optional[Application] = None

    def bootstrap(self) -> Application:
        if self._app is None:
            self._app = build_application()
        return self._app

    def run(self) -> None:
        self.bootstrap().run()
