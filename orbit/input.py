"""Attach Hyprland's ordered IPC event socket to GTK's main loop."""
import os
from pathlib import Path
import socket
import time
from orbit.events import OrbitEventDecoder


class HyprlandInput:
    def __init__(self, handle, cancel):
        self.handle, self.cancel = handle, cancel
        self.socket = None
        self.source_id = None
        self.decoder = OrbitEventDecoder()

    def start(self):
        from gi.repository import GLib
        signature = os.environ.get('HYPRLAND_INSTANCE_SIGNATURE')
        runtime = os.environ.get('XDG_RUNTIME_DIR')
        if not signature or not runtime:
            raise RuntimeError('Orbit requires a running Hyprland session')
        path = Path(runtime) / 'hypr' / signature / '.socket2.sock'
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.socket.settimeout(2)
            self.socket.connect(str(path))
            self.socket.setblocking(False)
            self.source_id = GLib.io_add_watch(
                self.socket.fileno(), GLib.IO_IN | GLib.IO_HUP | GLib.IO_ERR, self._read)
        except Exception:
            self.socket.close()
            self.socket = None
            raise

    def _read(self, channel, condition):
        from gi.repository import GLib
        try:
            while True:
                try:
                    chunk = self.socket.recv(8192)
                except BlockingIOError:
                    break
                if not chunk:
                    raise ConnectionError('Hyprland input connection closed')
                for command in self.decoder.feed(chunk):
                    if os.environ.get('ORBIT_DEBUG'):
                        print(f'Orbit input {time.monotonic():.6f}: {command}', flush=True)
                    try:
                        self.handle(command)
                    except Exception as error:
                        self.cancel()
                        print(f'Orbit input: {error}', flush=True)
            if condition & (GLib.IO_HUP | GLib.IO_ERR):
                raise ConnectionError('Hyprland input connection lost')
            return True
        except Exception as error:
            # Never leave an actionable wheel behind after losing the release channel.
            self.source_id = None
            self.socket.close()
            self.socket = None
            self.cancel()
            print(f'Orbit input: {error}', flush=True)
            return False

    def stop(self):
        from gi.repository import GLib
        if self.source_id is not None:
            GLib.source_remove(self.source_id)
            self.source_id = None
        if self.socket is not None:
            self.socket.close()
            self.socket = None
