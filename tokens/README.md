# Design Tokens

Machine-readable brand tokens for crayonbox.dev — the palette and the canonical
spectrum gradient, ready to drop into a codebase instead of copy-pasting hex codes.

## Source of truth

[`brand.tokens.json`](./brand.tokens.json) is the **only** file you edit. It follows
the [W3C Design Tokens (DTCG)](https://tr.designtokens.org/format/) format, so it can
also be fed to Style Dictionary, Tokens Studio, and similar tooling.

After editing it, regenerate the consumable formats:

```sh
python3 tokens/build.py
```

The generator has no dependencies. The files below are generated — **do not edit them
by hand** (changes will be overwritten on the next build).

## Consumable formats

| File | For |
|---|---|
| [`colors.css`](./colors.css) | CSS custom properties (`var(--cb-color-blue)`, `var(--cb-gradient-brand)`) |
| [`colors.scss`](./colors.scss) | Sass variables + a `$cb-colors` map |
| [`tailwind.cjs`](./tailwind.cjs) | Tailwind theme extension (`bg-cb-blue`, `bg-cb-brand`) |
| [`colors.ts`](./colors.ts) | Typed JS/TS exports (`brandColors`, `brandGradient`, `BrandColor`) |

### Examples

```css
/* CSS */
@import "colors.css";
.hero   { background: var(--cb-gradient-brand); }
.button { background: var(--cb-color-blue); }
```

```js
// Tailwind — tailwind.config.js
const cb = require("./tokens/tailwind.cjs");
module.exports = { presets: [cb] /* … */ };
// then: <div class="bg-cb-brand"> … <span class="text-cb-indigo">
```

```ts
// TypeScript
import { brandColors, brandGradient } from "./tokens/colors.ts";
```

## The brand gradient

`gradient.brand` is the spectrum gradient used in the logo. Its angle (`73deg`) and
stop offsets are taken directly from the logo artwork so any rendered surface matches
the mark exactly — don't re-eyeball it:

```
linear-gradient(73deg,
  #D92121 0%, #FF7034 17.4105%, #FBBC2A 31.7834%, #00C696 52.8219%,
  #1D75FB 71.9403%, #5A2BB6 87.6273%, #9C5FD0 100%)
```

## Scope

These tokens cover the **brand palette and gradient** only. Neutrals (grays, semantic
text/background tokens) and per-hue tint/shade ramps are intentionally not here yet —
they're the next layer of the system.

> ⚠️ **Accessibility:** several brand hues fail WCAG AA contrast as text on white
> (Yellow, Green, Orange, and Blue/Violet for body text). Use them for fills and
> decoration; see the palette contrast guidance before using any of them for text.
