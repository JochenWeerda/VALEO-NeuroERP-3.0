import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative } from 'node:path'
import { describe, expect, it } from 'vitest'

/**
 * Studio Design-Token-Invariante (Micro-Labels): keine arbiträren 10/11px-Textklassen
 * in pages/ und zentralen Mask-Builder-/Patterns-Pfaden.
 * Ausnahme: Feed-Rationsoptimierung (eigene Visual-Surface, Nachzug).
 */
const ROOTS = [
  join(__dirname, '../../pages'),
  join(__dirname, '../../components/mask-builder'),
  join(__dirname, '../../components/patterns'),
  join(__dirname, '../../components/dms'),
]

const ALLOWLIST = new Set([
  'components/mask-builder/specialized/feed/ration-optimization-surface.tsx',
])

const FORBIDDEN = new RegExp(String.raw`text-\[(?:10|11)px\]`)

function walkTsx(dir: string, out: string[] = []): string[] {
  for (const name of readdirSync(dir)) {
    const path = join(dir, name)
    const st = statSync(path)
    if (st.isDirectory()) {
      if (name === 'node_modules' || name === 'dist') continue
      walkTsx(path, out)
      continue
    }
    if (name.endsWith('.tsx')) out.push(path)
  }
  return out
}

describe('Design-Token Micro-Label Ratsche', () => {
  it('keine arbiträren 10/11px-Textklassen außerhalb der Allowlist', () => {
    const base = join(__dirname, '../..')
    const hits: string[] = []
    for (const root of ROOTS) {
      for (const file of walkTsx(root)) {
        const rel = relative(base, file).replace(/\\/g, '/')
        if (ALLOWLIST.has(rel)) continue
        const text = readFileSync(file, 'utf8')
        if (FORBIDDEN.test(text)) hits.push(rel)
      }
    }
    expect(hits, hits.join('\n')).toEqual([])
  })
})
