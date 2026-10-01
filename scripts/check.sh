#!/bin/sh
set -eu
ORBIT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ORBIT_ROOT"
sh -n install.sh bin/orbit scripts/check.sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q orbit scripts
if command -v luajit >/dev/null 2>&1; then
    ORBIT_LUA_CHECK=$(mktemp)
    trap 'rm -f "$ORBIT_LUA_CHECK"' EXIT
    luajit -b config/hyprland.lua "$ORBIT_LUA_CHECK"
fi
git diff --check
git diff --cached --check
