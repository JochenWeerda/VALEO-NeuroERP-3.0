#!/usr/bin/env node
const { execFileSync } = require('node:child_process')
const path = require('node:path')

const repoRoot = process.cwd()

function run(command, args) {
  const executable = process.platform === 'win32' && command === 'npx' ? 'npx.cmd' : command
  execFileSync(executable, args, {
    cwd: repoRoot,
    stdio: 'inherit',
    shell: process.platform === 'win32',
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

const scriptLikeFiles = stagedFiles.filter((file) => /\.(ts|tsx|js|jsx)$/i.test(file))
const markdownFiles = stagedFiles.filter((file) => /\.md$/i.test(file))

if (scriptLikeFiles.length > 0) {
  run('npx', ['eslint', '--fix', ...scriptLikeFiles])
  run('npx', ['eslint', ...scriptLikeFiles])
}

if (markdownFiles.length > 0) {
  const docsMarkdownCheck = path.join('scripts', 'docs-markdown-check.cjs')
  const docsGovernanceCheck = path.join('scripts', 'docs-governance-check.cjs')
  run('node', [docsMarkdownCheck, ...markdownFiles])
  run('node', [docsGovernanceCheck, ...markdownFiles])
}

console.log(`Staged checks passed for ${stagedFiles.length} file(s).`)
