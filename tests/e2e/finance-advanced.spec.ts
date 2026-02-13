/**
 * E2E Tests für Finance Advanced Features
 * Playwright Test-Suite für Wechselkurse, Buchungsschemata, Kostenrechnung, etc.
 */

import { test, expect } from '@playwright/test';

const AUTH_TOKEN = process.env.E2E_AUTH_TOKEN || 'dev-token';
const BASE_URL = process.env.API_URL || 'http://localhost:8000';

const headers = {
  'Authorization': `Bearer ${AUTH_TOKEN}`,
  'Content-Type': 'application/json',
};

test.describe('Finance Advanced - Wechselkurse', () => {
  test('S01: Wechselkurs erstellen und abrufen', async ({ request }) => {
    // Wechselkurs erstellen
    const createResponse = await request.post(`${BASE_URL}/api/finance/wechselkurse`, {
      headers,
      data: {
        waehrung_von: 'USD',
        waehrung_nach: 'EUR',
        kurs: 0.92,
        kurs_datum: '2026-02-12',
        quelle: 'EZB'
      }
    });
    
    expect(createResponse.status()).toBe(201);
    const created = await createResponse.json();
    expect(created.waehrung_von).toBe('USD');
    expect(created.waehrung_nach).toBe('EUR');
    
    // Abrufen
    const getResponse = await request.get(`${BASE_URL}/api/finance/wechselkurse/${created.id}`, { headers });
    expect(getResponse.status()).toBe(200);
    const fetched = await getResponse.json();
    expect(fetched.kurs).toBe(0.92);
  });

  test('S02: Wechselkurse listen', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/finance/wechselkurse`, { headers });
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(Array.isArray(data)).toBe(true);
  });

  test('S03: Währungsumrechnung', async ({ request }) => {
    // Mit Fremdwährung rechnen
    const response = await request.post(`${BASE_URL}/api/finance/wechselkurse/convert`, {
      headers,
      data: {
        betrag: 100,
        waehrung_von: 'USD',
        waehrung_nach: 'EUR'
      }
    });
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.betrag_eur).toBeDefined();
  });
});

test.describe('Finance Advanced - Buchungsschemata', () => {
  test('S10: Buchungsschema erstellen', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/api/finance/buchungsschemata`, {
      headers,
      data: {
        name: 'Eingangsrechnung Standard',
        beschreibung: 'Standard-Buchungsschema für ER',
        belegart: 'ER',
        soll_konto_schema: '6000',
        haben_konto_schema: '4400',
        steuer_code: 'VORSTEUER',
        steuer_satz: 19.0,
        aktiv: true,
        prioritaet: 10
      }
    });
    
    expect(response.status()).toBe(201);
    const created = await response.json();
    expect(created.name).toBe('Eingangsrechnung Standard');
    expect(created.belegart).toBe('ER');
  });

  test('S11: Buchungsschema für automatischen Vorschlag nutzen', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/api/finance/buchungsschemata/vorschlag`, {
      headers,
      data: {
        belegart: 'ER',
        betrag: 1000.00,
        text: 'Testrechnung',
        partner_id: 'LIEFERANT-001'
      }
    });
    
    expect(response.status()).toBe(200);
    const vorschlag = await response.json();
    expect(vorschlag.soll_konto).toBeDefined();
    expect(vorschlag.haben_konto).toBeDefined();
    expect(vorschlag.konfidenz).toBeDefined();
  });
});

test.describe('Finance Advanced - Kostenrechnung', () => {
  test('S20: Kostenstelle erstellen', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/api/finance/kostenstellen`, {
      headers,
      data: {
        nummer: 'KS-100',
        bezeichnung: 'Produktion Hauptwerk',
        kostenstelle_art: 'KOSTENSTELLE',
        verantwortlicher: 'Max Mustermann',
        budget: 50000.00,
        budget_periode: 'MONAT',
        aktiv: true
      }
    });
    
    expect(response.status()).toBe(201);
    const created = await response.json();
    expect(created.nummer).toBe('KS-100');
    expect(created.budget).toBe(50000.00);
  });

  test('S21: Kostenstellen-Hierarchie', async ({ request }) => {
    // Parent erstellen
    const parent = await request.post(`${BASE_URL}/api/finance/kostenstellen`, {
      headers,
      data: {
        nummer: 'KS-000',
        bezeichnung: 'Gesamtunternehmen',
        kostenstelle_art: 'ABTEILUNG',
        budget: 1000000.00,
        budget_periode: 'JAHR'
      }
    });
    
    // Child erstellen
    const child = await request.post(`${BASE_URL}/api/finance/kostenstellen`, {
      headers,
      data: {
        nummer: 'KS-100',
        bezeichnung: 'Produktion',
        kostenstelle_art: 'KOSTENSTELLE',
        uebergeordnet: (await parent.json()).id
      }
    });
    
    expect(child.status()).toBe(201);
  });

  test('S22: Kostenstellen-Report', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/finance/kostenstellen/report`, {
      headers,
      params: {
        von: '2026-01-01',
        bis: '2026-01-31'
      }
    });
    
    expect(response.status()).toBe(200);
    const report = await response.json();
    expect(report.gesamt_budget).toBeDefined();
    expect(report.gesamt_verbraucht).toBeDefined();
  });
});

test.describe('Finance Advanced - Abschlusschecklisten', () => {
  test('S30: Checkliste für Monatsabschluss erstellen', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/api/finance/checklisten`, {
      headers,
      data: {
        periode: '2026-01',
        abschluss_art: 'MONATLICH',
        verantwortlicher: 'Max Mustermann',
        items: [
          { id: '1', name: 'Alle Belege gebucht', status: 'OFFEN' },
          { id: '2', name: 'Kassenabschluss', status: 'OFFEN' },
          { id: '3', name: 'Bankabstimmung', status: 'OFFEN' }
        ]
      }
    });
    
    expect(response.status()).toBe(201);
    const created = await response.json();
    expect(created.periode).toBe('2026-01');
    expect(created.abschluss_art).toBe('MONATLICH');
    expect(created.items.length).toBe(3);
  });

  test('S31: Checklisten-Item abhaken', async ({ request }) => {
    // Erstelle Checkliste
    const create = await request.post(`${BASE_URL}/api/finance/checklisten`, {
      headers,
      data: {
        periode: '2026-02',
        abschluss_art: 'MONATLICH',
        items: [{ id: '1', name: 'Test Item', status: 'OFFEN' }]
      }
    });
    const checkliste = await create.json();
    
    // Update Item
    const update = await request.put(`${BASE_URL}/api/finance/checklisten/${checkliste.id}/items/1`, {
      headers,
      data: {
        item_id: '1',
        status: 'ERLEDIGT',
        bearbeiter: 'Max Mustermann',
        bemerkung: 'Erledigt am 2026-02-12'
      }
    });
    
    expect(update.status()).toBe(200);
  });

  test('S32: Checkliste abschließen', async ({ request }) => {
    const create = await request.post(`${BASE_URL}/api/finance/checklisten`, {
      headers,
      data: {
        periode: '2026-02',
        abschluss_art: 'MONATLICH',
        items: [{ id: '1', name: 'Test', status: 'ERLEDIGT' }]
      }
    });
    const checkliste = await create.json();
    
    const close = await request.put(`${BASE_URL}/api/finance/checklisten/${checkliste.id}`, {
      headers,
      data: {
        status: 'ABGESCHLOSSEN',
        abschluss_datum: '2026-02-12'
      }
    });
    
    expect(close.status()).toBe(200);
    const closed = await close.json();
    expect(closed.status).toBe('ABGESCHLOSSEN');
  });
});

test.describe('Finance Advanced - Nebenbuch-Abstimmung', () => {
  test('S40: Abstimmung erstellen und ausführen', async ({ request }) => {
    const create = await request.post(`${BASE_URL}/api/finance/abstimmung/nebenbuch`, {
      headers,
      data: {
        abstimmungs_datum: '2026-02-12',
        buchungskreis: 'DE01'
      }
    });
    
    expect(create.status()).toBe(201);
    const abstimmung = await create.json();
    
    // Ausführen
    const execute = await request.post(
      `${BASE_URL}/api/finance/abstimmung/nebenbuch/${abstimmung.id}/ausfuehren`,
      { headers }
    );
    
    expect(execute.status()).toBe(200);
  });

  test('S41: Debitoren-Abstimmung', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/finance/abstimmung/debitoren`, {
      headers,
      params: {
        datum: '2026-02-12'
      }
    });
    
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.kunden).toBeDefined();
  });
});

test.describe('Finance Advanced - Intercompany', () => {
  test('S50: Intercompany-Buchung erstellen', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/api/finance/intercompany`, {
      headers,
      data: {
        gesellschaft_von: 'DE01',
        gesellschaft_nach: 'AT01',
        belegnr: 'IC-2026-0001',
        datum: '2026-02-12',
        betrag: 10000.00,
        waehrung: 'EUR',
        konto_von: '1400',
        konto_nach: '2400',
        referenz: 'Interne Verrechnung Q1'
      }
    });
    
    expect(response.status()).toBe(201);
    const created = await response.json();
    expect(created.gesellschaft_von).toBe('DE01');
    expect(created.status).toBe('ERSTELLT');
  });

  test('S51: Gegenbuchung erstellen', async ({ request }) => {
    // Erstelle Original
    const create = await request.post(`${BASE_URL}/api/finance/intercompany`, {
      headers,
      data: {
        gesellschaft_von: 'DE01',
        gesellschaft_nach: 'AT01',
        belegnr: 'IC-2026-0002',
        datum: '2026-02-12',
        betrag: 5000.00,
        waehrung: 'EUR',
        konto_von: '1400',
        konto_nach: '2400'
      }
    });
    const original = await create.json();
    
    // Gegenbuchung
    const gegenbuchung = await request.post(
      `${BASE_URL}/api/finance/intercompany/${original.id}/gegenbuchung`,
      { headers }
    );
    
    expect(gegenbuchung.status()).toBe(200);
  });

  test('S52: Intercompany-Salden', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/finance/intercompany/salden`, {
      headers,
      params: {
        gesellschaft: 'DE01'
      }
    });
    
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(Array.isArray(data)).toBe(true);
  });
});
