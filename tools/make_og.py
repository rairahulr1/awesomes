#!/usr/bin/env python3
"""Generate docs/public/og.png — the Open Graph card used for link previews.

No image libraries are available on this host and no rasteriser is installed, so this
writes the PNG directly: RGB scanlines, filter type 0, zlib-deflated. The wordmark is a
hand-coded 5x7 bitmap font scaled up, which is enough for lowercase text.

Re-run after changing anything about the design:
    python3 tools/make_og.py
"""

import pathlib
import struct
import zlib

W, H = 1200, 630
BG = (0x0D, 0x11, 0x17)
ACCENT = (0x58, 0xA6, 0xFF)
DIM = (0x21, 0x2B, 0x36)

# 5x7 lowercase bitmap font — only the glyphs the wordmark needs.
GLYPHS = {
    "a": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", ".###."),
    "w": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "e": (".###.", "#...#", "#...#", "#####", "#....", "#...#", ".###."),
    "s": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "o": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "m": ("##.##", "#.#.#", "#.#.#", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
}
GLYPH_W, GLYPH_H = 5, 7
TRACKING = 1  # blank columns between glyphs

WORDMARK = "awesomes"
SCALE = 17


def blank():
    return [[BG for _ in range(W)] for _ in range(H)]


def fill_rect(px, x0, y0, w, h, colour):
    for y in range(max(0, y0), min(H, y0 + h)):
        row = px[y]
        for x in range(max(0, x0), min(W, x0 + w)):
            row[x] = colour


def text_width(word, scale):
    return len(word) * (GLYPH_W + TRACKING) * scale - TRACKING * scale


def draw_text(px, word, x0, y0, scale, colour):
    cursor = x0
    for ch in word:
        for r, line in enumerate(GLYPHS[ch]):
            for c, cell in enumerate(line):
                if cell == "#":
                    fill_rect(px, cursor + c * scale, y0 + r * scale, scale, scale, colour)
        cursor += (GLYPH_W + TRACKING) * scale


def write_png(path, px):
    raw = bytearray()
    for row in px:
        raw.append(0)  # filter type 0 (None)
        for r, g, b in row:
            raw += bytes((r, g, b))

    def chunk(tag, data):
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def main():
    px = blank()

    margin = 110
    word_w = text_width(WORDMARK, SCALE)
    word_h = GLYPH_H * SCALE
    top = (H - word_h) // 2 - 40

    draw_text(px, WORDMARK, margin, top, SCALE, ACCENT)

    # Accent rule under the wordmark, sized to the wordmark rather than the canvas.
    fill_rect(px, margin, top + word_h + 46, word_w, 6, ACCENT)
    fill_rect(px, margin + word_w, top + word_h + 46, 120, 6, DIM)

    # Footer rule.
    fill_rect(px, 0, H - 6, W, 6, DIM)

    out = pathlib.Path(__file__).resolve().parent.parent / "docs" / "public" / "og.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    write_png(out, px)
    print(f"wrote {out} ({out.stat().st_size} bytes, {W}x{H})")


if __name__ == "__main__":
    main()