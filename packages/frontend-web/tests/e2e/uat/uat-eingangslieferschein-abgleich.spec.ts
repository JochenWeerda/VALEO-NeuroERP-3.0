/**
 * UAT: Eingangslieferschein → Bestellabgleich → Einbuchen → Bestandskorrektur
 *
 * Nachbildung eines Realbelegs (Auricher Süssmost, Lieferschein LI2500740,
 * 9 Positionen mit Chargen, Gebinde 6x0,7): der Eingangslieferschein wird
 * automatisiert erfasst, gegen die Einkaufsbestellung abgeglichen
 * (POST /einkauf/lieferscheine/{id}/bestellung-abgleich), eingebucht
 * (POST .../einbuchen → EINLAGERUNG-Bewegungen) und die Bestandskorrektur
 * je Artikel verifiziert.
 *
 * Gewollte Abweichung: Rhabarberschorle (007161) bestellt 48 Fl, geliefert
 * 36 Fl → der Abgleich muss genau diese eine UNTERLIEFERUNG melden.
 */
import { test, expect } from '@playwright/test'

const API = process.env.API_URL ?? 'http://127.0.0.1:8000'
const TOKEN = process.env.API_DEV_TOKEN ?? 'dev-token'
const TENANT = process.env.TENANT_ID ?? '00000000-0000-0000-0000-000000000001'
const RUN = Date.now().toString()

async function api(method: string, path: string, body?: unknown): Promise<{ status: number; ms: number; body: any }> {
  const t0 = Date.now()
  const resp = await fetch(`${API}${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      'X-Tenant-Id': TENANT,
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  })
  let parsed: any = null
  try { parsed = await resp.json() } catch { /* leerer Body */ }
  return { status: resp.status, ms: Date.now() - t0, body: parsed }
}

function ann(label: string, value: string): void {
  test.info().annotations.push({ type: label, description: value })
}

// Beleg LI2500740: [artikel_nr, bezeichnung, menge_geliefert_fl, charge]
const POSITIONEN: Array<[string, string, number, string]> = [
  ['007561', 'Auricher Mango Maracuja Nektar 6/0,7', 12, '250616'],
  ['007461', 'Auricher Himbeer Maracuja Nektar 6/0,7', 36, '250517'],
  ['002861', 'Auricher Birne Sanddorn Direktsaft 100%', 18, '251211'],
  ['002761', 'Auricher Quittensaft Direktsaft 100%', 24, '251308'],
  ['007061', 'Auricher Orangen Direktsaft 100% 6/0,7', 36, '244904'],
  ['005561', 'Auricher Pink Grapefruit Saft 100%', 36, '251311'],
  ['007961', 'Auricher Apfel Holundersaft 100% 6/0,7', 24, '250701'],
  ['002661', 'Auricher Apfelschorle 65%', 36, '271008'],
  ['007161', 'Auricher Rhabarberschorle 6/0,7', 36, '245017'],
]
const BESTELLMENGE = (nr: string, geliefert: number): number => (nr === '007161' ? 48 : geliefert)

test.describe.serial('UAT TC-ELS: Eingangslieferschein-Abgleich (Realbeleg Auricher)', () => {
  let lieferantId: string
  let bestellungId: string
  let lieferscheinId: string
  let warehouseId: string
  const artikelIds: Record<string, string> = {}
  const bestandVorher: Record<string, number> = {}

  test('TC-ELS-001: Stammdaten sicherstellen (Lieferant, 9 Artikel, Lager mit Bin)', async () => {
    // Lieferant
    const lief = await api('GET', '/api/v1/einkauf/lieferanten?search=Auricher')
    const liefItems = Array.isArray(lief.body) ? lief.body : lief.body?.items ?? []
    lieferantId = liefItems.find((l: any) => (l.firmenname ?? '').includes('Auricher'))?.id
    if (!lieferantId) {
      const created = await api('POST', '/api/v1/einkauf/lieferanten', {
        lieferantennummer: '70011',
        firmenname: 'Auricher Süssmost GmbH',
        strasse: 'Kreihüttenmoorweg 11', plz: '26607', ort: 'Aurich',
        ust_id: 'DE343011631',
      })
      expect([200, 201]).toContain(created.status)
      lieferantId = created.body.id
    }

    // Artikel
    for (const [nr, bez] of POSITIONEN) {
      const found = await api('GET', `/api/v1/articles/?search=${nr}&limit=5`)
      const items = found.body?.items ?? found.body ?? []
      const hit = Array.isArray(items) ? items.find((a: any) => a.article_number === nr) : undefined
      if (hit) { artikelIds[nr] = hit.id; continue }
      const created = await api('POST', '/api/v1/articles/', {
        article_number: nr, name: bez, unit: 'Fl', base_unit: 'Fl',
        category: 'Getränke', tenant_id: TENANT,
        sales_price: 1.99, purchase_price: 1.2, is_active: true,
      })
      expect([200, 201]).toContain(created.status)
      artikelIds[nr] = created.body.id
    }

    // Lager + Bin (einbuchen braucht Lagerplatz mit Kapazität)
    const whs = await api('GET', '/api/v1/warehouses/?limit=5')
    const whItems = whs.body?.items ?? whs.body ?? []
    warehouseId = whItems[0]?.id
    expect(warehouseId, 'Warehouse muss existieren').toBeTruthy()
    const bins = await api('GET', `/api/v1/lager/wms/bins?warehouse_id=${warehouseId}`)
    const binItems = Array.isArray(bins.body) ? bins.body : bins.body?.items ?? []
    if (!binItems.length) {
      const zones = await api('GET', `/api/v1/lager/wms/zones?warehouse_id=${warehouseId}`)
      const zoneItems = Array.isArray(zones.body) ? zones.body : zones.body?.items ?? []
      let zoneId = zoneItems[0]?.id
      if (!zoneId) {
        const z = await api('POST', `/api/v1/lager/wms/zones?warehouse_id=${warehouseId}`,
          { zone_code: 'Z1', name: 'Zone 1 Getränke', zone_type: 'standard' })
        expect([200, 201]).toContain(z.status)
        zoneId = z.body.id
      }
      const b = await api('POST', `/api/v1/lager/wms/bins?zone_id=${zoneId}&warehouse_id=${warehouseId}`,
        { bin_code: `Z1-${RUN.slice(-6)}`, bin_type: 'standard', capacity_kg: 100000 })
      expect([200, 201]).toContain(b.status)
    }
    ann('Setup', `Lieferant ${lieferantId}, ${Object.keys(artikelIds).length} Artikel, Lager ${warehouseId}`)
  })

  test('TC-ELS-002: Bestellung anlegen (mit gewollter Abweichung 007161: 48 statt 36)', async () => {
    const result = await api('POST', '/api/v1/einkauf/bestellungen', {
      lieferant_id: lieferantId,
      bestelldatum: new Date().toISOString().slice(0, 10),
      unsere_referenz: `E2E-AURICHER-${RUN}`,
      positionen: POSITIONEN.map(([nr, bez, menge]) => ({
        artikel_nr: nr, artikel_bezeichnung: bez, article_id: artikelIds[nr],
        menge: BESTELLMENGE(nr, menge), einheit: 'Fl', einzelpreis: 1.2, preis_einheit: 'Stk',
      })),
    })
    ann('Ladezeit', `POST /einkauf/bestellungen: ${result.ms} ms`)
    expect([200, 201]).toContain(result.status)
    bestellungId = result.body.id
    ann('Ergebnis', `Bestellung ${result.body.bestellnummer} (${bestellungId})`)
  })

  test('TC-ELS-003: Eingangslieferschein automatisiert erfassen (9 Positionen, Chargen)', async () => {
    const result = await api('POST', `/api/v1/einkauf/lieferscheine?tenant_id=${TENANT}`, {
      lieferschein_nr: `LI2500740-${RUN}`,
      lieferschein_datum: new Date().toISOString().slice(0, 10),
      lieferant_id: lieferantId,
      lieferant_name: 'Auricher Süssmost GmbH',
      liefer_nr: '2500630',
      positionen: POSITIONEN.map(([nr, bez, menge, charge], i) => ({
        pos_nr: i + 1, artikel_nr: nr, bezeichnung: bez, gebinde: 6,
        menge, einheit: 'Fl', einzelpreis: 1.2, charge,
      })),
    })
    ann('Ladezeit', `POST /einkauf/lieferscheine: ${result.ms} ms`)
    expect([200, 201]).toContain(result.status)
    lieferscheinId = result.body.id
    expect(result.body.positionen).toHaveLength(9)
    ann('Ergebnis', `Eingangslieferschein ${lieferscheinId}`)
  })

  test('TC-ELS-004: Bestellabgleich — 8 MATCH, genau 1 UNTERLIEFERUNG (007161)', async () => {
    const result = await api('POST',
      `/api/v1/einkauf/lieferscheine/${lieferscheinId}/bestellung-abgleich?tenant_id=${TENANT}`,
      { bestellung_id: bestellungId })
    ann('Ladezeit', `POST bestellung-abgleich: ${result.ms} ms`)
    expect(result.status).toBe(200)
    expect(result.body.match).toBe(8)
    expect(result.body.abweichungen).toBe(1)
    const abweichung = result.body.positionen.filter((p: any) => p.status !== 'MATCH')
    expect(abweichung).toHaveLength(1)
    expect(abweichung[0].artikel_nr).toBe('007161')
    expect(abweichung[0].status).toBe('UNTERLIEFERUNG')
    expect(abweichung[0].differenz).toBe(-12)
    expect(result.body.bestellung_status).toBe('teilgeliefert')
    ann('Ergebnis', `Abgleich: 8 MATCH, 1 UNTERLIEFERUNG (007161, -12 Fl), Bestellung teilgeliefert`)
  })

  test('TC-ELS-005: Einbuchen — 9 EINLAGERUNG-Bewegungen', async () => {
    // Bestand vorher merken
    for (const [nr] of POSITIONEN) {
      const rows = await api('GET', `/api/v1/lager/bestaende?article_id=${artikelIds[nr]}&tenant_id=${TENANT}`)
      bestandVorher[nr] = Array.isArray(rows.body)
        ? rows.body.reduce((s: number, r: any) => s + (r.menge ?? 0), 0)
        : 0
    }
    const result = await api('POST',
      `/api/v1/einkauf/lieferscheine/${lieferscheinId}/einbuchen?tenant_id=${TENANT}`,
      { warehouse_id: warehouseId })
    ann('Ladezeit', `POST einbuchen: ${result.ms} ms`)
    expect(result.status).toBe(200)
    expect(result.body.movements_created).toBe(9)
    expect(result.body.positions_skipped).toBe(0)
    ann('Ergebnis', `${result.body.movements_created} Lagerbewegungen`)
  })

  test('TC-ELS-006: Bestandskorrektur — jede Position exakt um Liefermenge erhöht', async () => {
    for (const [nr, , menge] of POSITIONEN) {
      const rows = await api('GET', `/api/v1/lager/bestaende?article_id=${artikelIds[nr]}&tenant_id=${TENANT}`)
      const total = Array.isArray(rows.body)
        ? rows.body.reduce((s: number, r: any) => s + (r.menge ?? 0), 0)
        : 0
      expect(total - (bestandVorher[nr] ?? 0), `Artikel ${nr}: Bestandskorrektur`).toBeCloseTo(menge, 3)
    }
    ann('Ergebnis', 'Bestandskorrektur für alle 9 Positionen exakt verifiziert')
  })
})
