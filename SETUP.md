# Profile README

GitHub displays README.md on your profile when it is in a public repository
named exactly `3z4k`, owned by `3z4k`.

All displayed artwork is stored in assets/. There are no remote image-service
dependencies. Static PNG alternatives are selected for visitors who request
reduced motion. The text and image descriptions remain available without animation.

## Rebuild the artwork

Use Python 3.10 or newer and install requirements.txt in a virtual environment.

```sh
python3 scripts/build_assets.py
```

The intro regenerates independently. To also regenerate the terminal gallery,
pass a directory containing the original terminal-aquarium/aquarium.py and
terminal-roadster/roadster.py projects:

```sh
python3 scripts/build_assets.py --terminal-root /path/to/your/projects
```

The gallery uses the real renderers, without running either terminal UI. The
terminal projects remain local; the profile links only to existing public repos.

## Visual direction

Ink `#0C1524`, panel `#121F32`, blue `#8ABEFF`, apricot `#FFBF86`,
paper `#E6EDF3`, slate `#8DA0B8`. Menlo or DejaVu Sans Mono throughout.
One animated ASCII wordmark carries the identity; the rest stays readable and
compact. Each GIF begins on a complete, legible frame. PNGs preserve the same
composition for still previews and reduced motion.
