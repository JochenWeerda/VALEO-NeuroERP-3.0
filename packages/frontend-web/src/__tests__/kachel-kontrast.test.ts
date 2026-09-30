/**
 * Die Mikro-Überschrift auf einer getönten Kachel muss WCAG AA erreichen.
 *
 * Warum dieser Test und nicht der axe-Lauf allein: Der axe-Lauf auf `/` prüft
 * nur, was gerendert wurde. Im WCAG-Job ist das Backend nicht erreichbar, und
 * ohne Daten erscheint mitunter keine Kachel — dann ist der Lauf grün, ohne
 * etwas geprüft zu haben. Genau so wechselte der Job zwischen grün und rot,
 * während der Fehler unverändert bestand.
 *
 * Dieser Test liest die echten Farbtokens aus `styles/tokens/palette.css` und
 * rechnet den Kontrast für **alle** sechs Chart-Töne und beide Deckungsgrade,
 * die `launchpadTileSurface()` verwendet. Er ist deterministisch und schlägt
 * auch dann an, wenn jemand einen Chart-Ton abdunkelt oder den Vordergrund
 * aufhellt.
 *
 * Der Befund vom 30.09.2026: Mit `text-muted-foreground` lagen **alle zwölf**
 * Kombinationen zwischen 3,18 und 4,50 — unter den geforderten 4,5:1. Mit
 * `text-foreground` sind es 8,84 bis 12,52.
 */

import { readFileSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

const PALETTE = readFileSync(
  join(__dirname, '..', 'styles', 'tokens', 'palette.css'),
  'utf8',
)

/** Liest `--name: H S% L%;` aus der Palette. */
function token(name: string): [number, number, number] {
  const treffer = PALETTE.match(
    new RegExp(`--${name}:\\s*([\\d.]+)\\s+([\\d.]+)%\\s+([\\d.]+)%`),
  )
  if (!treffer) throw new Error(`Token --${name} steht nicht in palette.css`)
  return [Number(treffer[1]), Number(treffer[2]), Number(treffer[3])]
}

function hslZuRgb([h, s, l]: [number, number, number]): [number, number, number] {
  const sN = s / 100
  const lN = l / 100
  const c = (1 - Math.abs(2 * lN - 1)) * sN
  const hh = h / 60
  const x = c * (1 - Math.abs((hh % 2) - 1))
  const [r1, g1, b1] =
    hh < 1 ? [c, x, 0]
    : hh < 2 ? [x, c, 0]
    : hh < 3 ? [0, c, x]
    : hh < 4 ? [0, x, c]
    : hh < 5 ? [x, 0, c]
    : [c, 0, x]
  const m = lN - c / 2
  return [(r1 + m) * 255, (g1 + m) * 255, (b1 + m) * 255]
}

/** Deckung alpha über einem Hintergrund — so entsteht die Kachelfläche. */
function ueberlagern(
  vorne: [number, number, number],
  hinten: [number, number, number],
  alpha: number,
): [number, number, number] {
  return [0, 1, 2].map((i) => vorne[i] * alpha + hinten[i] * (1 - alpha)) as [
    number, number, number,
  ]
}

function leuchtdichte([r, g, b]: [number, number, number]): number {
  const f = (v: number): number => {
    const n = v / 255
    return n <= 0.03928 ? n / 12.92 : ((n + 0.055) / 1.055) ** 2.4
  }
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
}

function kontrast(
  a: [number, number, number],
  b: [number, number, number],
): number {
  const la = leuchtdichte(a)
  const lb = leuchtdichte(b)
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05)
}

/** Die Deckungsgrade aus launchpadTileSurface(): app 0.28, sonst 0.40. */
const DECKUNGEN = [0.28, 0.4]
const CHART_TOENE = [1, 2, 3, 4, 5, 6]
const AA_SCHWELLE = 4.5

describe('Kachel-Kontrast auf getönter Fläche', () => {
  const seite = hslZuRgb(token('color-neutral-50-hsl')) // --background
  const vordergrund = hslZuRgb(token('color-neutral-900-hsl')) // --foreground
  const gedaempft = hslZuRgb(token('color-neutral-600-hsl')) // --muted-foreground

  it.each(
    CHART_TOENE.flatMap((ton) => DECKUNGEN.map((deckung) => ({ ton, deckung }))),
  )(
    'text-foreground erreicht AA auf Chart-Ton $ton bei Deckung $deckung',
    ({ ton, deckung }) => {
      const flaeche = ueberlagern(hslZuRgb(token(`chart-${ton}-hsl`)), seite, deckung)
      expect(kontrast(vordergrund, flaeche)).toBeGreaterThanOrEqual(AA_SCHWELLE)
    },
  )

  it('text-muted-foreground würde AA verfehlen — deshalb steht es dort nicht', () => {
    // Kein Selbstzweck: Wer die Klasse zurückdreht, soll an dieser Zeile
    // sehen, dass es gemessen und nicht vermutet wurde.
    const verfehlt = CHART_TOENE.flatMap((ton) =>
      DECKUNGEN.map((deckung) => {
        const flaeche = ueberlagern(hslZuRgb(token(`chart-${ton}-hsl`)), seite, deckung)
        return kontrast(gedaempft, flaeche)
      }),
    ).filter((wert) => wert < AA_SCHWELLE)

    expect(verfehlt).toHaveLength(CHART_TOENE.length * DECKUNGEN.length)
  })

  it('die Kachelfläche selbst hebt sich von der Seite ab', () => {
    // Ohne diesen Unterschied wäre die Kachel nicht als Fläche erkennbar.
    for (const ton of CHART_TOENE) {
      const flaeche = ueberlagern(hslZuRgb(token(`chart-${ton}-hsl`)), seite, 0.28)
      expect(kontrast(flaeche, seite)).toBeGreaterThan(1.1)
    }
  })
})
