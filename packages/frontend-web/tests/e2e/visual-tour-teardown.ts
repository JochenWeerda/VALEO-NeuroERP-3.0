/**
 * Playwright globalTeardown — aggregiert alle per-Test Issues-Dateien
 * zu einer einzigen issues.json nach Abschluss aller Worker.
 */
import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const SCREENSHOT_DIR = path.join(__dirname, '../../visual-tour-results')
const RAW_DIR = path.join(SCREENSHOT_DIR, 'issues-raw')

export default async function globalTeardown() {
  if (!fs.existsSync(RAW_DIR)) {
    console.log('\n📋 Visual Tour: Keine Issues-Dateien gefunden.')
    return
  }

  const files = fs.readdirSync(RAW_DIR).filter((f) => f.endsWith('.json'))
  const allIssues: Array<{ route: string; viewport: string; type: string; detail: string }> = []

  for (const file of files) {
    try {
      const content = fs.readFileSync(path.join(RAW_DIR, file), 'utf-8')
      const parsed = JSON.parse(content)
      if (Array.isArray(parsed)) allIssues.push(...parsed)
    } catch {
      // ignore malformed files
    }
  }

  // Sort by type, then viewport, then route
  allIssues.sort((a, b) =>
    a.type.localeCompare(b.type) || a.viewport.localeCompare(b.viewport) || a.route.localeCompare(b.route),
  )

  const byType = allIssues.reduce<Record<string, number>>((acc, i) => {
    acc[i.type] = (acc[i.type] ?? 0) + 1
    return acc
  }, {})

  const byRoute = allIssues.reduce<Record<string, number>>((acc, i) => {
    acc[i.route] = (acc[i.route] ?? 0) + 1
    return acc
  }, {})

  const report = {
    timestamp: new Date().toISOString(),
    total_issues: allIssues.length,
    by_type: byType,
    top_routes: Object.entries(byRoute)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 20)
      .map(([route, count]) => ({ route, count })),
    issues: allIssues,
  }

  fs.writeFileSync(path.join(SCREENSHOT_DIR, 'issues.json'), JSON.stringify(report, null, 2))

  console.log(`\n📋 Visual Tour abgeschlossen: ${allIssues.length} Probleme gefunden`)
  if (allIssues.length > 0) {
    console.log('   Nach Typ:')
    Object.entries(byType).forEach(([t, n]) => console.log(`     [${t}] ${n}×`))
    console.log('   Top-Seiten:')
    report.top_routes.slice(0, 10).forEach(({ route, count }) =>
      console.log(`     ${route}: ${count} Problem(e)`),
    )
    console.log(`\n   Details: ${path.join(SCREENSHOT_DIR, 'issues.json')}`)
  } else {
    console.log('   ✅ Keine Darstellungsprobleme gefunden.')
  }
}
