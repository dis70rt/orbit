# Orbit

A radial shortcut launcher for Hyprland, inspired by the GTA V weapon wheel.
Hold a button, aim at a shortcut, and release to open it.

**Version:** v0.1.1 · **Status:** experimental · **Branch:** development

Orbit is under active development. Configuration and behavior may change before
v1.0.0. There is no stable release yet.

## Features

- Cursor-centered wheel with translucent wedges and compositor blur.
- Dedicated monochrome icons for X, LinkedIn, YouTube, Spotify, VS Code, GitHub,
  and the file explorer.
- Short opening, closing, and selection animations.
- Optional selected label and reduced-motion mode.
- Configurable trigger, shortcuts, colors, size, and center cancellation zone.
- Applications, folders, websites, and explicit command arguments.
- Single background instance with a small command-line interface.

## Requirements

- Linux with a running Hyprland Wayland session.
- Python 3.10 or newer.
- PyGObject, pycairo, GTK4, and GTK4 Layer Shell with its GI typelib.
- `hyprctl` on `PATH`.

The implementation uses Python and GTK4 directly. AGS and Astal are not required.
The development environment is Fedora 43 with Hyprland 0.56.2. Other distributions
need equivalent runtime libraries; their package names may differ.

## Getting started

Clone or download this repository, then run from the checkout:

```sh
./bin/orbit --version
./bin/orbit check
./bin/orbit serve
```

`check` validates the configuration and verifies access to Hyprland and layer-shell.
`serve` starts the background instance and keeps running until `quit` is requested.

In another terminal, preview the wheel:

```sh
./bin/orbit show
```

Press Escape or run `./bin/orbit cancel` to dismiss it. Stop the daemon with
`./bin/orbit quit`.

## Hyprland integration

Choose the configuration format used by your desktop. Load only one integration
file. Both examples assume the checkout is at `~/Projects/Orbit`; edit the launcher
path in the integration file if yours is elsewhere.

### Hyprlang

Add this to `hyprland.conf`:

```ini
source = ~/Projects/Orbit/config/hyprland.conf
```

Reload Hyprland and start `./bin/orbit serve` once. The supplied `exec-once` starts
the daemon automatically on subsequent sessions.

The optional helper `python3 scripts/connect_hyprland.py` adds the source line to
`~/.config/hypr/hyprland.conf`, backs up that file, reloads the compositor, and
starts Orbit. It rolls back the source change if the reload introduces errors.
It is intended for the example checkout location and hyprlang configurations.

### Lua

Add this to `hyprland.lua`:

```lua
dofile(os.getenv('HOME') .. '/Projects/Orbit/config/hyprland.lua')
```

Reload Hyprland and start Orbit once. Subsequent sessions start it through the
`hyprland.start` event.

### Trigger and blur

Middle mouse (`mouse:274`) is the default trigger. Hold it to show the wheel,
move toward a wedge, and release to launch. Release in the center or press Escape
to cancel. The wheel remains open only until release; tapping does not toggle it.
This binding consumes middle click, including its uses in other apps.

For a modified trigger, change both hyprlang bindings to `SUPER`, or set the Lua
`trigger` to `SUPER + mouse:274`. The release binding ignores modifiers so releasing
Super first does not leave the wheel open. Both bindings emit compositor events
that Orbit receives in order through Hyprland's IPC socket. The daemon must be
running before pressing the trigger. The wheel does not grab keyboard or pointer
focus, preserving Hyprland's held-button state. Escape cancellation uses a
non-consuming compositor binding, so Escape also reaches the underlying app.

The integration files enable blur for the `orbit` layer namespace and exclude
fully transparent pixels. Hyprland's global `decoration.blur.enabled` must be
true, with `size` and `passes` at least 1. Orbit uses the compositor's existing
blur strength and does not change your global blur settings.

## Configuration

The shipped configuration is [`config/default.json`](config/default.json).
Create `~/.config/orbit/config.json` to override it, or use
`$XDG_CONFIG_HOME/orbit/config.json` when `XDG_CONFIG_HOME` is set.

A custom file can be supplied when starting the daemon:

```sh
./bin/orbit serve --config /path/to/config.json
```

Quit and restart Orbit after changing settings. A running instance keeps its
startup configuration.

| Setting | Default | Description |
| --- | --- | --- |
| `radius` | `170` | Wheel radius in logical pixels, at most 400 |
| `dead_zone` | `56` | Center cancellation radius, at least 30 and below `radius` |
| `accent` | `[0.94, 0.94, 0.94]` | Selection RGB components between 0 and 1 |
| `animations` | `true` | Set to `false` for immediate transitions |
| `show_label` | `true` | Show only the selected shortcut's name; `false` hides all text |
| `shortcuts` | Seven entries | Between 2 and 12 shortcuts, ordered clockwise from the top |

Each shortcut has `label`, `icon`, `type`, and `value` fields.

| Type | Value |
| --- | --- |
| `website` | An HTTP or HTTPS URL |
| `folder` | A folder path; `~` expands to the home directory |
| `application` | An installed desktop ID such as `org.kde.dolphin.desktop` |
| `command` | A nonempty argument array such as `["code", "/path/to/project"]` |

Icons can be a shipped `bundled:` name, an absolute SVG/PNG path, or a system icon
name. Shipped names are `x`, `linkedin`, `youtube`, `spotify`, `vscode`, `github`,
and `files`. For example:

```json
{
  "label": "VS Code",
  "icon": "bundled:vscode",
  "type": "command",
  "value": ["code"]
}
```

The default Spotify shortcut opens its web player. To use the installed desktop
client, change it to `"type": "command", "value": ["spotify"]`. The file shortcut
opens your home directory in the default file manager. VS Code requires `code`
on `PATH`.

Commands do not interpret shell syntax automatically. To explicitly run a shell
script, use `["sh", "-c", "your script"]`. Command arguments are passed unchanged.

## Development

Work happens on `development`. Versions use `v0.x.x` until the first stable release.
The current version is recorded in `VERSION` and exposed by `orbit --version`.

Enable the repository's pre-commit checks:

```sh
git config core.hooksPath .githooks
```

Run the same checks manually:

```sh
./scripts/check.sh
```

The suite covers gesture cancellation, final cursor selection, repeated events,
monitor geometry, configuration validation, icon assets, and interrupted animation
transitions. It runs without GTK or a desktop session. GitHub Actions runs the
checks on pushes and pull requests with Python 3.10 and 3.14.

Changes to rendering or desktop integration also need a live Hyprland smoke test.
See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the workflow and architecture.

## Known limitations

- The wheel stays centered at the initial cursor position and can be clipped near
  monitor edges.
- Multi-monitor scaling and rotation have unit coverage but have not been tested
  on physical multi-monitor hardware.
- The UI follows the wheel interaction and silhouette style; it does not contain
  GTA V artwork or weapon assets.

## License and attribution

Orbit is available under the [MIT License](LICENSE).
Brand icons are vendored from Bootstrap Icons v1.13.1 and Devicon v2.17.0, with
licenses and source URLs in [`assets/icons`](assets/icons). Brand names and marks
belong to their owners. Orbit is not affiliated with those brands or Rockstar Games.

## References

- [Hyprland event dispatcher](https://wiki.hypr.land/0.54.0/Configuring/Dispatchers/)
- [Hyprland bindings](https://wiki.hypr.land/Configuring/Basics/Binds/)
- [Hyprland layer rules](https://wiki.hypr.land/Configuring/Basics/Window-Rules/#layer-rules)
- [GTK frame-clock callbacks](https://docs.gtk.org/gtk4/method.Widget.add_tick_callback.html)
- [GTK4 Layer Shell](https://wmww.github.io/gtk4-layer-shell/)
- [Python layer-shell linking](https://github.com/wmww/gtk4-layer-shell/blob/main/linking.md)
