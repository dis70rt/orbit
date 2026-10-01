"""Dispatch configured actions with explicit argument vectors."""
from pathlib import Path
from gi.repository import Gio


class ShortcutLauncher:
    def launch(self, shortcut):
        if shortcut.kind == 'command':
            Gio.Subprocess.new(list(shortcut.value), Gio.SubprocessFlags.NONE)
        elif shortcut.kind == 'application':
            app = Gio.DesktopAppInfo.new(shortcut.value)
            if app is None:
                raise RuntimeError(f'Application not installed: {shortcut.value}')
            app.launch([], None)
        else:
            uri = shortcut.value
            if shortcut.kind == 'folder':
                uri = Path(uri).expanduser().resolve().as_uri()
            Gio.AppInfo.launch_default_for_uri(uri, None)
