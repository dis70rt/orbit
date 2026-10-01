"""Layer-shell window, dedicated icon widgets, and gesture input routing."""
import cairo
import math
import time
from gi.repository import Gtk, Gdk, Gtk4LayerShell as Layer
from orbit.icons import IconResolver
from orbit.cursor import CursorTracker
from orbit.hyprland import HyprlandClient
from orbit.motion import WheelMotion
from orbit.renderer import WheelRenderer


class WheelView:
    def __init__(self, application, settings, session):
        self.settings, self.session = settings, session
        self.motion = WheelMotion(len(settings.shortcuts), settings.animations)
        self.tick_id = None
        self.window = Gtk.ApplicationWindow(application=application, title='Orbit')
        Layer.init_for_window(self.window)
        Layer.set_namespace(self.window, 'orbit')
        Layer.set_layer(self.window, Layer.Layer.OVERLAY)
        Layer.set_keyboard_mode(self.window, Layer.KeyboardMode.NONE)
        Layer.set_exclusive_zone(self.window, -1)
        for edge in (Layer.Edge.TOP, Layer.Edge.BOTTOM, Layer.Edge.LEFT, Layer.Edge.RIGHT):
            Layer.set_anchor(self.window, edge, True)
        self.window.add_css_class('orbit')
        provider = Gtk.CssProvider()
        provider.load_from_data(b'window.orbit { background: transparent; } window.orbit image { color: #f5f5f5; }')
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.renderer = WheelRenderer(settings, session, self.motion)
        self.area = Gtk.DrawingArea(hexpand=True, vexpand=True)
        self.area.set_draw_func(self.renderer.draw)
        self.content = Gtk.Overlay(child=self.area)
        self.icons = Gtk.Fixed()
        self.icons.set_can_target(False)
        self.content.add_overlay(self.icons)
        self.window.set_child(self.content)
        self.images = []
        for shortcut in settings.shortcuts:
            path = IconResolver.resolve(shortcut.icon)
            image = Gtk.Image.new_from_file(str(path)) if path else Gtk.Image.new_from_icon_name(shortcut.icon)
            image.set_pixel_size(28)
            image.set_size_request(28, 28)
            image.set_tooltip_text(shortcut.label)
            self.icons.put(image, 0, 0)
            self.images.append(image)
        self.tracker = CursorTracker(HyprlandClient().cursor, self._global_motion)

    def _global_motion(self, point):
        if self.session.active:
            self.session.move(point)
            self.motion.select(self.session.selected, time.monotonic())
            self._schedule()

    def _schedule(self):
        if self.tick_id is None:
            self.tick_id = self.window.add_tick_callback(self._tick)

    def _tick(self, widget, clock):
        changing = self.motion.advance(time.monotonic())
        self.content.set_opacity(self.motion.visibility.value)
        center = self.renderer.center
        distance = (self.settings.radius + self.settings.dead_zone + 6) / 2 * self.motion.scale
        for index, image in enumerate(self.images):
            angle = index * math.tau / len(self.images) - math.pi / 2
            self.icons.move(image, center[0] + math.cos(angle) * distance - 14,
                            center[1] + math.sin(angle) * distance - 14)
            image.set_opacity(0.78 + 0.22 * self.motion.wedges[index].value)
        self.area.queue_draw()
        if not changing:
            self.tick_id = None
            if self.motion.visibility.target == 0:
                self.window.hide()
        return changing

    def show(self, monitor, point):
        monitors = Gdk.Display.get_default().get_monitors()
        matched = next((monitors.get_item(i) for i in range(monitors.get_n_items())
                        if monitors.get_item(i).get_connector() == monitor['name']), None)
        if matched is None:
            raise RuntimeError(f"GTK cannot locate monitor {monitor['name']}")
        Layer.set_monitor(self.window, matched)
        Layer.set_keyboard_mode(self.window, Layer.KeyboardMode.NONE)
        self.renderer.center = point[0] - monitor['x'], point[1] - monitor['y']
        self.motion.show(time.monotonic())
        self.content.set_opacity(self.motion.visibility.value)
        self.window.present()
        surface = self.window.get_surface()
        # A focusable layer makes Hyprland release all held buttons on mapping.
        # Keep the HUD input-transparent and track the compositor cursor instead.
        if surface:
            surface.set_input_region(cairo.Region())
        self.tracker.start()
        self._schedule()

    def hide(self):
        self.tracker.stop()
        if not self.window.get_visible():
            return
        # Stop cursor sampling immediately while the HUD fades out.
        Layer.set_keyboard_mode(self.window, Layer.KeyboardMode.NONE)
        surface = self.window.get_surface()
        if surface:
            surface.set_input_region(cairo.Region())
        self.motion.hide(time.monotonic())
        self._schedule()

    def close(self):
        self.tracker.close()
