"""Coordinate gesture lifecycle through injected services."""
from orbit.geometry import monitor_at
from orbit.ports import Compositor, View, Launcher
from orbit.session import WheelSession


class WheelController:
    def __init__(self, session: WheelSession, compositor: Compositor, view: View, launcher: Launcher):
        self.session, self.compositor = session, compositor
        self.view, self.launcher = view, launcher

    def handle(self, command):
        if command == 'show':
            if self.session.active:
                return
            point = self.compositor.cursor()
            monitor = monitor_at(self.compositor.monitors(), point)
            self.session.begin(point)
            try:
                self.view.show(monitor, point)
            except Exception:
                self.cancel()
                raise
        elif command == 'release':
            if not self.session.active:
                return
            try:
                shortcut = self.session.release(self.compositor.cursor())
            finally:
                self.cancel()
            if shortcut:
                self.launcher.launch(shortcut)
        elif command == 'cancel':
            self.cancel()
        else:
            raise ValueError(f'Unknown command: {command}')

    def cancel(self):
        self.session.cancel()
        self.view.hide()
