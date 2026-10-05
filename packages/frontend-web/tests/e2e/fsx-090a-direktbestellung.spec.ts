/**
 * FSX-090a — technische Interaktionsmessung: Direktbestellung.
 *
 * Misst den Weg durch die Oberflaeche fuer die Aufgabe, an der die
 * Ausgangsdiagnose haengt: eine Direktbestellung aus dem Procure-to-Pay-Vorgang
 * heraus erfassen.
 *
 * WAS DIESE MESSUNG NICHT IST — und das gehoert an den Anfang, weil die Zahlen
 * sonst falsch zitiert werden:
 *
 * Playwright tippt ohne Zoegern, sucht nichts und liest nichts. Die Zahlen sagen
 * etwas ueber **Struktur** (wie viele Wechsel, Klicks, Eingaben und
 * Netzwerkrunden die Aufgabe kostet) und **nichts** ueber Bedienzeit oder
 * Verstaendlichkeit. Ob ein Sachbearbeiter die Sperre versteht, ob er die
 * naechste Aktion findet, ob ihn das Prozessband ohne Erklaertext traegt — das
 * beantwortet ausschliesslich FSX-090b (Nutzerbeobachtung).
 *
 * Eine kuerzere Prozessleiste allein ist kein Nachweis.
 *
 * VERGLEICH ALT GEGEN NEU — Verfahren, bewusst nicht automatisiert:
 *
 * Der Stand "vor FSX" liegt in der Historie, nicht im Arbeitsbaum. Der Vergleich
 * laeuft deshalb ueber zwei Laeufe:
 *
 *   1. `git worktree add ../valeo-vor-fsx cb7a38f99` (letzter Commit vor FSX-002)
 *   2. dort `pnpm install && pnpm build`, Stack starten, diesen Spec laufen
 *   3. Protokollzeile mit `Variante: vor-fsx` sichern
 *   4. im Hauptbaum denselben Spec laufen, `Variante: nach-fsx`
 *
 * Automatisiert waere das ein Bauwerk, das bei jeder Toolchain-Aenderung bricht
 * — fuer eine Messung, die zweimal stattfindet.
 */
import { test, expect } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'
import {
  startTaskMeasurement,
  protokollzeile,
  type FlowSpineTaskMetrics,
} from './helpers/flow-spine-task-metrics'

const COMMIT = process.env.FSX_MESSUNG_COMMIT ?? 'unbekannt'
const VARIANTE = (process.env.FSX_MESSUNG_VARIANTE ?? 'nach-fsx') as FlowSpineTaskMetrics['variante']

test.describe('FSX-090a Direktbestellung', () => {
  test('misst den Weg von der Bestellmaske bis zur ausgefuellten Position', async ({ page }, testInfo) => {
    await prepareE2EAuth(page)
    const auswerten = await startTaskMeasurement(page)

    // Einstieg wie im Handover: aus dem Procure-to-Pay-Vorgang in die Maske.
    await page.goto(
      '/einkauf/bestellungen/neu?workflowProcess=procure-to-pay&workflowInstanceId=e2e-1' +
        '&workflowCase=WF-E2E-001&entryMode=Direktbestellung&partnerName=Agrarhandel%20Nord' +
        '&subject=Saisonbedarf',
    )
    await waitForDashboardShell(page)

    // Der Lieferant kommt aus dem Handover — wer ihn erneut tippen muss, hat
    // einen Medienbruch, und genau das soll die Zahl zeigen.
    const lieferant = page.getByLabel('Lieferant *')
    await expect(lieferant).toBeVisible()

    await page.getByRole('button', { name: 'Weiter' }).click()

    const artikel = page.getByPlaceholder('Artikel')
    await expect(artikel).toBeVisible()
    await artikel.fill('Weizen A-Qualitaet')
    await page.getByRole('spinbutton').nth(1).fill('24')

    const metrics: FlowSpineTaskMetrics = {
      aufgabe: 'Direktbestellung aus P2P-Handover bis ausgefuellte Position',
      variante: VARIANTE,
      commit: COMMIT,
      gemessenAm: new Date().toISOString(),
      ...(await auswerten()),
    }

    // Das Ergebnis ist der Zweck des Tests, nicht eine Nebenausgabe.
    await testInfo.attach('fsx-090a-messung', {
      body: protokollzeile(metrics),
      contentType: 'text/plain',
    })
    // eslint-disable-next-line no-console -- Messprotokoll ist hier das Ergebnis.
    console.log(protokollzeile(metrics))

    // Bewusst keine Schwellwerte: eine Zahl, gegen die niemand etwas haelt,
    // waere eine erfundene Norm. Der Vergleich passiert zwischen zwei Laeufen,
    // nicht gegen eine hier hineingeschriebene Erwartung.
    expect(metrics.eingaben).toBeGreaterThan(0)
  })
})
