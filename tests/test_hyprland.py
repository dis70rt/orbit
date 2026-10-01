import json
import os
from pathlib import Path
import socket
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch
from orbit.hyprland import HyprlandClient


class HyprlandTests(unittest.TestCase):
    def test_cursor_uses_json_command_socket_without_subprocess(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'hypr/test'
            path.mkdir(parents=True)
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
                server.bind(str(path / '.socket.sock'))
                server.listen(1)
                requests = []
                def respond():
                    connection, _ = server.accept()
                    with connection:
                        requests.append(connection.recv(256))
                        connection.sendall(json.dumps({'x': 42, 'y': -10}).encode())
                worker = Thread(target=respond, daemon=True)
                worker.start()
                with patch.dict(os.environ, {'XDG_RUNTIME_DIR': directory, 'HYPRLAND_INSTANCE_SIGNATURE': 'test'}):
                    self.assertEqual(HyprlandClient().cursor(), (42, -10))
                worker.join(timeout=2)
                self.assertFalse(worker.is_alive())
                self.assertEqual(requests, [b'j/cursorpos'])

    def test_missing_session_is_explicit(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'running Hyprland'):
                HyprlandClient().cursor()
