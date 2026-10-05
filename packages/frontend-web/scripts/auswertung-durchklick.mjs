#!/usr/bin/env node
/**
 * Auswertung des Durchklick-Berichts.
 *
 * Der Rohbericht listet jede Gruppe von Routen, die denselben Fingerabdruck
 * zeigt. Das ist noch kein Fund: `/crm/kunden` und `/crm/customers` sind ein
 * bewusstes Alias-Paar, und dass eine URL unter zwei Schreibweisen erreichbar
 * ist, stoert niemanden.
 *
 * Ein Fund ist es erst, wenn **zwei Eintraege im Menue** auf dieselbe Seite
 * fuehren — dann steht der Anwender vor zwei Wegen, die dasselbe tun, und
 * einer davon ist Ballast.
 *
 * Aufruf:  node scripts/auswertung-durchklick.mjs
 */
import { readFileSync, existsSync } from 'node:fs'
import { resolve } from 'node:path'

const BERICHT = resolve(process.cwd(), 'tests/e2e/durchklick-report.json')
const NAV_ROUTEN = resolve(process.cwd(), 'src/app/routing/navigation-routes.json')

if (!existsSync(BERICHT)) {
  console.error('Kein Bericht. Zuerst:  npx playwright test tests/e2e/navigation-durchklick.spec.ts')
  process.exit(1)
}

const bericht = JSON.parse(readFileSync(BERICHT, 'utf-8'))

/** Pfade, die wirklich im Menue stehen — nur die klickt jemand an. */
const navPfade = new Set(
  JSON.parse(readFileSync(NAV_ROUTEN, 'utf-8')).map((e) => '/' + String(e.path).replace(/^\//, '')),
)

const nurMenue = bericht.doppelgaenger
  .map((gruppe) => ({
    ueberschrift: gruppe.ueberschrift || '(ohne Überschrift)',
    imMenue: gruppe.pfade.filter((p) => navPfade.has(p)),
    weitere: gruppe.pfade.filter((p) => !navPfade.has(p)),
  }))
  .filter((g) => g.imMenue.length > 1)
  .sort((a, b) => b.imMenue.length - a.imMenue.length)

const nurAlias = bericht.doppelgaenger.length - nurMenue.length

console.log(`Durchklick-Auswertung (${bericht.geprueft} Routen, ${bericht.erzeugtAm})`)
console.log('')
console.log('Nach Befund:', JSON.stringify(bericht.nachBefund))
console.log('')

console.log(`Landet im Nichts: ${bericht.landetImNichts.length}`)
for (const e of bericht.landetImNichts) {
  console.log(`   ${e.befund.padEnd(20)} ${e.pfad.padEnd(48)} ${e.details.slice(0, 60)}`)
}
console.log('')

console.log(`Zwei Menüeinträge, eine Seite: ${nurMenue.length}`)
for (const g of nurMenue) {
  console.log(`   [${g.ueberschrift.slice(0, 50)}]`)
  for (const p of g.imMenue) console.log(`        Menü: ${p}`)
  for (const p of g.weitere) console.log(`        (nur URL): ${p}`)
}
console.log('')
console.log(`Weitere ${nurAlias} Gruppen sind reine URL-Aliase — kein Fund.`)
