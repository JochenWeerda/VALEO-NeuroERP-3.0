***REMOVED*** UAT Smoke-Runbook

**Ziel:** 30-Minuten-Quick-Check pro Domain zur Baseline-Verifikation

---

***REMOVED******REMOVED*** Sales Domain (8 Min)

***REMOVED******REMOVED******REMOVED*** 1. Angebote-Liste (2 Min)
- [ ] Navigiere zu `/sales/angebote`
- [ ] Seite lädt ohne Fehler
- [ ] Tabelle sichtbar
- [ ] Export-Button → CSV-Download oder Toast
- [ ] Drucken-Button → Print-Dialog oder Toast

***REMOVED******REMOVED******REMOVED*** 2. Angebot erstellen (3 Min)
- [ ] Klicke "Neu" → `/sales/angebot/neu`
- [ ] Formular lädt
- [ ] Fülle 1 Feld aus (z. B. Kunde)
- [ ] Klicke "Speichern" (OK oder Toast-Meldung)

***REMOVED******REMOVED******REMOVED*** 3. Order-Flow (3 Min)
- [ ] `/sales/order` lädt
- [ ] `/sales/delivery` lädt
- [ ] `/sales/invoice` lädt
- [ ] Mind. 1 Workflow-Button sichtbar

---

***REMOVED******REMOVED*** Agrar Domain (6 Min)

***REMOVED******REMOVED******REMOVED*** 1. PSM-Liste (2 Min)
- [ ] `/agrar/psm` lädt
- [ ] Tabelle/Grid sichtbar
- [ ] Export funktioniert

***REMOVED******REMOVED******REMOVED*** 2. Saatgut (2 Min)
- [ ] `/agrar/saatgut-liste` lädt
- [ ] `/agrar/saatgut-stamm` lädt

***REMOVED******REMOVED******REMOVED*** 3. Dünger (2 Min)
- [ ] `/agrar/duenger-liste` lädt
- [ ] `/agrar/duenger/bedarfsrechner` lädt

---

***REMOVED******REMOVED*** CRM Domain (5 Min)

***REMOVED******REMOVED******REMOVED*** 1. Kontakte (2 Min)
- [ ] `/crm/kontakte-liste` lädt
- [ ] Export-Button funktioniert
- [ ] Drucken-Button funktioniert

***REMOVED******REMOVED******REMOVED*** 2. Leads (2 Min)
- [ ] `/crm/leads` lädt
- [ ] `/crm/lead/test-1` lädt (oder Leer-State)

***REMOVED******REMOVED******REMOVED*** 3. Aktivitäten (1 Min)
- [ ] `/crm/aktivitaeten` lädt

---

***REMOVED******REMOVED*** Finance Domain (6 Min)

***REMOVED******REMOVED******REMOVED*** 1. Buchungsjournal (2 Min)
- [ ] `/finance/bookings/new` lädt
- [ ] Formular sichtbar

***REMOVED******REMOVED******REMOVED*** 2. Debitoren (2 Min)
- [ ] `/fibu/debitoren` lädt
- [ ] `/fibu/offene-posten` lädt

***REMOVED******REMOVED******REMOVED*** 3. OP-Verwaltung (2 Min)
- [ ] `/fibu/op-verwaltung` lädt

---

***REMOVED******REMOVED*** Inventory Domain (5 Min)

***REMOVED******REMOVED******REMOVED*** 1. Artikel (2 Min)
- [ ] `/artikel/liste` lädt
- [ ] Export funktioniert

***REMOVED******REMOVED******REMOVED*** 2. Lager (2 Min)
- [ ] `/lager/bewegungen` lädt
- [ ] `/lager/bestand` lädt

***REMOVED******REMOVED******REMOVED*** 3. Inventory (1 Min)
- [ ] `/inventory` lädt

---

***REMOVED******REMOVED*** Ergebnis

**Gesamt:** 30 Min  
**Grün:** Alle Checks ✅  
**Rot:** Mind. 1 Check ❌ → Ticket anlegen, S2 oder höher

---

**Ausführung:**
- Manuell: Checkliste abhaken
- Automatisiert: `pnpm test:e2e:smoke`

