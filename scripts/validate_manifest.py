#!/usr/bin/env python3
"""Validate a theme-config.js manifest without depending on a JS parser package."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

# The renderer draws six hue stops around a loop and mixes each color with its
# array neighbors.
RENDERED_COLORS = 6


def load_manifest(path: pathlib.Path) -> dict:
    program = (
        "global.window={};require(require('path').resolve(process.argv[1]));"
        "process.stdout.write(JSON.stringify(window.SPECTRAL_THEME));"
    )
    result = subprocess.run(
        ["node", "-e", program, str(path)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate(config: dict) -> list[str]:
    errors: list[str] = []
    required = ("schemaVersion", "mode", "label", "preset", "seed", "overallColorIntensity", "base", "colors", "field", "output")
    for key in required:
        require(key in config, f"missing top-level field: {key}", errors)
    if errors:
        return errors

    require(config["mode"] in ("opal", "obsidian"), "mode must be opal or obsidian", errors)
    require(0 <= config["overallColorIntensity"] <= 1, "overallColorIntensity must be in [0, 1]", errors)
    base = config["base"].get("oklch", {})
    require(0 <= base.get("l", -1) <= 1, "base OKLCH lightness must be in [0, 1]", errors)
    require(0 <= base.get("c", -1) <= 0.4, "base OKLCH chroma must be in [0, 0.4]", errors)
    require(0 <= base.get("h", -1) < 360, "base OKLCH hue must be in [0, 360)", errors)

    colors = config["colors"]
    require(3 <= len(colors) <= 12, "colors must contain 3 to 12 entries", errors)
    ids: set[str] = set()
    for index, color in enumerate(colors):
        prefix = f"colors[{index}]"
        for key in ("id", "label", "oklch", "srgbFallback", "intensity", "peakOpacity", "fieldScale", "phase"):
            require(key in color, f"{prefix} missing {key}", errors)
        if "id" in color:
            require(color["id"] not in ids, f"duplicate color id: {color['id']}", errors)
            ids.add(color["id"])
        oklch = color.get("oklch", {})
        require(0 <= oklch.get("l", -1) <= 1, f"{prefix}.oklch.l must be in [0, 1]", errors)
        require(0 <= oklch.get("c", -1) <= 0.4, f"{prefix}.oklch.c must be in [0, 0.4]", errors)
        require(0 <= oklch.get("h", -1) < 360, f"{prefix}.oklch.h must be in [0, 360)", errors)
        require(0 <= color.get("intensity", -1) <= 1, f"{prefix}.intensity must be in [0, 1]", errors)
        require(0 <= color.get("peakOpacity", -1) <= 1, f"{prefix}.peakOpacity must be in [0, 1]", errors)
        require(color.get("fieldScale", 0) > 0, f"{prefix}.fieldScale must be positive", errors)
        require(len(color.get("phase", [])) == 2, f"{prefix}.phase must contain two values", errors)

    field = config["field"]
    for key in ("scale", "octaves", "warpStrength", "motionSpeed", "staticTime", "ditherStrength"):
        require(key in field, f"field missing {key}", errors)
    require(field.get("scale", 0) > 0, "field.scale must be positive", errors)
    require(field.get("octaves", 0) >= 1, "field.octaves must be at least 1", errors)
    require(0 <= field.get("warpStrength", -1) <= 1, "field.warpStrength must be in [0, 1]", errors)
    require(0 <= field.get("ditherStrength", -1) <= 1, "field.ditherStrength must be in [0, 1]", errors)
    if config["mode"] == "obsidian" or "luminanceCap" in field:
        require(0 < field.get("luminanceCap", 0) <= 1, "field.luminanceCap must be in (0, 1]", errors)
    return errors


def hue_travel(hues: list[float]) -> float:
    steps = (abs(a - b) % 360 for a, b in zip(hues, hues[1:] + hues[:1]))
    return sum(min(step, 360 - step) for step in steps)


def best_hue_travel(hues: list[float]) -> float:
    ordered = sorted(h % 360 for h in hues)
    widest = max([b - a for a, b in zip(ordered, ordered[1:])] + [ordered[0] + 360 - ordered[-1]])
    return 360.0 if widest <= 180 else 2 * (360 - widest)


def collect_warnings(config: dict) -> list[str]:
    notes: list[str] = []
    colors = config.get("colors", [])
    hues = [float(color.get("oklch", {}).get("h", 0)) for color in colors]
    if len(hues) >= 3:
        travel, best = hue_travel(hues), best_hue_travel(hues)
        if travel > best * 1.1:
            notes.append(
                f"colors are not in hue order: neighbor hue steps add up to {travel:.0f} degrees, "
                f"the best order gives {best:.0f}. The renderer mixes each color with its array "
                "neighbors, and near-complementary neighbors mix toward gray."
            )
    if colors and len(colors) != RENDERED_COLORS:
        notes.append(
            f"the renderer draws {RENDERED_COLORS} hue stops; with {len(colors)} colors it "
            + ("ignores the extra ones" if len(colors) > RENDERED_COLORS else "repeats the last color to fill them")
        )
    return notes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=pathlib.Path)
    args = parser.parse_args()
    config = load_manifest(args.config.resolve())
    errors = validate(config)
    if errors:
        print(json.dumps({"status": "invalid", "errors": errors}, ensure_ascii=False, indent=2))
        sys.exit(1)
    report = {"status": "valid", "mode": config["mode"], "preset": config["preset"], "colors": len(config["colors"])}
    notes = collect_warnings(config)
    if notes:
        report["warnings"] = notes
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
