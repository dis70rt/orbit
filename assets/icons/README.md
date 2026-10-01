# Icon assets

Monochrome shortcut silhouettes vendored from:

- Bootstrap Icons v1.13.1: X, LinkedIn, YouTube, Spotify, GitHub, and folder.
- Devicon v2.17.0: Visual Studio Code.

Both collections are distributed under MIT licenses. Their notices are included
in this directory. Brand names and marks belong to their respective owners.
Orbit is not affiliated with these brands or Rockstar Games.

`sources.json` records the exact upstream URLs. The shapes are preserved while
fill colors and dimensions are normalized for Orbit's monochrome HUD.
Run `python3 scripts/vendor_icons.py` to reproduce these assets. The application
loads them locally and makes no network requests for icons.
