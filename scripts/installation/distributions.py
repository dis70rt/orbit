"""Resolve native dependency packages without executing os-release contents."""
from dataclasses import dataclass
from pathlib import Path
import shlex


@dataclass(frozen=True)
class Distribution:
    family: str
    manager: str
    packages: tuple[str, ...]

    def install_command(self, yes=False, hyprland_missing=False):
        packages = self.packages + (('hyprland',) if hyprland_missing else ())
        if self.manager == 'pacman':
            return ['pacman', '-S', '--needed', *(['--noconfirm'] if yes else []), *packages]
        if self.manager == 'dnf':
            return ['dnf', 'install', *(['-y'] if yes else []), *packages]
        return ['apt-get', 'install', *(['-y'] if yes else []), *packages]


FAMILIES = {
    'arch': Distribution('Arch', 'pacman', ('python', 'python-gobject', 'python-cairo',
                                         'gtk4', 'gtk4-layer-shell')),
    'fedora': Distribution('Fedora', 'dnf', ('python3', 'python3-gobject', 'python3-cairo',
                                          'gtk4', 'gtk4-layer-shell')),
    'debian': Distribution('Debian/Ubuntu', 'apt-get', ('python3', 'python3-gi',
                          'python3-gi-cairo', 'python3-cairo', 'gir1.2-gtk-4.0',
                          'gir1.2-gtk4layershell-1.0')),
}


def detect(path=Path('/etc/os-release')):
    values = {}
    for line in path.read_text().splitlines():
        key, separator, value = line.partition('=')
        if separator and key in ('ID', 'ID_LIKE'):
            tokens = shlex.split(value, comments=True)
            values[key] = tokens[0] if len(tokens) == 1 else ' '.join(tokens)
    for identity in [values.get('ID', ''), *values.get('ID_LIKE', '').split()]:
        if identity == 'ubuntu':
            identity = 'debian'
        if identity in FAMILIES:
            return FAMILIES[identity]
    raise ValueError('Unsupported distribution. Install dependencies manually and use --skip-deps.')
