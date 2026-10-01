"""Pure radial hit testing and monitor coordinate conversion."""
import math


def segment_at(x, y, count, dead_zone):
    if math.hypot(x, y) <= dead_zone:
        return None
    # Segment zero points north; indices advance clockwise.
    angle = (math.atan2(y, x) + math.pi / 2) % math.tau
    return int((angle + math.pi / count) % math.tau / (math.tau / count))


def monitor_bounds(monitor):
    width, height = monitor['width'], monitor['height']
    if monitor.get('transform', 0) % 2:
        width, height = height, width
    return monitor['x'], monitor['y'], width / monitor['scale'], height / monitor['scale']


def monitor_at(monitors, point):
    for monitor in monitors:
        x, y, width, height = monitor_bounds(monitor)
        if x <= point[0] < x + width and y <= point[1] < y + height:
            return monitor
    raise RuntimeError('Cursor is not on an active monitor')
