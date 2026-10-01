"""Track the global cursor while a gesture is active without grabbing input."""
from concurrent.futures import ThreadPoolExecutor


class CursorTracker:
    def __init__(self, read, update, loop=None):
        self.read, self.update = read, update
        self.loop = loop
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='orbit-cursor')
        self.source_id = None
        self.future = None
        self.generation = 0

    def _loop(self):
        if self.loop is None:
            from gi.repository import GLib
            self.loop = GLib
        return self.loop

    def start(self):
        GLib = self._loop()
        self.stop()
        generation = self.generation
        self.source_id = GLib.timeout_add(20, self._tick, generation)

    def _tick(self, generation):
        if generation != self.generation:
            return False
        if self.future is None:
            self.future = self.executor.submit(self.read)
        elif self.future.done():
            try:
                point = self.future.result()
            except Exception:
                point = None
            self.future = None
            if point is not None:
                self.update(point)
        return True

    def stop(self):
        GLib = self._loop()
        self.generation += 1
        if self.source_id is not None:
            GLib.source_remove(self.source_id)
            self.source_id = None
        self.future = None

    def close(self):
        self.stop()
        self.executor.shutdown(wait=False, cancel_futures=True)
