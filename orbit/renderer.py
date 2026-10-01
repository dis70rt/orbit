"""Minimal translucent wedge rendering and selected-label typography."""
import math
from gi.repository import Pango, PangoCairo


class WheelRenderer:
    def __init__(self, settings, session, motion):
        self.settings, self.session, self.motion = settings, session, motion
        self.center = (0, 0)

    def draw(self, area, cr, width, height):
        cx, cy = self.center
        cr.translate(cx, cy)
        cr.scale(self.motion.scale, self.motion.scale)
        radius, dead = self.settings.radius, self.settings.dead_zone
        count = len(self.settings.shortcuts)
        for index in range(count):
            angle = index * math.tau / count - math.pi / 2
            half = math.pi / count - 0.012
            cr.new_path()
            cr.arc(0, 0, radius, angle - half, angle + half)
            cr.arc_negative(0, 0, dead + 6, angle + half, angle - half)
            cr.close_path()
            weight = self.motion.wedges[index].value
            color = tuple(0.055 + (channel * 0.27 - 0.055) * weight for channel in self.settings.accent)
            cr.set_source_rgba(*color, 0.48 + 0.14 * weight)
            cr.fill_preserve()
            cr.set_source_rgba(1, 1, 1, 0.10 + 0.40 * weight)
            cr.set_line_width(0.8)
            cr.stroke()
            if weight > 0.001:
                cr.arc(0, 0, radius - 2, angle - half + 0.04, angle + half - 0.04)
                cr.set_source_rgba(*self.settings.accent, weight * 0.85)
                cr.set_line_width(2)
                cr.stroke()
        cr.arc(0, 0, dead, 0, math.tau)
        cr.set_source_rgba(0.03, 0.035, 0.04, 0.36)
        cr.fill()
        selected = self.session.selected
        if selected is not None and self.settings.show_label:
            self.text(cr, self.settings.shortcuts[selected].label, 12, int(dead * 1.7))
        else:
            cr.arc(0, 0, 2, 0, math.tau)
            cr.set_source_rgba(1, 1, 1, 0.35)
            cr.fill()

    @staticmethod
    def text(cr, text, size, width):
        layout = PangoCairo.create_layout(cr)
        layout.set_text(text, -1)
        layout.set_font_description(Pango.FontDescription(f'Sans {size}'))
        layout.set_width(width * Pango.SCALE)
        layout.set_alignment(Pango.Alignment.CENTER)
        layout.set_ellipsize(Pango.EllipsizeMode.END)
        _, height = layout.get_pixel_size()
        cr.move_to(-width / 2, -height / 2)
        cr.set_source_rgba(0.96, 0.96, 0.96, 0.92)
        PangoCairo.show_layout(cr, layout)
