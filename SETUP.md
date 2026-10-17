# Profile README

README.md appears on the GitHub profile at https://github.com/3z4k.

The profile has one 12-second ASCII animation: Kaze Kylan rises behind layered
Himalayan ridgelines, with a small Nepal flag. A still PNG is selected when a
visitor prefers reduced motion. Two cards below show public GitHub profile
counts and the language mix of original public projects.

All images live in this repository. There are no third-party card servers,
project links, or project previews in the README.

## Regenerate

The mountain animation needs Python 3.10+, Pillow from requirements.txt, and
Menlo or DejaVu Sans Mono:

```sh
python3 scripts/build_mountains.py
```

The card generator uses only Python's standard library and the public GitHub
API. GITHUB_TOKEN is optional locally and supplied by GitHub Actions:

```sh
python3 scripts/build_cards.py
```

The Refresh GitHub cards workflow is scheduled daily and can also be started
manually. If GitHub Actions is unavailable, the committed cards continue to
display the last successfully generated public data, with its update date.
Its token can write the two card SVGs in this repository. Language percentages
use code bytes from original public repos, excluding this profile repository
and forks. Private repositories and private activity are never queried.

## Visual direction

Night `#08131C`, glacier `#85B5C4`, snow `#D9ECEC`, dawn `#D9957D`,
crimson `#C12D44`. Monospace throughout. The name is composited behind opaque
mountain silhouettes, rises slowly, holds, then fades before the loop restarts.
