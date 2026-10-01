"""Resolve vendored brand assets independently of desktop icon themes."""
from pathlib import Path

ASSET_ROOT = Path(__file__).resolve().parent.parent / 'assets/icons'
BUNDLED = frozenset({'x', 'linkedin', 'youtube', 'spotify', 'vscode', 'github', 'files'})


class IconResolver:
    @staticmethod
    def resolve(icon):
        if icon.startswith('bundled:'):
            name = icon.removeprefix('bundled:')
            if name not in BUNDLED:
                raise ValueError(f'Unknown bundled icon: {name}')
            path = ASSET_ROOT / f'{name}.svg'
        else:
            path = Path(icon).expanduser()
            if not path.is_file() and '/' not in icon:
                return None  # Native icon theme name.
        if not path.is_file():
            raise FileNotFoundError(f'Icon file not found: {path}')
        return path
