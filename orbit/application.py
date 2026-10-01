"""Single-instance GTK application and command-line IPC."""
import sys
from ctypes import CDLL, RTLD_GLOBAL
# Load before GTK/libwayland so layer-shell can intercept Wayland calls.
CDLL('libgtk4-layer-shell.so.0', mode=RTLD_GLOBAL)
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk4LayerShell', '1.0')
from gi.repository import Gio, Gtk
from orbit.settings import Settings
from orbit.session import WheelSession
from orbit.hyprland import HyprlandClient
from orbit.launcher import ShortcutLauncher
from orbit.controller import WheelController
from orbit.view import WheelView
from orbit.input import HyprlandInput


class OrbitApplication(Gtk.Application):
    def __init__(self, settings):
        super().__init__(application_id='io.github.orbit.Launcher',
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.settings = settings
        self.controller = None
        self.input = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.hold()
        session = WheelSession(self.settings)
        view = WheelView(self, self.settings, session)
        self.controller = WheelController(session, HyprlandClient(), view, ShortcutLauncher())
        self.input = HyprlandInput(self.controller.handle, self.controller.cancel)
        self.input.start()

    def do_shutdown(self):
        if self.input is not None:
            self.input.stop()
        if self.controller is not None:
            self.controller.view.close()
        Gtk.Application.do_shutdown(self)

    def do_command_line(self, command_line):
        args = command_line.get_arguments()[1:]
        command = args[0] if args else 'serve'
        try:
            if command == 'quit':
                self.controller.cancel()
                self.quit()
            elif command != 'serve':
                self.controller.handle(command)
            return 0
        except Exception as error:
            command_line.printerr_literal(f'Orbit: {error}\n')
            return 1


def main(command, config=None):
    return OrbitApplication(Settings.load(config)).run([sys.argv[0], command])
