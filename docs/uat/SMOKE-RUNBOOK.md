# UAT Smoke-Runbook

**Ziel:** 30-Minuten-Quick-Check pro Domain zur Baseline-Verifikation

---

## Sales Domain (8 Min)

### 1. Angebote-Liste (2 Min)
- [ ] Navigiere zu `/sales/angebote`
- [ ] Seite lädt ohne Fehler
- [ ] Tabelle sichtbar
- [ ] Export-Button → CSV-Download oder Toast
- [ ] Drucken-Button → Print-Dialog oder Toast

### 2. Angebot erstellen (3 Min)
- [ ] Klicke "Neu" → `/sales/angebot/neu`
- [ ] Formular lädt
- [ ] Fülle 1 Feld aus (z. B. Kunde)
- [ ] Klicke "Speichern" (OK oder Toast-Meldung)

### 3. Order-Flow (3 Min)
- [ ] `/sales/order` lädt
- [ ] `/sales/delivery` lädt
- [ ] `/sales/invoice` lädt
- [ ] Mind. 1 Workflow-Button sichtbar

---

## Agrar Domain (6 Min)

### 1. PSM-Liste (2 Min)
- [ ] `/agrar/psm` lädt
- [ ] Tabelle/Grid sichtbar
- [ ] Export funktioniert

### 2. Saatgut (2 Min)
- [ ] `/agrar/saatgut-liste` lädt
- [ ] `/agrar/saatgut-stamm` lädt

### 3. Dünger (2 Min)
- [ ] `/agrar/duenger-liste` lädt
- [ ] `/agrar/duenger/bedarfsrechner` lädt

---

## CRM Domain (5 Min)

### 1. Kontakte (2 Min)
- [ ] `/crm/kontakte-liste` lädt
- [ ] Export-Button funktioniert
- [ ] Drucken-Button funktioniert

### 2. Leads (2 Min)
- [ ] `/crm/leads` lädt
- [ ] `/crm/lead/test-1` lädt (oder Leer-State)

### 3. Aktivitäten (1 Min)
- [ ] `/crm/aktivitaeten` lädt

---

## Finance Domain (6 Min)

### 1. Buchungsjournal (2 Min)
- [ ] `/finance/bookings/new` lädt
- [ ] Formular sichtbar

### 2. Debitoren (2 Min)
- [ ] `/fibu/debitoren` lädt
- [ ] `/fibu/offene-posten` lädt

### 3. OP-Verwaltung (2 Min)
- [ ] `/fibu/op-verwaltung` lädt

---

## Inventory Domain (5 Min)

### 1. Artikel (2 Min)
- [ ] `/artikel/liste` lädt
- [ ] Export funktioniert

### 2. Lager (2 Min)
- [ ] `/lager/bewegungen` lädt
- [ ] `/lager/bestand` lädt

### 3. Inventory (1 Min)
- [ ] `/inventory` lädt

---

## Ergebnis

**Gesamt:** 30 Min  
**Grün:** Alle Checks ✅  
**Rot:** Mind. 1 Check ❌ → Ticket anlegen, S2 oder höher

---

**Ausführung:**
- Manuell: Checkliste abhaken
- Automatisiert: `pnpm test:e2e:smoke`

