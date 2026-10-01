"""Read compositor state without changing the user's configuration."""
import json
import subprocess


class HyprlandClient:
    def query(self, command):
        result = subprocess.run(['hyprctl', '-j', command], check=True, capture_output=True,
                                text=True, timeout=2)
        return json.loads(result.stdout)

    def cursor(self):
        point = self.query('cursorpos')
        return point['x'], point['y']

    def monitors(self):
        return [m for m in self.query('monitors') if not m.get('disabled')]
