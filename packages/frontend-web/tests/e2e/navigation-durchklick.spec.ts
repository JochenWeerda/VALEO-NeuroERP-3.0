/**
 * DURCHKLICK: jeder Menüeintrag, vor und zurück
 *
 * Der All-Routes-Smoke prüft, ob eine Route *antwortet*. Dieser Test prüft
 * zwei Dinge, die dabei durchrutschen:
 *
 * 1. **Landet der Eintrag im Nichts?** Eine Route kann 200 liefern und
 *    trotzdem nichts zeigen — eine leere Hülle, ein Platzhalter, ein
 *    Fehlerzustand. Gemessen wird, was tatsächlich im Hauptbereich steht.
 *
 * 2. **Führen zwei Einträge auf dieselbe Seite?** Genau das ist bei
 *    „Kundenportal" und „KIM – Kunde im Mittelpunkt" berichtet worden. Dafür
 *    bekommt jede Route einen Fingerabdruck aus Überschrift und Textanfang;
 *    zwei verschiedene Ziele mit demselben Fingerabdruck sind ein Fund.
 *
 * Dazu die Rückwärtsnavigation: Wer vor und zurück geht, muss dort landen,
 * wo er war — nicht auf der Startseite und nicht auf einer leeren Seite.
 *
 * Ausführung:
 *   npx playwright test tests/e2e/navigation-durchklick.spec.ts
 *
 * Der Bericht liegt danach in tests/e2e/durchklick-report.json.
 */
import { test, expect, type Page } from '@playwright/test'
import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { resolve } from 'node:path'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Befund =
  | 'OK'
  | 'LEER'
  | 'FEHLER'
  | 'NICHT_GEFUNDEN'
  | 'ZEITUEBERSCHREITUNG'

interface Ergebnis {
  pfad: string
  quelle: string
  befund: Befund
  ueberschrift: string
  fingerabdruck: string
  details: string
  dauerMs: number
}

const ROUTES_FILE = resolve(process.cwd(), 'tests/e2e/.generated-routes.json')
if (!existsSync(ROUTES_FILE)) {
  throw new Error(
    'Routenmanifest fehlt. Zuerst ausführen:\n  node scripts/harvest-routes.mjs',
  )
}

const manifest = JSON.parse(readFileSync(ROUTES_FILE, 'utf-8'))

/**
 * Das Kundenportal fehlt im Manifest — `scripts/harvest-routes.mjs` ueberspringt
 * `/portal/` bewusst, wie Login und Fehlerseiten. Fuer einen Smoke mag das
 * richtig sein; fuer den Durchklick nicht: Das Portal ist eine ganze
 * Oberflaeche, die ein Kunde benutzt, und wenn dort etwas im Nichts landet,
 * sieht es sonst niemand. Die Pfade kommen aus dem generierten Routenbaum.
 */
function portalRouten(): Array<{ path: string; source: string }> {
  const baum = resolve(process.cwd(), 'src/app/routing/route-tree.gen.tsx')
  if (!existsSync(baum)) return []
  const inhalt = readFileSync(baum, 'utf-8')
  const treffer = [...inhalt.matchAll(/"legacyPath":"(\/portal[^"]*)"/g)].map((m) => m[1])
  const eindeutig = [...new Set(treffer)].filter((p) => !p.includes('$') && !p.includes(':'))
  return eindeutig.sort().map((path) => ({ path, source: 'portal' }))
}

const alleRouten: Array<{ path: string; source: string }> = [
  ...manifest.routes,
  ...portalRouten(),
]

/** Nur eine Teilmenge prüfen, z.B. DURCHKLICK_FILTER=portal,crm */
const filter = (process.env.DURCHKLICK_FILTER ?? '')
  .split(',')
  .map((t) => t.trim())
  .filter(Boolean)

const gefiltert = filter.length
  ? alleRouten.filter((r) => filter.some((t) => r.path.includes(t)))
  : alleRouten

/**
 * In Teilen laufen: DURCHKLICK_TEIL=3/10 nimmt das dritte von zehn Stuecken.
 *
 * Acht­hundert Routen in einem Prozess sprengen den Arbeitsspeicher — der
 * Browser-Kontext waechst mit jeder Navigation. Jeder Teil laeuft als eigener
 * Prozess, gibt danach alles frei, und `scripts/durchklick-lauf.mjs` fuegt die
 * Teilberichte zusammen.
 */
const teilAngabe = process.env.DURCHKLICK_TEIL ?? ''
const [teilNr, teilGesamt] = teilAngabe.includes('/')
  ? teilAngabe.split('/').map((n) => Number.parseInt(n, 10))
  : [1, 1]

const stueckGroesse = Math.ceil(gefiltert.length / teilGesamt)
const routen =
  teilGesamt > 1
    ? gefiltert.slice((teilNr - 1) * stueckGroesse, teilNr * stueckGroesse)
    : gefiltert

const AUSGABE = process.env.DURCHKLICK_AUSGABE ?? 'tests/e2e/durchklick-report.json'

const ergebnisse: Ergebnis[] = []

/**
 * Wartet, bis der Hauptbereich Inhalt zeigt — oder bis die Geduld zu Ende ist.
 * Gibt in beiden Fällen zurück, was dasteht; ein leeres Ergebnis nach vollem
 * Warten ist dann wirklich eine leere Seite.
 */
async function inhaltAbwarten(
  page: Page,
  timeout = 8_000,
): Promise<{ ueberschrift: string; text: string }> {
  const ende = Date.now() + timeout
  let letzte = await lesen(page)
  while (Date.now() < ende && letzte.text.length < 40) {
    await page.waitForTimeout(300)
    letzte = await lesen(page)
  }
  return letzte
}

/**
 * Wartet, bis die Seite eine Überschrift hat — manche Masken (KIM) laden erst
 * ihre Liste und setzen die Überschrift danach. Wer vorher misst, vergleicht
 * einen leeren String mit dem späteren Ergebnis und hält den Unterschied für
 * einen Navigationsfehler. Bleibt sie leer, ist das auch eine Auskunft.
 */
async function ueberschriftAbwarten(page: Page, timeout = 8_000): Promise<string> {
  const ende = Date.now() + timeout
  let letzte = ''
  while (Date.now() < ende) {
    letzte = (await lesen(page)).ueberschrift
    if (letzte) return letzte
    await page.waitForTimeout(250)
  }
  return letzte
}

/** Was steht wirklich auf der Seite? */
async function lesen(page: Page): Promise<{ ueberschrift: string; text: string }> {
  return page.evaluate(() => {
    const haupt =
      document.querySelector('main') ??
      document.querySelector('[role="main"]') ??
      document.body
    const h1 = haupt.querySelector('h1')
    const text = (haupt.textContent ?? '').replace(/\s+/g, ' ').trim()
    return { ueberschrift: (h1?.textContent ?? '').trim(), text }
  })
}

/**
 * Der Fingerabdruck ist bewusst grob: Überschrift plus die ersten 300 Zeichen
 * des Hauptbereichs. Zwei Masken mit identischem Anfang sind entweder
 * dieselbe Seite oder so ähnlich, dass der Unterschied niemandem auffällt —
 * beides ist ein Fund.
 */
function fingerabdruck(ueberschrift: string, text: string): string {
  return `${ueberschrift}||${text.slice(0, 300)}`
}

/**
 * Muster fuer „hier steht nichts Brauchbares".
 *
 * Ein blosses /404/ war zu gierig: Es trifft jede Belegnummer, die die Ziffern
 * enthaelt — die Buchungserfassung wurde so als Fehlerseite gemeldet, obwohl
 * sie einwandfrei rendert. Gesucht wird deshalb die 404 als eigenstaendige
 * Zahl in Fehlerkontext, nicht als Zeichenfolge irgendwo im Text.
 *
 * `noch nicht implementiert` bleibt drin, meint aber oft einen ehrlichen
 * Leerzustand („der Endpunkt fehlt noch") statt einer kaputten Seite — der
 * Fund gehoert dann ins Backend, nicht ins Frontend.
 */
const LEER_MUSTER = [
  /seite nicht gefunden/i,
  // Ohne Wortgrenze: `textContent` klebt Nachbarn zusammen, aus
  // „Produktion" + „Not Found" wird „ProduktionNot Found" — mit  faellt
  // genau die kaputte Seite durch, die gefunden werden soll.
  /not\s*found/i,
  /404\s*[—:-]?\s*(seite|page|not found|nicht gefunden)/i,
  /etwas ist schiefgelaufen/i,
  /ein fehler ist aufgetreten/i,
  /noch nicht implementiert/i,
  /coming soon/i,
]

/**
 * Ein Test, eine Schleife, ein Browser-Kontext.
 *
 * Zuerst stand hier ein Test **je Route**. Bei 786 Routen legt Playwright 786
 * Kontexte an und haelt Video- und Trace-Artefakte je Test vor — der Durchlauf
 * starb am Arbeitsspeicher. Eine Schleife in einem Test braucht einen Kontext
 * und schreibt den Bericht zwischendurch mit, damit ein Abbruch nicht alles
 * verliert.
 */
// Video, Screenshot und Trace aus: Bei mehreren hundert Routen sind sie der
// Grund, warum der Durchlauf am Arbeitsspeicher stirbt, nicht die Routen.
test.use({ video: 'off', screenshot: 'off', trace: 'off' })

test.describe('Durchklick durch alle Routen', () => {
  test(`${routen.length} Routen`, async ({ page }) => {
    test.setTimeout(routen.length * 12_000 + 120_000)

    for (const [nr, route] of routen.entries()) {
      const start = Date.now()
      let befund: Befund = 'OK'
      let details = ''
      let ueberschrift = ''
      let text = ''

      try {
        const antwort = await page.goto(route.path, {
          waitUntil: 'domcontentloaded',
          timeout: 20_000,
        })
        if (antwort && antwort.status() >= 400) {
          befund = 'NICHT_GEFUNDEN'
          details = `HTTP ${antwort.status()}`
        }
        // Vite/React lazy: erst ein PageLoader ganz ohne `main`, das `main`
        // erscheint nach drei bis fuenf Sekunden. Wer frueher misst, haelt
        // jede Seite fuer leer — das ist kein Befund, sondern ein Messfehler.
        await waitForDashboardShell(page, 15_000)
        // Nicht eine feste Zeit abwarten, sondern auf Inhalt: Manche Seiten
        // (Portal-Rationswerkbank) laden ihren Hauptteil erst per Suspense
        // nach. Wer nach 400 ms misst, meldet sie als leer — das waere ein
        // Messfehler, kein Fund.
        const gelesen = await inhaltAbwarten(page)
        ueberschrift = gelesen.ueberschrift
        text = gelesen.text

        if (befund === 'OK') {
          if (text.length < 40) {
            befund = 'LEER'
            details = `nur ${text.length} Zeichen im Hauptbereich`
          } else {
            const treffer = LEER_MUSTER.find((m) => m.test(text.slice(0, 400)))
            if (treffer) {
              befund = text.match(/404|nicht gefunden|not found/i) ? 'NICHT_GEFUNDEN' : 'FEHLER'
              details = `Text passt auf ${treffer}`
            }
          }
        }
      } catch (fehler) {
        befund = /timeout/i.test(String(fehler)) ? 'ZEITUEBERSCHREITUNG' : 'FEHLER'
        details = String(fehler).slice(0, 200)
      }

      ergebnisse.push({
        pfad: route.path,
        quelle: route.source,
        befund,
        ueberschrift,
        fingerabdruck: fingerabdruck(ueberschrift, text),
        details,
        dauerMs: Date.now() - start,
      })

      if (befund !== 'OK') {
        console.log(`  ${befund.padEnd(20)} ${route.path}  ${details.slice(0, 60)}`)
      }
      // Alle 25 Routen mitschreiben — ein Abbruch verliert dann hoechstens 25.
      if ((nr + 1) % 25 === 0) {
        berichtSchreiben()
        console.log(`  ... ${nr + 1}/${routen.length}`)
      }
    }

    berichtSchreiben()
  })
})

/** Der Bericht, jederzeit schreibbar. */
function berichtSchreiben(): void {
  const nachFingerabdruck = new Map<string, string[]>()
  for (const e of ergebnisse) {
    if (e.befund !== 'OK') continue
    const liste = nachFingerabdruck.get(e.fingerabdruck) ?? []
    liste.push(e.pfad)
    nachFingerabdruck.set(e.fingerabdruck, liste)
  }

  const doppelgaenger = [...nachFingerabdruck.entries()]
    .filter(([, pfade]) => pfade.length > 1)
    .map(([abdruck, pfade]) => ({
      ueberschrift: abdruck.split('||')[0],
      pfade: pfade.sort(),
    }))
    .sort((a, b) => b.pfade.length - a.pfade.length)

  const nachBefund = ergebnisse.reduce<Record<string, number>>((acc, e) => {
    acc[e.befund] = (acc[e.befund] ?? 0) + 1
    return acc
  }, {})

  writeFileSync(
    resolve(process.cwd(), AUSGABE),
    JSON.stringify(
      {
        erzeugtAm: new Date().toISOString(),
        geprueft: ergebnisse.length,
        nachBefund,
        landetImNichts: ergebnisse
          .filter((e) => e.befund !== 'OK')
          .sort((a, b) => a.pfad.localeCompare(b.pfad)),
        doppelgaenger,
        alle: ergebnisse,
      },
      null,
      2,
    ),
    'utf-8',
  )
}

test.describe('Vor und zurück', () => {
  test.describe.configure({ timeout: 60_000 })

  /**
   * Wer vor und zurück geht, muss dort landen, wo er war. Geprüft an einer
   * kurzen Kette quer durch die Arbeitswelten — nicht an allen 786 Routen,
   * denn der Fehler säße in der Router-Verdrahtung, nicht an einer Maske.
   */
  test('die Kette führt zurück, wo sie hergekommen ist', async ({ page }) => {
    // `/verkauf/rechnungen` leitet auf die kanonische `/sales/rechnungen` um.
    // Verglichen wird deshalb der *erreichte* Pfad, nicht der eingegebene —
    // sonst meldet der Test eine funktionierende Umleitung als Fehler.
    const kette = ['/', '/crm', '/portal', '/verkauf/rechnungen']
    const gesehen: Array<{ pfad: string; ueberschrift: string }> = []

    for (const pfad of kette) {
      await page.goto(pfad, { waitUntil: 'domcontentloaded' })
      await waitForDashboardShell(page, 20_000)
      const ueberschrift = await ueberschriftAbwarten(page)
      gesehen.push({ pfad: new URL(page.url()).pathname, ueberschrift })
    }

    for (let i = kette.length - 2; i >= 0; i--) {
      await page.goBack({ waitUntil: 'domcontentloaded' })
      await waitForDashboardShell(page, 20_000)
      const ueberschrift = await ueberschriftAbwarten(page)
      expect(
        new URL(page.url()).pathname,
        `Zurück von Schritt ${i + 2} führte nicht auf ${gesehen[i].pfad}`,
      ).toBe(gesehen[i].pfad)
      if (gesehen[i].ueberschrift && ueberschrift) {
        expect(
          ueberschrift,
          `Zurück auf ${gesehen[i].pfad} zeigt eine andere Seite als beim Hinweg`,
        ).toBe(gesehen[i].ueberschrift)
      }
    }

    for (let i = 1; i < kette.length; i++) {
      await page.goForward({ waitUntil: 'domcontentloaded' })
      await waitForDashboardShell(page, 20_000)
      expect(
        new URL(page.url()).pathname,
        `Vorwärts führte nicht auf ${gesehen[i].pfad}`,
      ).toBe(gesehen[i].pfad)
    }
  })
})
