# Liuguang Banlan UI

An Agent Skills package for building parameterized front-end workbenches in two fixed visual modes:

- **流光溢彩白 / Iridescent White** (`opal`)
- **五彩斑斓黑 / Colorful Black** (`obsidian`)

The skill keeps the information layer stable while treating the spectral field as a controlled environmental layer. It includes OKLCH style contracts, a continuous WebGL field with a CSS fallback, responsive starter templates, a visual-capability gate, screenshot QA, and deterministic pixel measurements.

## Install

Copy this directory into the skill location used by your agent, or install it from the repository with your agent's skill manager. The `SKILL.md` file is the entry point; `references/`, `scripts/`, and `assets/` are loaded on demand.

## Parameter reporting

Every starter exposes `overallColorIntensity` and per-color `intensity` values. Reports should also include each color's OKLCH values, peak opacity, spatial scale, phase, measured coverage, and effective share. If the executing model cannot inspect screenshots natively, the report must mark visual verification as `visual-unverified` even when deterministic pixel checks pass.

## Development

Run the script tests with `python -m unittest discover -s tests`. Preview the starters with `python scripts/serve_preview.py . --port 8000` and open `/assets/starter/`; the server disables caching so an edited manifest is not served stale.

## License

Apache-2.0. See [LICENSE.txt](LICENSE.txt).
