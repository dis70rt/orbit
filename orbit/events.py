"""Decode ordered compositor events without spawning per-gesture processes."""


class OrbitEventDecoder:
    COMMANDS = {b'custom>>orbit:press': 'show', b'custom>>orbit:release': 'release',
                b'custom>>orbit:cancel': 'cancel'}

    def __init__(self):
        self.pending = b''

    def feed(self, data):
        self.pending += data
        lines = self.pending.split(b'\n')
        self.pending = lines.pop()
        if len(self.pending) > 65536:
            raise ValueError('Hyprland event exceeded the maximum line length')
        return [self.COMMANDS[line] for line in lines if line in self.COMMANDS]
