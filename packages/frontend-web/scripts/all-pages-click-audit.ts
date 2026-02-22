import fs from 'node:fs'
import path from 'node:path'
import { chromium } from 'playwright'

type PageAuditResult = {
  route: string
  ok: boolean
  title: string
  error?: string
}

const BASE_URL = process.env.AUDIT_BASE_URL ?? 'http://localhost:3000'
const ROOT = path.resolve(process.cwd(), 'src/pages')
const OUTPUT_DIR = path.resolve(process.cwd(), 'artifacts')
const OUTPUT_MD = path.join(OUTPUT_DIR, 'all-pages-click-audit.md')
const OUTPUT_JSON = path.join(OUTPUT_DIR, 'all-pages-click-audit.json')

const pageFiles = walkFiles(ROOT)
  .filter((entry) => entry.endsWith('.tsx'))
  .sort((a, b) => a.localeCompare(b))

const routes = pageFiles.map(fileToRoute)
const browser = await chromium.launch({ headless: true })
const page = await browser.newPage()

const results: PageAuditResult[] = []

for (const route of routes) {
  const target = `${BASE_URL}${route}`
  try {
    await page.goto(target, { waitUntil: 'domcontentloaded', timeout: 25000 })
    await page.waitForTimeout(120)
    results.push({ route, ok: true, title: await page.title() })
  } catch (error) {
    results.push({ route, ok: false, title: '', error: String(error) })
  }
}

await browser.close()

const failed = results.filter((entry) => !entry.ok)
const markdown: string[] = []
markdown.push('# All Pages Click Audit')
markdown.push('')
markdown.push(`Base URL: ${BASE_URL}`)
markdown.push(`Pages checked: ${results.length}`)
markdown.push(`Failed: ${failed.length}`)
markdown.push('')
markdown.push('## Results')
markdown.push('')
for (const entry of results) {
  markdown.push(`- ${entry.ok ? 'OK' : 'FAIL'} \`${entry.route}\` ${entry.ok ? '' : `| ${entry.error}`}`)
}

fs.mkdirSync(OUTPUT_DIR, { recursive: true })
fs.writeFileSync(OUTPUT_MD, `${markdown.join('\n')}\n`, 'utf8')
fs.writeFileSync(OUTPUT_JSON, JSON.stringify({ baseUrl: BASE_URL, results }, null, 2), 'utf8')

console.log(`All-pages click audit written:`)
console.log(`- ${OUTPUT_MD}`)
console.log(`- ${OUTPUT_JSON}`)

function fileToRoute(file: string): string {
  const rel = path.relative(ROOT, file).replaceAll('\\', '/').replace(/\.tsx$/, '')
  if (rel === 'index') {
    return '/'
  }
  if (rel.startsWith('portal/')) {
    const portalRel = rel.replace(/^portal\//, '')
    if (portalRel === 'index') {
      return '/portal'
    }
    return `/portal/${portalRel}`
  }
  if (rel.endsWith('/index')) {
    return `/${rel.slice(0, -('/index'.length))}`
  }
  return `/${rel}`
}

function walkFiles(root: string): string[] {
  const files: string[] = []
  const stack = [root]

  while (stack.length > 0) {
    const current = stack.pop()
    if (!current) {
      continue
    }
    const stat = fs.statSync(current)
    if (stat.isDirectory()) {
      for (const entry of fs.readdirSync(current)) {
        stack.push(path.join(current, entry))
      }
    } else if (stat.isFile()) {
      files.push(current)
    }
  }

  return files
}
