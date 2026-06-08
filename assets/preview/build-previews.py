#!/usr/bin/env python3
"""Generate display-only README preview thumbnails for the mono logo variants.

The black and white marks are transparent, so each vanishes against one of
GitHub's README themes (white on light mode, black on dark mode). These
previews composite them onto a contrasting card purely for display in the
README table — the real, downloadable assets stay untouched.

The card has square corners (matching the color logo) and the mark is
*optically* centered: text is centered on its cap-to-baseline block, with any
descender (e.g. the "y" tail) hanging into the lower margin, so it reads as
centered rather than sitting low.

No third-party deps beyond Pillow:

    python3 assets/preview/build-previews.py
"""
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
LOGOS = HERE.parent / "logos"
DARK = (26, 26, 26, 255)       # #1A1A1A — backs the white mark
LIGHT = (255, 255, 255, 255)   # #FFFFFF — backs the black mark
ALPHA_THRESHOLD = 40
SQUARE_SIDE = 500              # keep square variants square
PAD = 70                      # margin around the wordmark

# (source transparent PNG, output, card color, layout)
JOBS = [
    ("logo-square--white.png", "logo-square--white.preview.png", DARK, "square"),
    ("logo-wordmark--white.png", "logo-wordmark--white.preview.png", DARK, "wordmark"),
    ("logo-square--black.png", "logo-square--black.preview.png", LIGHT, "square"),
    ("logo-wordmark--black.png", "logo-wordmark--black.preview.png", LIGHT, "wordmark"),
]


def content_bbox(mark):
    """Tight bounding box of the visible (non-transparent) pixels."""
    mask = mark.split()[3].point(lambda v: 255 if v > ALPHA_THRESHOLD else 0)
    return mask.getbbox()


def baseline_offset(content, frac=0.35):
    """Row of the typographic baseline, relative to the content's top.

    Returns the lowest row whose ink coverage is still a substantial fraction of
    the densest row — below it lies only a descender (a thin, low-coverage tail).
    """
    w, h = content.size
    alpha = content.split()[3].load()
    coverage = [sum(1 for x in range(w) if alpha[x, y] > ALPHA_THRESHOLD)
                for y in range(h)]
    threshold = max(coverage) * frac
    return max(y for y, c in enumerate(coverage) if c >= threshold)


def build(mark, color, layout):
    bbox = content_bbox(mark)
    content = mark.crop(bbox)
    w, h = content.size
    baseline = baseline_offset(content)   # cap-top is 0; baseline is here
    descender = h - 1 - baseline          # pixels hanging below the baseline

    if layout == "square":
        card_w = card_h = SQUARE_SIDE
        x = (card_w - w) // 2
        # Put the cap-to-baseline midpoint at the card's vertical center.
        y = round(card_h / 2 - baseline / 2)
    else:  # wordmark: size the card to the mark plus a uniform margin
        gap = max(PAD, descender)         # equal space above caps / below baseline
        card_w = w + 2 * PAD
        card_h = baseline + 2 * gap
        x = PAD
        y = gap

    card = Image.new("RGBA", (card_w, card_h), color)  # square corners
    card.alpha_composite(content, (x, y))
    return card, (card_w, card_h)


def main():
    for src, out, color, layout in JOBS:
        mark = Image.open(LOGOS / src).convert("RGBA")
        card, size = build(mark, color, layout)
        card.save(HERE / out)
        print(f"  wrote assets/preview/{out}  ({size[0]}x{size[1]})")


if __name__ == "__main__":
    main()
