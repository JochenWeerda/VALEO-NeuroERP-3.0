# Systematischer Test-Plan

## Phase 1: Frontend-Seiten Test

### CRM Domain
- [ ] `/crm/kunden` - Kundenliste
- [ ] `/crm/kunden/stamm/new` - Neuer Kunde
- [ ] `/crm/kontakte` - Kontaktliste
- [ ] `/crm/leads` - Leads
- [ ] `/crm/aktivitaeten` - Aktivitäten

### Purchase Domain
- [ ] `/einkauf/bestellungen` - Bestellungen
- [ ] `/einkauf/bestellung-anlegen` - Neue Bestellung
- [ ] `/einkauf/bestellung-stamm` - Bestellung bearbeiten
- [ ] `/einkauf/anfrage-stamm` - Anfrage
- [ ] `/einkauf/angebot-stamm` - Angebot

### Sales Domain
- [ ] `/sales/auftraege` - Aufträge
- [ ] `/sales/rechnungen` - Rechnungen
- [ ] `/sales/lieferungen` - Lieferungen
- [ ] `/sales/order-editor` - Auftrag Editor

### Finance Domain
- [ ] `/finance/debitoren` - Debitoren
- [ ] `/finance/kreditoren` - Kreditoren
- [ ] `/finance/kasse` - Kasse
- [ ] `/finance/mahnwesen` - Mahnwesen

## Phase 2: API-Endpunkte Test

### Backend Health
- [ ] `GET /health` - Health Check
- [ ] `GET /api/health` - API Health

### CRUD-Operationen
- [ ] `GET /api/crm/kunden` - Liste
- [ ] `POST /api/crm/kunden` - Erstellen
- [ ] `PUT /api/crm/kunden/{id}` - Aktualisieren
- [ ] `DELETE /api/crm/kunden/{id}` - Löschen

## Phase 3: i18n-Tests

- [ ] Alle Seiten zeigen deutsche Übersetzungen
- [ ] Keine hardcoded deutschen Texte
- [ ] Tooltips funktionieren
- [ ] Placeholder-Texte übersetzt

## Phase 4: Integration-Tests

- [ ] Frontend kann Backend erreichen
- [ ] Daten werden korrekt geladen
- [ ] Fehlerbehandlung funktioniert
- [ ] Loading-States werden angezeigt

