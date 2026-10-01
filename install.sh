#!/bin/sh
# Use the distribution's Python so native GTK bindings remain available.
set -eu
ORBIT_SOURCE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ ! -x /usr/bin/python3 ]; then
    echo 'Orbit installer: install your distribution python3 package first.' >&2
    exit 1
fi
if ! /usr/bin/python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
    echo 'Orbit installer: Python 3.10 or newer is required.' >&2
    exit 1
fi
exec /usr/bin/python3 "$ORBIT_SOURCE/scripts/install.py" "$@"
