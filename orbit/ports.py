"""Structural interfaces for the controller's external dependencies."""
from typing import Protocol
from orbit.settings import Shortcut


class Compositor(Protocol):
    def cursor(self) -> tuple[float, float]: ...
    def monitors(self) -> list[dict]: ...


class View(Protocol):
    def show(self, monitor: dict, point: tuple[float, float]) -> None: ...
    def hide(self) -> None: ...


class Launcher(Protocol):
    def launch(self, shortcut: Shortcut) -> None: ...
