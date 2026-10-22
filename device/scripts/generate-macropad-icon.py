#!/usr/bin/env python3
"""Render the shared MacroPad SVG into macOS app and menu-bar resources.

Requires Python/Pillow, Node.js and the workspace's existing sharp installation.
The Windows icon and tray resources are intentionally read-only inputs here.
"""

from __future__ import annotations

import json
from pathlib import Path
import struct
import subprocess

from PIL import Image


DEVICE = Path(__file__).resolve().parents[1]
RESOURCES = DEVICE / "app" / "resources"
SHARP = DEVICE.parent / "website" / "node_modules" / "sharp"
SOURCE = RESOURCES / "macropad-icon.svg"
ICON_PNG = RESOURCES / "macropad-icon-1024.png"
ICON_ICNS = DEVICE / "app" / "macos" / "MacroPad.icns"
TRAY_PNG = RESOURCES / "macropad-tray-template.png"
TRAY_RGBA = RESOURCES / "macropad-tray-template-96.rgba"


def render_svg(source: str, destination: Path, size: int) -> None:
    renderer = """
const sharp = require(process.argv[1]);
sharp(Buffer.from(process.argv[2]), { density: 384 })
  .resize(Number(process.argv[4]), Number(process.argv[4]))
  .ensureAlpha().png().toFile(process.argv[3])
  .catch(error => { console.error(error); process.exit(1); });
"""
    subprocess.run(
        ["node", "-e", renderer, str(SHARP), source, str(destination), str(size)],
        check=True,
    )


def icns_chunks(path: Path) -> list[str]:
    data = path.read_bytes()
    magic, length = struct.unpack(">4sI", data[:8])
    assert magic == b"icns" and length == len(data), "Invalid ICNS header"
    chunks = []
    offset = 8
    while offset < length:
        name, chunk_length = struct.unpack(">4sI", data[offset : offset + 8])
        assert chunk_length >= 8 and offset + chunk_length <= length
        chunks.append(name.decode("ascii"))
        offset += chunk_length
    assert offset == length
    return chunks


def main() -> None:
    assert SOURCE.is_file(), f"Missing source: {SOURCE}"
    assert SHARP.is_dir(), f"Missing existing sharp installation: {SHARP}"
    ICON_ICNS.parent.mkdir(parents=True, exist_ok=True)
    render_svg(SOURCE.read_text(encoding="utf-8"), ICON_PNG, 1024)
    with Image.open(ICON_PNG) as image:
        assert image.size == (1024, 1024)
        image.convert("RGBA").save(ICON_ICNS, format="ICNS")

    # A transparent monochrome version of the same input-grid mark. macOS
    # uses alpha as its template mask and supplies the menu-bar foreground.
    keys = "".join(
        f'<rect x="{x}" y="{y}" width="10" height="10" rx="2"/>'
        for y in (20, 36, 52)
        for x in (20, 36, 52, 68)
    )
    template = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" '
        'viewBox="0 0 96 96">'
        '<rect x="8" y="8" width="80" height="80" rx="14" '
        'fill="none" stroke="#000" stroke-width="6"/>'
        f'<g fill="#000">{keys}'
        '<rect x="20" y="68" width="10" height="10" rx="2"/>'
        '<rect x="52" y="68" width="26" height="10" rx="2"/></g>'
        '<circle cx="41" cy="73" r="5" fill="none" stroke="#000" '
        'stroke-width="3"/></svg>'
    )
    render_svg(template, TRAY_PNG, 96)
    with Image.open(TRAY_PNG) as image:
        rgba = image.convert("RGBA")
        assert rgba.size == (96, 96)
        pixels = rgba.tobytes()
        alpha = pixels[3::4]
        assert min(alpha) == 0 and max(alpha) == 255
        assert any(value == 0 for value in alpha)
        assert any(value > 0 for value in alpha)
        assert all(value == 0 for index, value in enumerate(pixels) if index % 4 != 3)
        TRAY_RGBA.write_bytes(pixels)
        assert TRAY_RGBA.stat().st_size == 96 * 96 * 4

    with Image.open(ICON_ICNS) as image:
        sizes = image.info.get("sizes", [])
        assert (1024, 1024, 1) in sizes or (512, 512, 2) in sizes
    print(json.dumps({
        "icon_png": str(ICON_PNG),
        "icon_icns": str(ICON_ICNS),
        "icns_chunks": icns_chunks(ICON_ICNS),
        "icns_sizes": sizes,
        "tray_png": str(TRAY_PNG),
        "tray_rgba": str(TRAY_RGBA),
        "transparent_pixels": sum(value == 0 for value in alpha),
        "glyph_pixels": sum(value > 0 for value in alpha),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
