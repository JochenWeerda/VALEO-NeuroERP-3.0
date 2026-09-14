#!/usr/bin/env node
// Prueft eine einzelne Datei gegen die mechanisch pruefbaren Design-Invarianten
// aus CLAUDE.md. Meldet Befunde als Warnung (Exit 0) - es gibt Altbestand,
// der in eigenen Slices abgebaut wird (axe text-green-600-Sweep, networkidle).
// Aufruf: node scripts/check-design-invariants.mjs <datei>
import { readFileSync } from 'node:fs'

const RULES = [
  {
    test: /\b(?:text|bg|border)-(?:red|green|blue|yellow|amber|orange|emerald|rose|lime|sky|teal)-[0-9]{2,3}\b/,
    applies: (f) => /\.tsx?$/.test(f),
    msg: 'Rohe Palette-Klasse. Semantische Farben nur ueber Badge/Button-Variants oder text-status-success|warning|error|info (WCAG AA).',
  },
  {
    test: /text-\[10px\]/,
    applies: (f) => /\.tsx?$/.test(f),
    msg: 'Arbitrary-Wert text-[10px]. Micro-Labels: text-2xs tracking-wide uppercase.',
  },
  {
    test: /#[0-9a-fA-F]{6}\b/,
    applies: (f) => f.includes('/components/charts/') && !f.endsWith('chart-palette.ts'),
    msg: 'Roher Hex-Wert im Chart-Code. Farben nur aus components/charts/chart-palette.ts.',
  },
  {
    test: /networkidle/,
    applies: (f) => /[\/]tests[\/]/.test(f),
    msg: 'networkidle gehoert nicht in Specs. Stattdessen waitForAppReady() aus helpers/ui.ts.',
  },
]

const file = process.argv[2]
if (!file) process.exit(0)

let src
try {
  src = readFileSync(file, 'utf8')
} catch {
  process.exit(0) // geloescht oder unlesbar: kein Befund, nicht blockieren
}

const findings = []
for (const rule of RULES) {
  if (!rule.applies(file)) continue
  src.split('\n').forEach((line, i) => {
    if (rule.test.test(line)) findings.push(`  ${file}:${i + 1}  ${rule.msg}`)
  })
}

if (findings.length > 0) {
  const shown = findings.slice(0, 10)
  const more = findings.length - shown.length
  console.log(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: 'PostToolUse',
        additionalContext:
          `Design-Invarianten (CLAUDE.md) - ${findings.length} Befund(e):\n` +
          shown.join('\n') +
          (more > 0 ? `\n  ... und ${more} weitere` : '') +
          '\nAltbestand nicht pauschal mitfixen; neue Verstoesse aber vermeiden.',
      },
      suppressOutput: true,
    }),
  )
}
process.exit(0)
