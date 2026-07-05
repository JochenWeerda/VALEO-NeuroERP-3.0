#!/usr/bin/env node
const { execFileSync } = require('node:child_process')
const path = require('node:path')

const repoRoot = process.cwd()
const eslintBin = path.join(path.dirname(require.resolve('eslint/package.json')), 'bin', 'eslint.js')

function run(command, args) {
  execFileSync(command, args, {
    cwd: repoRoot,
    stdio: 'inherit',
    shell: false,
  })
}

function getStagedFiles() {
  const output = execFileSync(
    'git',
    ['diff', '--cached', '--name-only', '--diff-filter=ACMR'],
    { cwd: repoRoot, encoding: 'utf8', shell: false },
  )

  return output
    .split(/\r?\n/)
    .map((entry) => entry.trim())
    .filter(Boolean)
}

const stagedFiles = getStagedFiles()

if (stagedFiles.length === 0) {
  console.log('No staged files to validate.')
  process.exit(0)
}

// PII-/Lead-Daten-Guard (DSGVO): blockiert Personen-/GAP-Lead-Daten vor dem Commit.
// python/python3-Fallback; wenn kein Interpreter gefunden wird, warnen (CI ist Backstop).
;(function runPiiGuard() {
  const guard = path.join('scripts', 'check_no_pii_data.py')
  for (const py of ['python', 'python3']) {
    try {
      execFileSync(py, [guard, '--staged'], { cwd: repoRoot, stdio: 'inherit', shell: false })
      return
    } catch (err) {
      if (err && err.code === 'ENOENT') continue // Interpreter nicht gefunden -> naechsten versuchen
      process.exit(err.status || 1) // Guard hat blockiert (PII gefunden)
    }
  }
  console.warn('WARN: kein python/python3 fuer PII-Guard gefunden — CI-Gate greift stattdessen.')
})()

const scriptLikeFiles = stagedFiles.filter(
  (file) =>
    /\.(ts|tsx|js|jsx)$/i.test(file) &&
    !/\.(spec|test)\.(ts|tsx|js|jsx)$/i.test(file) &&
    !/\/vite\.config(?:\.performance)?\.ts$/i.test(file),
)
const markdownFiles = stagedFiles.filter((file) => /\.md$/i.test(file))

if (scriptLikeFiles.length > 0) {
  run(process.execPath, [eslintBin, '--fix', ...scriptLikeFiles])
  run(process.execPath, [eslintBin, ...scriptLikeFiles])
}

if (markdownFiles.length > 0) {
  const docsMarkdownCheck = path.join('scripts', 'docs-markdown-check.cjs')
  const docsGovernanceCheck = path.join('scripts', 'docs-governance-check.cjs')
  run('node', [docsMarkdownCheck, ...markdownFiles])
  run('node', [docsGovernanceCheck, ...markdownFiles])
}

console.log(`Staged checks passed for ${stagedFiles.length} file(s).`)
