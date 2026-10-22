import { readFileSync, existsSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const pages = resolve(__dirname, '../../pages')
const repoRoot = resolve(__dirname, '../../../../../')

function read(rel: string): string {
  return readFileSync(resolve(pages, rel), 'utf8')
}

describe('MASK-BESTELLUNG-NAV-NATIVE-20261022', () => {
  it('Bestellungen-Liste ist NativeListPage auf Screen einkauf/bestellungen', () => {
    const src = read('einkauf/bestellungen-liste.tsx')
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="einkauf/bestellungen"')
  })

  it('Listen-SD row_route zeigt auf native Singular-Detailroute wenn Listen-Modul vorhanden', () => {
    const listenPath = resolve(repoRoot, 'app/core/screen_definitions_listen.py')
    if (!existsSync(listenPath)) {
      // WIP kann das Modul entfernen; dann gilt der NativeListPage-Vertrag oben.
      expect(existsSync(listenPath)).toBe(false)
      return
    }
    const src = readFileSync(listenPath, 'utf8')
    expect(src).toContain('row_route="/einkauf/bestellung/{id}"')
    expect(src).not.toContain('row_route="/einkauf/bestellungen/{id}"')
  })

  it('Angebot-Stamm Folgebestellung oeffnet die native Detailroute', () => {
    expect(read('einkauf/angebot-stamm.tsx')).toContain(
      '`/einkauf/bestellung/${encodeURIComponent(response.data.purchaseOrderId)}`',
    )
    expect(read('einkauf/angebot-stamm.tsx')).not.toContain(
      '`/einkauf/bestellungen/${encodeURIComponent(response.data.purchaseOrderId)}`',
    )
  })

  it('Bestellung-Anlegen resumed auf native Detailroute', () => {
    const src = read('einkauf/bestellung-anlegen.tsx')
    expect(src).toContain('`/einkauf/bestellung/${encodeURIComponent(purchaseOrderId)}')
    expect(src).toContain('`/einkauf/bestellung/${encodeURIComponent(pendingLink.purchaseOrderId)}')
    expect(src).not.toMatch(
      /navigate\(\s*`\/einkauf\/bestellungen\/\$\{encodeURIComponent\(purchaseOrderId\)\}/,
    )
  })
})
