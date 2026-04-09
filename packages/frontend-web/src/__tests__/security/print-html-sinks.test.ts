import { describe, expect, it } from 'vitest'
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative, resolve } from 'node:path'

const SRC_ROOT = resolve(__dirname, '../..')
const ALLOWED_DOCUMENT_WRITE_FILES = new Set([
  'lib/export-utils.ts',
  'lib/nawaro-communication.ts',
  'lib/services/bon-druck.ts',
  'pages/einkauf/bestellungen-liste.tsx',
])

const DANGEROUS_PATTERNS: Array<{ name: string; regex: RegExp }> = [
  { name: 'document.write', regex: /document\.write\s*\(/g },
  { name: 'innerHTML assignment', regex: /\.innerHTML\s*=/g },
  { name: 'outerHTML assignment', regex: /\.outerHTML\s*=/g },
  { name: 'insertAdjacentHTML', regex: /\.insertAdjacentHTML\s*\(/g },
  { name: 'dangerouslySetInnerHTML', regex: /dangerouslySetInnerHTML/g },
  { name: 'eval', regex: /\beval\s*\(/g },
  { name: 'new Function', regex: /new Function\s*\(/g },
]

function collectSourceFiles(dir: string): string[] {
  const result: string[] = []
  for (const entry of readdirSync(dir)) {
    const fullPath = join(dir, entry)
    const stat = statSync(fullPath)
    if (stat.isDirectory()) {
      if (entry === '__tests__') {
        continue
      }
      result.push(...collectSourceFiles(fullPath))
      continue
    }
    if (/\.(ts|tsx)$/.test(entry)) {
      result.push(fullPath)
    }
  }
  return result
}

describe('frontend html sink inventory', () => {
  it('allows document.write only in the hardened print paths', () => {
    const hits = collectSourceFiles(SRC_ROOT)
      .map((filePath) => {
        const content = readFileSync(filePath, 'utf-8')
        if (!DANGEROUS_PATTERNS[0].regex.test(content)) {
          return null
        }
        DANGEROUS_PATTERNS[0].regex.lastIndex = 0
        return relative(SRC_ROOT, filePath).replace(/\\/g, '/')
      })
      .filter((value): value is string => Boolean(value))
      .sort()

    expect(hits).toEqual([...ALLOWED_DOCUMENT_WRITE_FILES].sort())
  })

  it('finds no new raw html sink patterns in frontend source', () => {
    const findings: string[] = []
    for (const filePath of collectSourceFiles(SRC_ROOT)) {
      const relativePath = relative(SRC_ROOT, filePath).replace(/\\/g, '/')
      const content = readFileSync(filePath, 'utf-8')
      for (const pattern of DANGEROUS_PATTERNS) {
        pattern.regex.lastIndex = 0
        if (!pattern.regex.test(content)) {
          continue
        }
        if (pattern.name === 'document.write' && ALLOWED_DOCUMENT_WRITE_FILES.has(relativePath)) {
          continue
        }
        findings.push(`${pattern.name}: ${relativePath}`)
      }
    }

    expect(findings).toEqual([])
  })
})
