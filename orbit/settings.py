"""Load and validate the user-owned shortcut configuration."""
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path


@dataclass(frozen=True)
class Shortcut:
    label: str
    icon: str
    kind: str
    value: str | tuple[str, ...]


@dataclass(frozen=True)
class Settings:
    radius: float
    dead_zone: float
    accent: tuple[float, float, float]
    shortcuts: tuple[Shortcut, ...]

    animations: bool = True
    show_label: bool = True

    @classmethod
    def load(cls, path=None):
        user = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'orbit/config.json'
        default = Path(__file__).resolve().parent.parent / 'config/default.json'
        return cls.from_dict(json.loads(Path(path or (user if user.exists() else default)).read_text()))

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError('Configuration must be a JSON object')
        animations = data.get('animations', True)
        show_label = data.get('show_label', True)
        if not isinstance(animations, bool) or not isinstance(show_label, bool):
            raise ValueError('animations and show_label must be booleans')
        radius, dead = data.get('radius', 170), data.get('dead_zone', 56)
        def number(value):
            return type(value) in (int, float) and math.isfinite(value)
        if not number(radius) or not number(dead) or not 30 <= dead < radius <= 400:
            raise ValueError('Require 30 <= dead_zone < radius <= 400')
        accent = data.get('accent', [0.94, 0.94, 0.94])
        if not isinstance(accent, list) or len(accent) != 3 or not all(number(v) and 0 <= v <= 1 for v in accent):
            raise ValueError('accent must contain three RGB values between 0 and 1')
        items = data.get('shortcuts', [])
        if not isinstance(items, list) or not 2 <= len(items) <= 12:
            raise ValueError('Configure between 2 and 12 shortcuts')
        shortcuts = []
        for item in items:
            if not isinstance(item, dict):
                raise ValueError('Each shortcut must be an object')
            label, icon, kind, value = (item.get(k) for k in ('label', 'icon', 'type', 'value'))
            if not isinstance(label, str) or not label.strip() or len(label) > 48:
                raise ValueError('Shortcut label must be 1–48 characters')
            if not isinstance(icon, str) or not icon:
                raise ValueError('Shortcut icon must be a theme name or file path')
            if kind == 'command':
                if not isinstance(value, list) or not value or not all(isinstance(v, str) and v and '\0' not in v for v in value):
                    raise ValueError('Commands require a nonempty argv array')
                value = tuple(value)
            elif kind in ('application', 'folder', 'website'):
                if not isinstance(value, str) or not value or '\0' in value:
                    raise ValueError('Shortcut value must be a nonempty string')
                if kind == 'website' and not value.startswith(('https://', 'http://')):
                    raise ValueError('Websites require an http(s) URL')
                if kind == 'application' and not value.endswith('.desktop'):
                    raise ValueError('Applications require a .desktop ID')
            else:
                raise ValueError(f'Unknown shortcut type: {kind}')
            shortcuts.append(Shortcut(label, icon, kind, value))
        return cls(radius, dead, tuple(accent), tuple(shortcuts), animations, show_label)
