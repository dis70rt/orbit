"""Gesture state independent of GTK and process launching."""
from orbit.geometry import segment_at


class WheelSession:
    def __init__(self, settings):
        self.settings = settings
        self.origin = None
        self.selected = None

    @property
    def active(self):
        return self.origin is not None

    def begin(self, point):
        if not self.active:
            self.origin = point
            self.selected = None

    def move(self, point):
        if self.active:
            self.selected = segment_at(point[0] - self.origin[0], point[1] - self.origin[1],
                                       len(self.settings.shortcuts), self.settings.dead_zone)

    def cancel(self):
        self.origin = None
        self.selected = None

    def release(self, point):
        if not self.active:
            return None
        self.move(point)
        shortcut = None if self.selected is None else self.settings.shortcuts[self.selected]
        self.cancel()
        return shortcut
