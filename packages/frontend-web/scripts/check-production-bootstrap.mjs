import { chromium } from '@playwright/test'
import { existsSync } from 'node:fs'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const base = new URL(process.env.VALEO_BASE_URL || 'http://127.0.0.1:4173')
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..')
const output = path.join(root, 'playwright-tests/artifacts/production-bootstrap')
await mkdir(output, { recursive: true })
const browser = await chromium.launch({
  headless: true,
  ...(existsSync(chromium.executablePath()) ? {} : { channel: 'chrome' }),
})
const errors = []
let failure
let result
try {
  const page = await browser.newPage({ viewport: { width: 1366, height: 768 } })
  page.on('pageerror', (error) => errors.push(error.message))
  // Test compiled application initialization, never an identity provider or business data.
  await page.route('**/*', (route) => {
    const target = new URL(route.request().url())
    if (target.origin !== base.origin) return route.abort()
    if (target.pathname.startsWith('/api/')) {
      return route.fulfill({ status: 401, contentType: 'application/json', body: '{"detail":"Authentication required"}' })
    }
    return route.continue()
  })
  try {
    await page.goto(new URL('/login', base).href, { waitUntil: 'domcontentloaded' })
    const login = page.getByRole('button', { name: 'Mit SSO anmelden', exact: true })
    await login.waitFor({ state: 'visible', timeout: 15000 })
    if (!(await login.isEnabled())) throw new Error('Production login remains disabled')
    if (errors.length) throw new Error('Production application raised a page error')
  } catch (error) {
    failure = error
  }
  result = { passed: !failure, pathname: new URL(page.url()).pathname, pageErrors: errors }
  await page.screenshot({ path: path.join(output, 'login.png'), fullPage: true })
  await writeFile(path.join(output, 'result.json'), JSON.stringify(result, null, 2) + '\n')
} finally {
  await browser.close()
}
console.log(JSON.stringify(result))
if (failure) throw failure
