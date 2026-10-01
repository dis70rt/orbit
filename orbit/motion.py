"""Frame-clock-independent transitions for visibility and wedge highlighting."""
from dataclasses import dataclass


@dataclass
class Transition:
    value: float = 0.0
    target: float = 0.0
    start_value: float = 0.0
    started: float = 0.0
    duration: float = 0.12

    def sample(self, now):
        progress = min(1.0, max(0.0, (now - self.started) / self.duration))
        eased = 1 - (1 - progress) ** 3
        self.value = self.start_value + (self.target - self.start_value) * eased
        return self.value

    def retarget(self, target, now, duration):
        self.sample(now)
        self.start_value, self.target = self.value, target
        self.started, self.duration = now, duration

    @property
    def settled(self):
        return abs(self.value - self.target) < 0.001


class WheelMotion:
    def __init__(self, count, enabled=True):
        self.enabled = enabled
        self.visibility = Transition()
        self.wedges = [Transition() for _ in range(count)]

    def show(self, now):
        self.visibility.retarget(1, now, 0.14)
        self.select(None, now)

    def hide(self, now):
        self.visibility.retarget(0, now, 0.09)

    def select(self, selected, now):
        for index, wedge in enumerate(self.wedges):
            target = float(index == selected)
            if wedge.target != target:
                wedge.retarget(target, now, 0.09)

    def advance(self, now):
        for transition in [self.visibility, *self.wedges]:
            if self.enabled:
                transition.sample(now)
            else:
                transition.value = transition.target
        return not all(t.settled for t in [self.visibility, *self.wedges])

    @property
    def scale(self):
        return 0.94 + 0.06 * self.visibility.value
