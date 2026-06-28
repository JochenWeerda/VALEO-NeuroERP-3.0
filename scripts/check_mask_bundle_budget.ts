#!/usr/bin/env npx ts-node
/**
 * Wave 37 — prueft Bundle-Budgets fuer Mask-Pilot-Routen nach Production-Build.
 */

import { createGzip } from 'node:zlib'
import { readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'
import { pipeline } from 'node:stream/promises'
import { Readable } from 'node:stream'

const DIST_DIR = join(process.cwd(), 'packages', 'frontend-web', 'dist', 'assets', 'js')

const BUDGETS_KB = {
  largestAsyncChunk: 512,
  totalJs: 4096,
}

async function gzipSizeKb(filePath: string): Promise<number> {
  const content = readFileSync(filePath)
  const gzip = createGzip()
  const chunks: Buffer[] = []
  gzip.on('data', (chunk) => chunks.push(chunk as Buffer))
  await pipeline(Readable.from(content), gzip)
  return Buffer.concat(chunks).length / 1024
}

function listJsFiles(): string[] {
  try {
    return readdirSync(DIST_DIR)
      .filter((name) => name.endsWith('.js'))
      .map((name) => join(DIST_DIR, name))
  } catch {
    return []
  }
}

async function main(): Promise<void> {
  const files = listJsFiles()
  if (files.length === 0) {
    console.warn('Mask bundle budget check skipped: no dist assets found (run frontend build first).')
    return
  }

  const sizes = await Promise.all(
    files.map(async (file) => ({
      file,
      kb: await gzipSizeKb(file),
    })),
  )

  const totalKb = sizes.reduce((sum, entry) => sum + entry.kb, 0)
  const largest = sizes.reduce((max, entry) => (entry.kb > max.kb ? entry : max), sizes[0])
  const violations: string[] = []

  if (largest.kb > BUDGETS_KB.largestAsyncChunk) {
    violations.push(
      `Largest chunk ${largest.file} (${largest.kb.toFixed(1)} KB gzip) exceeds ${BUDGETS_KB.largestAsyncChunk} KB`,
    )
  }
  if (totalKb > BUDGETS_KB.totalJs) {
    violations.push(`Total JS ${totalKb.toFixed(1)} KB gzip exceeds ${BUDGETS_KB.totalJs} KB`)
  }

  if (violations.length > 0) {
    console.error('Mask bundle budget violations:')
    for (const violation of violations) {
      console.error(`- ${violation}`)
    }
    process.exit(1)
  }

  console.log(
    `Mask bundle budget OK (total ${totalKb.toFixed(1)} KB gzip, largest ${largest.kb.toFixed(1)} KB).`,
  )
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
