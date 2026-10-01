#!/usr/bin/env python3
"""Coordinate native package installation and per-user Orbit deployment."""
import argparse
import json
from pathlib import Path
import os
import shlex
import shutil
import subprocess
import sys

from installation.distributions import detect
from installation.files import InstallPaths, deploy


RUNTIME_PROBE = '''
import sys
assert sys.version_info >= (3, 10), 'Python 3.10 or newer is required'
from ctypes import CDLL, RTLD_GLOBAL
CDLL('libgtk4-layer-shell.so.0', mode=RTLD_GLOBAL)
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gtk4LayerShell', '1.0')
gi.require_foreign('cairo')
from gi.repository import Gtk, Gtk4LayerShell
import cairo
'''


def install_dependencies(distribution, yes):
    if not shutil.which(distribution.manager):
        raise ValueError(f'Package manager not found: {distribution.manager}')
    if not shutil.which('sudo'):
        raise ValueError('sudo is required for native package installation. Alternatively use --skip-deps.')
    if distribution.manager == 'apt-get':
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
    command = distribution.install_command(yes, hyprland_missing=not shutil.which('hyprctl'))
    print('Installing native packages:', shlex.join(command), flush=True)
    try:
        subprocess.run(['sudo', *command], check=True)
    except subprocess.CalledProcessError as error:
        raise ValueError('Native dependency installation failed. Your release may not provide '
                         'Hyprland or GTK4 Layer Shell. Use a supported release or install them '
                         'manually, then retry with --skip-deps.') from error


def main(argv=None):
    parser = argparse.ArgumentParser(description='Install Orbit for the current user. Run without sudo.')
    parser.add_argument('--dry-run', action='store_true', help='Print the plan without changing files or installing packages')
    parser.add_argument('--skip-deps', action='store_true', help='Use dependencies already installed (also supports other distros)')
    parser.add_argument('-y', '--yes', action='store_true', help='Accept package manager confirmation prompts')
    args = parser.parse_args(argv)
    try:
        if os.geteuid() == 0:
            raise ValueError('Run ./install.sh as your regular desktop user, without sudo.')
        paths = InstallPaths.for_user()
        distribution = None if args.skip_deps else detect()
        if distribution:
            command = distribution.install_command(args.yes, not shutil.which('hyprctl'))
            print(f'Distribution family: {distribution.family}')
            if distribution.manager == 'apt-get':
                print('Package index: sudo apt-get update')
            print('Dependencies:', shlex.join(['sudo', *command]))
        print(f'Application: {paths.application}\nLauncher: {paths.executable}\nIntegration: {paths.integration}')
        if args.dry_run:
            return 0
        if distribution:
            install_dependencies(distribution, args.yes)
        if not shutil.which('hyprctl') or not shutil.which('Hyprland'):
            raise ValueError('Hyprland and hyprctl are required. Install Hyprland and ensure both are on PATH.')
        probe = subprocess.run([sys.executable, '-c', RUNTIME_PROBE], capture_output=True, text=True)
        if probe.returncode:
            raise ValueError(f'GTK runtime verification failed:\n{probe.stderr.strip()}')
        deploy(Path(__file__).resolve().parent.parent, paths, Path(sys.executable))
        print('\nOrbit installed. Add ~/.local/bin to PATH if it is not already there.')
        print('Load ONE integration file in your Hyprland configuration:')
        print(f'  Hyprlang: source = "{paths.integration / "hyprland.conf"}"')
        print(f'  Lua: dofile({json.dumps(str(paths.integration / "hyprland.lua"))})')
        print('Remove any previous Orbit source/dofile line to avoid duplicate bindings.')
        print(f'In your Hyprland session, reload configuration, then run: {shlex.quote(str(paths.executable))} check')
        print(f'Start once with: {shlex.quote(str(paths.executable))} serve')
        print('Future Hyprland sessions start Orbit through the integration file.')
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'Orbit installer: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
