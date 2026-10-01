# Changelog

Versions below v1.0.0 are experimental and may include incompatible changes.

## v0.1.1

- Keep the overlay unfocused so mapping it preserves Hyprland's held-button state.
- Track the global cursor without capturing pointer input.
- Route Escape cancellation through a non-consuming compositor binding.
- Deliver button press and release through an ordered compositor event stream.
- Remove per-gesture process spawning from the mouse bindings.
- Cancel an active gesture if the compositor event connection is lost.
- Add regression coverage for held gestures, fast taps, and fragmented event delivery.

## v0.1.0

Initial development version.

- Hold, aim, release shortcut selection for Hyprland.
- Center release and Escape cancellation.
- Seven configured shortcuts with dedicated monochrome icons.
- Translucent HUD, compositor blur, and frame-clock animations.
- Optional selected labels and reduced-motion setting.
- Modular Python architecture with dependency interfaces.
- Core, asset, and animation tests; pre-commit checks and CI workflow.
