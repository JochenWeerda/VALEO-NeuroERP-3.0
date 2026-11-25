import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative } from 'node:path'
import { describe, expect, it } from 'vitest'

/**
 * Studio Tabs-Invariante: jede TabsList braucht ein aria-label
 * (Accessible Name fuer role=tablist). Pages + Components.
 */
const ROOTS = [
  join(__dirname, '../../pages'),
  join(__dirname, '../../components'),
]

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

describe('TabsList aria-label Ratsche', () => {
  it('jedes TabsList in pages/ und components/ hat aria-label', () => {
    const missing: string[] = []
    for (const root of ROOTS) {
      for (const file of walkTsx(root)) {
        const text = readFileSync(file, 'utf8')
        if (!text.includes('TabsList')) continue
        const re = /<TabsList([^>]*)>/g
        let match: RegExpExecArray | null
        while ((match = re.exec(text)) !== null) {
          const attrs = match[1] ?? ''
          if (!attrs.includes('aria-label')) {
            missing.push(relative(join(__dirname, '../..'), file))
          }
        }
      }
    }
    expect(missing, missing.join('\n')).toEqual([])
  })
})
