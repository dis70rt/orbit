"""Query the compositor directly through its local IPC command socket."""
import json
import os
from pathlib import Path
import socket


class HyprlandClient:
    def query(self, command):
        runtime = os.environ.get('XDG_RUNTIME_DIR')
        signature = os.environ.get('HYPRLAND_INSTANCE_SIGNATURE')
        if not runtime or not signature:
            raise RuntimeError('Orbit requires a running Hyprland session')
        path = Path(runtime) / 'hypr' / signature / '.socket.sock'
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(2)
            connection.connect(str(path))
            connection.sendall(f'j/{command}'.encode())
            chunks = []
            while chunk := connection.recv(8192):
                chunks.append(chunk)
        return json.loads(b''.join(chunks))

    def cursor(self):
        point = self.query('cursorpos')
        return point['x'], point['y']

    def monitors(self):
        return [m for m in self.query('monitors') if not m.get('disabled')]
