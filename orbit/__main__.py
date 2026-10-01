"""CLI parsing and dependency diagnostics."""
import argparse
import sys
from orbit.settings import Settings
from orbit import __version__


def main():
    parser = argparse.ArgumentParser(description='Orbit radial shortcut launcher')
    parser.add_argument('--version', action='version', version=f'Orbit v{__version__}')
    parser.add_argument('command', nargs='?', default='serve', choices=['serve', 'show', 'release', 'cancel', 'quit', 'check'])
    parser.add_argument('--config', help='JSON config path; restart the daemon after edits')
    args = parser.parse_args()
    try:
        settings = Settings.load(args.config)
        from orbit.application import main as run
        if args.command == 'check':
            from orbit.hyprland import HyprlandClient
            from gi.repository import Gtk, Gtk4LayerShell
            Gtk.init()
            client = HyprlandClient()
            print(f'{len(settings.shortcuts)} shortcuts; cursor={client.cursor()}; monitors={len(client.monitors())}')
            if not Gtk4LayerShell.is_supported():
                raise RuntimeError('Wayland layer-shell protocol is unavailable')
            print('GTK4, Cairo and layer-shell ready')
            return 0
        return run(args.command, args.config)
    except Exception as error:
        print(f'Orbit: {error}', file=sys.stderr)
        return 1


sys.exit(main())
