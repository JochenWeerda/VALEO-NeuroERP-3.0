import type { Page } from '@playwright/test'

/**
 * FSX-090a — technische Interaktionsmessung.
 *
 * Misst den **Weg** durch die Oberfläche, nicht die Bedienzeit. Playwright tippt
 * ohne Zögern, sucht nichts und liest nichts; jede Zahl, die hier entsteht, sagt
 * etwas über Struktur und nichts über Verständlichkeit. Letzteres ist FSX-090b
 * (Nutzerbeobachtung) und durch nichts hiervon zu ersetzen.
 *
 * Deshalb enthält dieser Helfer bewusst **keine** Zeitmessung der Aufgabe. Eine
 * "Dauer" wäre die Zahl, die am ehesten falsch zitiert würde.
 */

export type FlowSpineTaskVariant = 'vor-fsx' | 'nach-fsx'

export type FlowSpineTaskMetrics = {
  aufgabe: string
  variante: FlowSpineTaskVariant
  /** Wechsel der Route — jeder Wechsel ist ein Kontextbruch. */
  maskenwechsel: number
  /** Klicks auf Schaltflächen und Verweise. */
  klicks: number
  /** Feldeingaben (change-Ereignisse auf Eingabeelementen). */
  eingaben: number
  /** API-Aufrufe unter /api/v1/ — Netzwerkrunden bis zum Ziel. */
  netzwerkrunden: number
  /** Commit, gegen den gemessen wurde. Ohne ihn ist die Zahl nicht einordenbar. */
  commit: string
  gemessenAm: string
}

/**
 * Hängt Zähler an die Seite. Muss **vor** der ersten Navigation laufen.
 */
export async function startTaskMeasurement(page: Page): Promise<() => Promise<Omit<FlowSpineTaskMetrics, 'aufgabe' | 'variante' | 'commit' | 'gemessenAm'>>> {
  let maskenwechsel = 0
  let netzwerkrunden = 0

  page.on('framenavigated', (frame) => {
    if (frame === page.mainFrame()) maskenwechsel += 1
  })
  page.on('request', (request) => {
    if (/\/api\/v1\//.test(request.url())) netzwerkrunden += 1
  })

  // Klicks und Eingaben werden im Browser gezählt: Playwright-Aktionen lösen
  // echte DOM-Ereignisse aus, und eine Zählung im Seitenkontext erfasst auch
  // Klicks, die Folgeaktionen auslösen.
  await page.addInitScript(() => {
    const w = window as unknown as { __fsxKlicks?: number; __fsxEingaben?: number }
    w.__fsxKlicks = 0
    w.__fsxEingaben = 0
    document.addEventListener(
      'click',
      (event) => {
        const target = event.target as HTMLElement | null
        if (target?.closest('button, a, [role="button"], [role="tab"]')) {
          w.__fsxKlicks = (w.__fsxKlicks ?? 0) + 1
        }
      },
      true,
    )
    document.addEventListener(
      'change',
      (event) => {
        const target = event.target as HTMLElement | null
        if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement) {
          w.__fsxEingaben = (w.__fsxEingaben ?? 0) + 1
        }
      },
      true,
    )
  })

  return async () => {
    const zaehler = await page.evaluate(() => {
      const w = window as unknown as { __fsxKlicks?: number; __fsxEingaben?: number }
      return { klicks: w.__fsxKlicks ?? 0, eingaben: w.__fsxEingaben ?? 0 }
    })
    return {
      // Die erste Navigation ist das Öffnen selbst und zählt nicht als Wechsel.
      maskenwechsel: Math.max(0, maskenwechsel - 1),
      klicks: zaehler.klicks,
      eingaben: zaehler.eingaben,
      netzwerkrunden,
    }
  }
}

/**
 * Formatiert das Ergebnis als Protokollzeile.
 *
 * Bewusst ohne Bewertung: ob weniger Klicks besser sind, entscheidet nicht die
 * Zahl, sondern FSX-090b. Wer hier ein "besser" hineinschreibt, hat die
 * Trennung der beiden Verfahren wieder aufgehoben.
 */
export function protokollzeile(metrics: FlowSpineTaskMetrics): string {
  return [
    `Aufgabe: ${metrics.aufgabe}`,
    `Variante: ${metrics.variante}`,
    `Commit: ${metrics.commit}`,
    `Maskenwechsel: ${metrics.maskenwechsel}`,
    `Klicks: ${metrics.klicks}`,
    `Eingaben: ${metrics.eingaben}`,
    `Netzwerkrunden: ${metrics.netzwerkrunden}`,
    `Gemessen: ${metrics.gemessenAm}`,
  ].join(' | ')
}
