import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative, resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

/**
 * Keine erfundenen Fachdaten als Ersatz fuer echte Antworten (20.10.2026).
 *
 * Gefunden und entfernt: erfundene Saatgut-/Duengerprodukte mit Bestand und Preisen, eine erfundene
 * Chargen-Rueckverfolgung, erfundene Lagerorte und Artikel in Einlagerung, Bestandskorrektur und LKW-Ablaeufen
 * (dort sogar der Artikelname als Kennung). Eine Seite zeigt bei Fehler oder leerer Antwort einen Fehler- bzw.
 * Leerzustand, nie Daten, die es nicht gibt.
 */
const SRC = resolve(__dirname, '../..')
const MUSTER = /const\s+[A-Z_]*(FALLBACK|MOCK|DUMMY|SAMPLE|FAKE)[A-Z_]*\s*(:[^=]+)?=\s*\[/

/** Ausdruecklich als Vorfuehrung gekennzeichnete Seiten; sie behaupten keine echten Daten. */
const AUSNAHMEN = new Map<string, string>([])

function dateien(verzeichnis: string): string[] {
  return readdirSync(verzeichnis).flatMap((name) => {
    const pfad = join(verzeichnis, name)
    if (statSync(pfad).isDirectory()) {
      return ['__tests__', 'mocks', 'stories', 'test'].includes(name) ? [] : dateien(pfad)
    }
    return /\.(ts|tsx)$/.test(name) && !/\.(test|spec|stories)\.tsx?$/.test(name) ? [pfad] : []
  })
}

describe('Keine Scheindaten', () => {
  it('Seiten, Features und Bibliotheken definieren keine Ersatzlisten mit erfundenen Daten', () => {
    const funde = ['pages', 'features', 'lib', 'components']
      .flatMap((teil) => dateien(join(SRC, teil)))
      .map((pfad) => relative(SRC, pfad).replaceAll('\\', '/'))
      .filter((pfad) => !AUSNAHMEN.has(pfad) && MUSTER.test(readFileSync(join(SRC, pfad), 'utf8')))
    expect(funde).toEqual([])
  })
})
