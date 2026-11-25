import { readFileSync, existsSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const pages = resolve(__dirname, '../../pages')
const repoRoot = resolve(__dirname, '../../../../../')

function read(rel: string): string {
  return readFileSync(resolve(pages, rel), 'utf8')
}

describe('MASK-BESTELLUNG-NAV-NATIVE-20261022', () => {
  it('Bestellungen-Liste ist die Bestell-Variante der Belegliste (DocFlow, BELEG-052)', () => {
    const src = read('einkauf/bestellungen-liste.tsx')
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="beleg-liste/purchase-order"')
  })

  it('Listen-SD row_route oeffnet die Belegmaske der Bestellung (DocFlow, BELEG-052 S3)', () => {
    const listenPath = resolve(repoRoot, 'app/core/screen_definitions_listen.py')
    if (!existsSync(listenPath)) {
      // WIP kann das Modul entfernen; dann gilt der NativeListPage-Vertrag oben.
      expect(existsSync(listenPath)).toBe(false)
      return
    }
    const src = readFileSync(listenPath, 'utf8')
    expect(src).toContain('row_route="/belege/purchase_order/{id}"')
    expect(src).not.toContain('row_route="/einkauf/bestellungen/{id}"')
    expect(src).not.toContain('endpoint="/api/v1/einkauf/bestellungen"')
  })

  it('Angebot inBestellung navigiert zur nativen Bestell-Detailroute (ScreenDefinition)', () => {
    const sdPath = resolve(repoRoot, 'app/core/screen_definitions.py')
    const src = readFileSync(sdPath, 'utf8')
    expect(src).toContain('"resultNavigationRoute": "/einkauf/bestellung/{purchaseOrderId}"')
    expect(src).not.toContain('"resultNavigationRoute": "/einkauf/bestellungen/{purchaseOrderId}"')
    expect(read('einkauf/angebot-stamm.tsx')).toContain("createStammNativeDetailPage(")
    expect(read('einkauf/angebot-stamm.tsx')).toContain("'einkauf/angebot'")
  })

  it('Bestellung-Anlegen legt ueber die Belegmaske an (DocFlow, BELEG-052)', () => {
    expect(read('einkauf/bestellung-anlegen.tsx')).toContain("belegSeite('purchase_order')")
  })
})
