#!/usr/bin/env python3
"""Generate consumable token files from brand.tokens.json (the source of truth).

No third-party dependencies. Run from the repo root or anywhere:

    python3 tokens/build.py

Emits, alongside the source: colors.css, colors.scss, tailwind.cjs, colors.ts.
Do not edit the generated files by hand — change brand.tokens.json and re-run.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "brand.tokens.json"
PREFIX = "cb"  # crayonbox
BANNER = "Generated from brand.tokens.json by tokens/build.py — do not edit by hand."


def resolve(ref, tokens):
    """Resolve a DTCG alias like '{color.red}' to its $value; pass hex through."""
    m = re.fullmatch(r"\{([^}]+)\}", ref.strip()) if isinstance(ref, str) else None
    if not m:
        return ref
    node = tokens
    for key in m.group(1).split("."):
        node = node[key]
    return node["$value"]


def pct(position):
    """Format a 0..1 stop position as a trimmed CSS percentage."""
    s = f"{position * 100:.4f}".rstrip("0").rstrip(".")
    return f"{s}%"


def load():
    tokens = json.loads(SRC.read_text())
    colors = {
        name: node["$value"]
        for name, node in tokens["color"].items()
        if not name.startswith("$")
    }
    grad = tokens["gradient"]["brand"]
    angle = grad["$extensions"]["dev.crayonbox.angle"]
    stops = [(resolve(s["color"], tokens), s["position"]) for s in grad["$value"]]
    gradient = f"linear-gradient({angle}, " + ", ".join(
        f"{hex_} {pct(pos)}" for hex_, pos in stops
    ) + ")"
    return colors, gradient


def write(path, text):
    path.write_text(text)
    print(f"  wrote {path.relative_to(HERE.parent)}")


def build_css(colors, gradient):
    lines = [f"/* {BANNER} */", ":root {"]
    lines += [f"  --{PREFIX}-color-{n}: {h};" for n, h in colors.items()]
    lines.append(f"  --{PREFIX}-gradient-brand: {gradient};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def build_scss(colors, gradient):
    lines = [f"// {BANNER}", ""]
    lines += [f"${PREFIX}-color-{n}: {h};" for n, h in colors.items()]
    lines.append("")
    lines.append(f"${PREFIX}-colors: (")
    lines += [f'  "{n}": ${PREFIX}-color-{n},' for n in colors]
    lines.append(");")
    lines.append("")
    lines.append(f"${PREFIX}-gradient-brand: {gradient};")
    return "\n".join(lines) + "\n"


def build_tailwind(colors, gradient):
    color_entries = ",\n".join(f'        {n}: "{h}"' for n, h in colors.items())
    return (
        f"/** {BANNER} */\n"
        "module.exports = {\n"
        "  theme: {\n"
        "    extend: {\n"
        "      colors: {\n"
        f'        {PREFIX}: {{\n{indent(color_entries)}\n        }}\n'
        "      },\n"
        "      backgroundImage: {\n"
        f'        "{PREFIX}-brand": "{gradient}"\n'
        "      }\n"
        "    }\n"
        "  }\n"
        "};\n"
    )


def indent(block, spaces=2):
    pad = " " * spaces
    return "\n".join(pad + line for line in block.splitlines())


def build_ts(colors, gradient):
    entries = ",\n".join(f'  {n}: "{h}"' for n, h in colors.items())
    return (
        f"// {BANNER}\n"
        f"export const brandColors = {{\n{entries}\n}} as const;\n\n"
        "export type BrandColor = keyof typeof brandColors;\n\n"
        f'export const brandGradient = "{gradient}";\n'
    )


def main():
    colors, gradient = load()
    print(f"Building tokens ({len(colors)} colors)…")
    write(HERE / "colors.css", build_css(colors, gradient))
    write(HERE / "colors.scss", build_scss(colors, gradient))
    write(HERE / "tailwind.cjs", build_tailwind(colors, gradient))
    write(HERE / "colors.ts", build_ts(colors, gradient))
    print("Done.")


if __name__ == "__main__":
    main()
