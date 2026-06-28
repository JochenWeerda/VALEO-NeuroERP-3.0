#!/usr/bin/env npx ts-node
/**
 * Wave 38 — misst einfache Render-Marken fuer Mask-Pilot-Routen via Playwright.
 * Nutzung: nach `pnpm --filter @valero-neuroerp/frontend-web build && pnpm preview`
 */

import { execSync } from 'node:child_process'

const DEFAULT_ROUTES = [
  { name: 'crm-pilot', path: '/crm/kunden-stamm-modern/e2e-customer', flag: 'VITE_ENABLE_UNIVERSAL_MASK_CUSTOMER' },
  { name: 'sales-pilot', path: '/sales/order-editor/e2e-order', flag: 'VITE_ENABLE_UNIVERSAL_MASK_SALES_ORDER' },
]

function main(): void {
  console.log('Mask render measurement delegates to Playwright spec:')
  console.log('  packages/frontend-web/tests/e2e/mask-render-performance.spec.ts')
  console.log('')
  console.log('Run:')
  for (const route of DEFAULT_ROUTES) {
    console.log(`  ${route.flag}=true npx playwright test tests/e2e/mask-render-performance.spec.ts -g "${route.name}"`)
  }

  try {
    execSync(
      'pnpm --filter @valero-neuroerp/frontend-web exec vitest --run src/__tests__/render-plan/schema-compiler.test.ts',
      { stdio: 'inherit' },
    )
    console.log('\nCompiler cache test OK (proxy for compile-once contract).')
  } catch {
    process.exit(1)
  }
}

main()
