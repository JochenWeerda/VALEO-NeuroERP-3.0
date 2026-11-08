/** Shared mask tokens: text AA and functional input/focus contours in all themes. */
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'

const css = readFileSync(join(__dirname, '../index.css'), 'utf8')
const palette = readFileSync(join(__dirname, '../styles/tokens/palette.css'), 'utf8')
type Tokens = Record<string, string>
function declarations(text: string): Tokens {
  return Object.fromEntries([...text.matchAll(/(--[\w-]+):\s*([^;]+);/g)].map(m => [m[1], m[2].trim()]))
}
const base = declarations(palette.split('.dark {')[0])
function themeTokens(theme: string): Tokens {
  if (theme.startsWith('meridian-') || theme.startsWith('terra-')) {
    const brand = theme.split('-')[0]
    const source = readFileSync(join(__dirname, `../styles/design-tokens-${brand}.css`), 'utf8')
    const marker = brand === 'meridian' ? '[data-theme="meridian"].dark,' : ':root[data-theme="terra"].dark,'
    const [light, dark] = source.split(marker)
    if (!dark) throw new Error(`Missing branded dark theme ${brand}`)
    return { ...themeTokens('light'), ...declarations(light), ...(theme.endsWith('dark') ? declarations(dark.split('}')[0]) : {}) }
  }
  const section = css.slice(css.indexOf('/* Tailwind design system variables */'))
  const light = declarations(section.split('.dark {')[0])
  if (theme === 'light') return { ...base, ...light }
  const selector = theme === 'dark' ? '.dark {' : '.theme-warehouse {'
  const block = section.split(selector)[1]?.split('}')[0]
  if (!block) throw new Error(`Missing theme ${theme}`)
  return { ...base, ...light, ...declarations(block) }
}
function luminance(value: string, tokens: Tokens, depth = 0): number {
  if (depth > 12) throw new Error('Cyclic theme token')
  const ref = /^var\((--[\w-]+)\)$/.exec(value)
  if (ref) {
    if (!tokens[ref[1]]) throw new Error(`Missing ${ref[1]}`)
    return luminance(tokens[ref[1]], tokens, depth + 1)
  }
  const parts = /^([\d.]+)\s+([\d.]+)%\s+([\d.]+)%$/.exec(value)
  if (!parts) throw new Error(`Unsupported HSL ${value}`)
  const h = +parts[1] / 60, s = +parts[2] / 100, l = +parts[3] / 100
  const c = (1 - Math.abs(2 * l - 1)) * s, x = c * (1 - Math.abs(h % 2 - 1)), m = l - c / 2
  const rgb = h < 1 ? [c, x, 0] : h < 2 ? [x, c, 0] : h < 3 ? [0, c, x] : h < 4 ? [0, x, c] : h < 5 ? [x, 0, c] : [c, 0, x]
  const linear = rgb.map(v => v + m).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4)
  return linear[0] * .2126 + linear[1] * .7152 + linear[2] * .0722
}
const textPairs = [
  ['foreground', 'background'], ['card-foreground', 'card'], ['popover-foreground', 'popover'],
  ['primary-foreground', 'primary'], ['secondary-foreground', 'secondary'],
  ['accent-foreground', 'accent'], ['destructive-foreground', 'destructive'],
  ['destructive', 'background'], ['muted-foreground', 'background'], ['muted-foreground', 'muted'],
] as const
for (const theme of ['light', 'dark', 'warehouse', 'meridian-dark', 'terra-light', 'terra-dark']) {
  describe(`${theme}: central Studio and native mask palette`, () => {
    const tokens = themeTokens(theme)
    for (const [fg, bg] of [...textPairs, ['input', 'background'], ['input', 'muted'], ['ring', 'background']] as const) {
      const minimum = fg === 'input' || fg === 'ring' ? 3 : 4.5
      it(`${fg} on ${bg} >= ${minimum}:1`, () => {
        const a = luminance(tokens[`--${fg}`], tokens), b = luminance(tokens[`--${bg}`], tokens)
        expect((Math.max(a, b) + .05) / (Math.min(a, b) + .05)).toBeGreaterThanOrEqual(minimum)
      })
    }
  })
}
