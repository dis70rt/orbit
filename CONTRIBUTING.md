# Contributing to Orbit

Orbit is experimental. Submit changes against `development` and describe the
behavior they change, how they were tested, and any remaining limitations.

## Local workflow

1. Check out `development` and enable hooks with `git config core.hooksPath .githooks`.
2. Keep each module focused on one responsibility.
3. Add behavioral tests for changes to selection, configuration, animation, or actions.
4. Run `./scripts/check.sh` before committing. Do not bypass the pre-commit hook.
5. For UI changes, also check a running Hyprland session.

Use concise commit subjects that describe the resulting change. Do not commit
local configurations, logs, caches, credentials, or unrelated files.

## Desktop smoke test

Run `./bin/orbit check`, then start `./bin/orbit serve`. Verify:

- Opening at the cursor, moving through wedges, and selected icon/label feedback.
- Center release and Escape cancellation without launching.
- One action per release and no action from a release after cancellation.
- Immediate input/focus restoration while the closing animation finishes.
- A new hold during a closing animation.
- `animations: false` and `show_label: false`.
- Blur inside the wheel with a clear desktop outside it.
- `./bin/orbit quit` closes the daemon cleanly.

The mouse bindings use Hyprland's `event` dispatcher. Test the real event channel
as well as CLI preview commands. Press and release must remain ordered, including
a fast tap. CLI-only tests do not prove physical mouse release behavior.

Record the Hyprland version and display arrangement when reporting desktop issues.

## Architecture

| Module | Responsibility |
| --- | --- |
| `settings` | Immutable settings and validation |
| `geometry` | Radial hit testing and monitor geometry |
| `session` | Hold, aim, release state |
| `ports` | Controller service interfaces |
| `controller` | Gesture lifecycle and action dispatch orchestration |
| `hyprland` | Compositor queries |
| `events` | Pure ordered event decoding |
| `input` | Compositor socket connection and main-loop integration |
| `cursor` | Global cursor sampling during active gestures |
| `launcher` | Configured action execution |
| `icons` | Asset resolution |
| `motion` | Pure transition state and easing |
| `renderer` | Cairo wedge and label drawing |
| `view` | GTK window, input, and frame-clock scheduling |
| `application` | Single-instance application and IPC |
| `__main__` | CLI parsing and diagnostics |

Keep GTK imports out of the pure state modules. The controller uses structural
interfaces so services can be replaced by test doubles. The overlay must use keyboard mode NONE: Hyprland clears held mouse buttons
when a focusable layer maps. Frame-clock callbacks stop
when transitions settle; the hidden wheel should not run an animation timer.

## Versions and assets

Keep `VERSION` and `orbit.__version__` consistent. Use `v0.x.x` tags until a stable
v1.0.0 release and document changes in `CHANGELOG.md`.

Icons are pinned and vendored. `python3 scripts/vendor_icons.py` refreshes the
existing pinned assets and license notices; it needs network access. Preserve
`sources.json` and the upstream license files when changing asset sources.
