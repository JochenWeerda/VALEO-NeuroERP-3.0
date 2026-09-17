#!/usr/bin/env node
/**
 * Führt den Durchklick in Teilen aus und fügt die Teilberichte zusammen.
 *
 * Achthundert Routen in einem Playwright-Prozess sprengen den Arbeitsspeicher:
 * Der Browser-Kontext wächst mit jeder Navigation, und der Lauf wird vom System
 * abgeräumt, bevor er fertig ist. Jeder Teil ist deshalb ein eigener Prozess,
 * der seinen Speicher beim Beenden wieder freigibt.
 *
 * Aufruf:  node scripts/durchklick-lauf.mjs [Anzahl Teile]
 */
import { execFileSync } from 'node:child_process'
import { readFileSync, writeFileSync, existsSync, rmSync, mkdirSync } from 'node:fs'
import { resolve } from 'node:path'

const teile = Number.parseInt(process.argv[2] ?? '12', 10)
const zwischen = resolve(process.cwd(), 'tests/e2e/.durchklick-teile')
/**
 * Fortsetzbar: Ein fertiger Teilbericht wird nicht neu gefahren.
 *
 * Auf einer Maschine, auf der noch eine WSL-VM und ein zweiter Editor laufen,
 * wird ein langer Lauf vom System abgeraeumt, bevor er durch ist. Dann genuegt
 * ein erneuter Aufruf, statt von vorn zu beginnen. `--neu` erzwingt den
 * vollstaendigen Durchlauf.
 */
if (process.argv.includes('--neu')) {
  rmSync(zwischen, { recursive: true, force: true })
}
mkdirSync(zwischen, { recursive: true })

const alle = []
for (let i = 1; i <= teile; i++) {
  const ausgabe = `tests/e2e/.durchklick-teile/teil-${i}.json`
  const schonDa = resolve(process.cwd(), ausgabe)
  if (existsSync(schonDa)) {
    alle.push(...JSON.parse(readFileSync(schonDa, 'utf-8')).alle)
    process.stdout.write(`Teil ${i}/${teile} liegt vor — übersprungen.\n`)
    continue
  }
  process.stdout.write(`\nTeil ${i}/${teile} ...\n`)
  try {
    execFileSync(
      'npx',
      ['playwright', 'test', 'tests/e2e/navigation-durchklick.spec.ts',
       '--project=chromium', '--workers=1', '--grep', 'Routen', '--reporter=line'],
      {
        stdio: 'inherit',
        shell: true,
        env: { ...process.env, DURCHKLICK_TEIL: `${i}/${teile}`, DURCHKLICK_AUSGABE: ausgabe },
      },
    )
  } catch {
    process.stdout.write(`   Teil ${i} vorzeitig beendet — der Teilbericht wird trotzdem gelesen.\n`)
  }
  const pfad = resolve(process.cwd(), ausgabe)
  if (existsSync(pfad)) {
    alle.push(...JSON.parse(readFileSync(pfad, 'utf-8')).alle)
  }
}

// Zusammenfügen — dieselbe Auswertung wie im Einzellauf.
const nachFingerabdruck = new Map()
for (const e of alle) {
  if (e.befund !== 'OK') continue
  const liste = nachFingerabdruck.get(e.fingerabdruck) ?? []
  liste.push(e.pfad)
  nachFingerabdruck.set(e.fingerabdruck, liste)
}
const doppelgaenger = [...nachFingerabdruck.entries()]
  .filter(([, pfade]) => pfade.length > 1)
  .map(([abdruck, pfade]) => ({ ueberschrift: abdruck.split('||')[0], pfade: pfade.sort() }))
  .sort((a, b) => b.pfade.length - a.pfade.length)
const nachBefund = alle.reduce((acc, e) => ({ ...acc, [e.befund]: (acc[e.befund] ?? 0) + 1 }), {})

writeFileSync(
  resolve(process.cwd(), 'tests/e2e/durchklick-report.json'),
  JSON.stringify(
    {
      erzeugtAm: new Date().toISOString(),
      geprueft: alle.length,
      nachBefund,
      landetImNichts: alle.filter((e) => e.befund !== 'OK').sort((a, b) => a.pfad.localeCompare(b.pfad)),
      doppelgaenger,
      alle,
    },
    null,
    2,
  ),
  'utf-8',
)
console.log(`\nZusammengefügt: ${alle.length} Routen, ${JSON.stringify(nachBefund)}`)
