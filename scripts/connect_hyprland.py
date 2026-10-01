#!/usr/bin/env python3
"""Connect the reviewed legacy integration, backing up and rolling back on errors."""
from datetime import datetime
from pathlib import Path
import subprocess
import tempfile


def config_errors():
    return subprocess.check_output(['hyprctl', 'configerrors'], text=True).strip()


def main():
    root = Path(__file__).resolve().parent.parent
    target = Path.home() / '.config/hypr/hyprland.conf'
    source = f'source = {root}/config/hyprland.conf'
    original = target.read_text()
    before = config_errors()
    if source not in original.splitlines():
        backup = target.with_name(f'hyprland.conf.orbit-backup-{datetime.now():%Y%m%d-%H%M%S}')
        backup.write_text(original)
        target.write_text(original.rstrip() + '\n\n# Orbit radial launcher\n' + source + '\n')
        try:
            subprocess.run(['hyprctl', 'reload'], check=True, capture_output=True)
            after = config_errors()
            if after and after != before:
                raise RuntimeError(after)
        except Exception:
            target.write_text(original)
            subprocess.run(['hyprctl', 'reload'], check=False, capture_output=True)
            raise
        print(f'Connected Orbit. Backup: {backup}')
    log = tempfile.NamedTemporaryFile(prefix='orbit-', suffix='.log', delete=False)
    subprocess.Popen([str(root / 'bin/orbit'), 'serve'], stdout=log, stderr=log, start_new_session=True)
    print(f'Orbit started. Log: {log.name}')


if __name__ == '__main__':
    main()
