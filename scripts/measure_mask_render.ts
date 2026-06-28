#!/usr/bin/env npx ts-node
/**
 * Wave 38/41 — Mask Render Messung.
 * - Verhaltens-Smoke: mask-render-performance.spec.ts
 * - A/B PoC Legacy vs. Pilot: benchmark_mask_render_ab.ts
 */

import { execSync } from 'node:child_process'

function main(): void {
  console.log('Mask render measurement:')
  console.log('  A/B PoC (Legacy vs. Pilot):')
  console.log('    pnpm benchmark:mask-render-ab')
  console.log('')
  console.log('  Behavioral smoke:')
  console.log('    cd packages/frontend-web && npx playwright test tests/e2e/mask-render-performance.spec.ts')
  console.log('')

  try {
    execSync(
      'pnpm --filter @valero-neuroerp/frontend-web exec vitest --run src/__tests__/render-plan/schema-compiler.test.ts',
      { stdio: 'inherit' },
    )
    console.log('\nCompiler cache test OK (compile-once contract).')
  } catch {
    process.exit(1)
  }
}

main()
