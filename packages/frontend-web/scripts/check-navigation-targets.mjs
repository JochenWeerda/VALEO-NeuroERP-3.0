#!/usr/bin/env node
import { readFileSync, readdirSync, statSync } from 'node:fs'
import { join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))
const root = join(__dirname, '..')
const sourceRoot = join(root, 'src')
const inventory = JSON.parse(
  readFileSync(join(sourceRoot, 'app', 'routing', 'route-inventory.gen.json'), 'utf8'),
)

const routeMatchers = inventory.routes.map(({ path }) => {
  const normalized = `/${path}`.replace(/\/+$/, '') || '/'
  const source = normalized
    .replace(/[.+?^${}()|[\]\\]/g, '\\$&')
    .replace(/:([A-Za-z0-9_]+)/g, '[^/?#]+')
    .replace(/\/\$\/?$/, '(?:/.*)?')
  return new RegExp(`^${source}/?$`)
})

const targetPatterns = [
  { regex: /\bnavigate\(\s*(['"])(\/[^'"\n]*)\1/g, targetGroup: 2 },
  { regex: /\bnavigate\(\s*`(\/[^`\n]+)`/g, targetGroup: 1 },
  { regex: /\bto\s*=\s*(['"])(\/[^'"\n]*)\1/g, targetGroup: 2 },
  { regex: /\bto\s*=\s*\{\s*(['"])(\/[^'"\n]*)\1\s*\}/g, targetGroup: 2 },
  { regex: /\bto\s*=\s*\{\s*`(\/[^`\n]+)`\s*\}/g, targetGroup: 1 },
]

const issues = []
for (const file of walk(sourceRoot)) {
  if (!/\.(?:ts|tsx)$/.test(file) || file.endsWith('route-tree.gen.tsx')) continue
  const text = readFileSync(file, 'utf8')
  for (const { regex, targetGroup } of targetPatterns) {
    for (const match of text.matchAll(regex)) {
      const rawTarget = match[targetGroup]
      if (rawTarget.includes('${') && !rawTarget.includes('}')) continue
      const pathname =
        rawTarget
          .replace(/\$\{(?:[A-Za-z0-9_]*Query|q)\}$/i, '')
          .replace(/\$\{[^}]+\}/g, '__value__')
          .split(/[?#]/, 1)[0]
          .replace(/\/+$/, '') || '/'
      if (routeMatchers.some((matcher) => matcher.test(pathname))) continue
      const line = text.slice(0, match.index).split('\n').length
      issues.push({
        file: relative(root, file).replaceAll('\\', '/'),
        line,
        target: rawTarget,
      })
    }
  }
}

if (issues.length > 0) {
  console.error(`Navigation target check failed with ${issues.length} issue(s):`)
  for (const issue of issues) {
    console.error(`- ${issue.file}:${issue.line} -> ${issue.target}`)
  }
  process.exit(1)
}

console.log(`Navigation target check passed (${routeMatchers.length} route patterns).`)

function walk(directory) {
  const files = []
  for (const entry of readdirSync(directory)) {
    const file = join(directory, entry)
    if (statSync(file).isDirectory()) files.push(...walk(file))
    else files.push(file)
  }
  return files
}
