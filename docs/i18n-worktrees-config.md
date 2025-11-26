***REMOVED*** i18n-Integration Worktrees Configuration

***REMOVED******REMOVED*** Status-Übersicht

***REMOVED******REMOVED******REMOVED*** ✅ Abgeschlossen
- **Purchase Domain Editor-Seiten**: bestellung-anlegen, bestellung-stamm, anfrage-stamm, angebot-stamm, rechnungseingang, auftragsbestaetigung
- **Sales Domain Editor-Seiten**: invoice-editor, delivery-editor, order-editor, credit-note-editor
- **CRUD Komponenten**: CrudDeleteDialog, CrudCancelDialog
- **Contracts**: contracts-v2.tsx

***REMOVED******REMOVED******REMOVED*** 🔄 In Bearbeitung
- Keine

***REMOVED******REMOVED******REMOVED*** 📋 Ausstehend

***REMOVED******REMOVED*** Phase 1: CRM Domain Seiten (Priorität: Hoch)

***REMOVED******REMOVED******REMOVED*** 1.1 Detail-Seiten (Mask Builder / FormBuilder)
- [ ] `packages/frontend-web/src/pages/crm/kunden-stamm.tsx`
- [ ] `packages/frontend-web/src/pages/crm/kunden-stamm-modern.tsx`
- [ ] `packages/frontend-web/src/pages/crm/kontakt-detail.tsx`
- [ ] `packages/frontend-web/src/pages/crm/lead-detail.tsx`
- [ ] `packages/frontend-web/src/pages/crm/betriebsprofil-detail.tsx`
- [ ] `packages/frontend-web/src/pages/crm/aktivitaet-detail.tsx`
- [ ] `packages/frontend-web/src/pages/crm/lieferanten-stamm.tsx`

***REMOVED******REMOVED******REMOVED*** 1.2 Listen-Seiten (ListReport System)
- [ ] `packages/frontend-web/src/pages/crm/kunden-liste.tsx` ⚠️ ListReport
- [ ] `packages/frontend-web/src/pages/crm/kontakte-liste.tsx` ⚠️ ListReport
- [ ] `packages/frontend-web/src/pages/crm/betriebsprofile-liste.tsx` ⚠️ ListReport
- [ ] `packages/frontend-web/src/pages/crm/lieferanten-liste.tsx` ⚠️ ListReport

***REMOVED******REMOVED******REMOVED*** 1.3 Übersichts-Seiten
- [ ] `packages/frontend-web/src/pages/crm/leads.tsx`
- [ ] `packages/frontend-web/src/pages/crm/aktivitaeten.tsx`
- [ ] `packages/frontend-web/src/pages/crm/kontakt-management.tsx`
- [ ] `packages/frontend-web/src/pages/crm/crm-dashboard.tsx`

**Entity-Typen für CRM Domain:**
- `customer` → "Kunde" (bereits vorhanden)
- `contact` → "Kontakt" (bereits vorhanden)
- `lead` → "Lead" (bereits vorhanden)
- `supplier` → "Lieferant" (bereits vorhanden)
- `account` → "Konto" (bereits vorhanden)
- `activity` → "Aktivität" (hinzufügen)
- `businessProfile` → "Betriebsprofil" (hinzufügen)

***REMOVED******REMOVED*** Phase 2: Finance Domain Seiten (Priorität: Hoch)

***REMOVED******REMOVED******REMOVED*** 2.1 Detail-Seiten (Mask Builder / FormBuilder)
- [ ] `packages/frontend-web/src/pages/finance/kreditoren-stamm.tsx`
- [ ] `packages/frontend-web/src/pages/finance/dunning-editor.tsx`
- [ ] `packages/frontend-web/src/pages/finance/buchungserfassung.tsx`

***REMOVED******REMOVED******REMOVED*** 2.2 Listen-Seiten (ListReport System)
- [ ] `packages/frontend-web/src/pages/finance/debitoren-liste.tsx` ⚠️ ListReport

***REMOVED******REMOVED******REMOVED*** 2.3 Spezial-Seiten
- [ ] `packages/frontend-web/src/pages/finance/kasse.tsx`
- [ ] `packages/frontend-web/src/pages/finance/mahnwesen.tsx`
- [ ] `packages/frontend-web/src/pages/finance/bank-abgleich.tsx`
- [ ] `packages/frontend-web/src/pages/finance/ustva.tsx`
- [ ] `packages/frontend-web/src/pages/finance/zahlungslauf-kreditoren.tsx`
- [ ] `packages/frontend-web/src/pages/finance/lastschriften-debitoren.tsx`
- [ ] `packages/frontend-web/src/pages/finance/abschluss.tsx`
- [ ] `packages/frontend-web/src/pages/finance/chart-of-accounts.tsx`
- [ ] `packages/frontend-web/src/pages/finance/kontenplan.tsx`
- [ ] `packages/frontend-web/src/pages/finance/op-debitoren.tsx`
- [ ] `packages/frontend-web/src/pages/finance/steuerschluessel.tsx`

**Entity-Typen für Finance Domain:**
- `debtor` → "Debitor" (bereits vorhanden)
- `creditor` → "Kreditor" (bereits vorhanden)
- `payment` → "Zahlung" (bereits vorhanden)
- `dunning` → "Mahnung" (bereits vorhanden)
- `bankReconciliation` → "Bankabgleich" (bereits vorhanden)

***REMOVED******REMOVED*** Phase 3: Sales Domain Listen-Seiten (Priorität: Mittel)

***REMOVED******REMOVED******REMOVED*** 3.1 Listen-Seiten (ListReport System)
- [ ] `packages/frontend-web/src/pages/sales/rechnungen-liste.tsx` ⚠️ ListReport
- [ ] `packages/frontend-web/src/pages/sales/lieferungen-liste.tsx` ⚠️ ListReport
- [ ] `packages/frontend-web/src/pages/sales/auftraege-liste.tsx` ⚠️ ListReport
- [ ] `packages/frontend-web/src/pages/sales/angebote-liste.tsx` ⚠️ ListReport

***REMOVED******REMOVED******REMOVED*** 3.2 Weitere Sales-Seiten
- [ ] `packages/frontend-web/src/pages/sales/orders-modern.tsx`
- [ ] `packages/frontend-web/src/pages/sales/angebot-erstellen.tsx`

***REMOVED******REMOVED*** Phase 4: Purchase Domain Listen-Seiten (Priorität: Mittel)

***REMOVED******REMOVED******REMOVED*** 4.1 Listen-Seiten (ListReport System)
- [ ] `packages/frontend-web/src/pages/einkauf/bestellungen-liste.tsx` ⚠️ ListReport
- [ ] `packages/frontend-web/src/pages/einkauf/angebote-liste.tsx` ⚠️ ListReport
- [ ] `packages/frontend-web/src/pages/einkauf/anfragen-liste.tsx` ⚠️ ListReport
- [ ] `packages/frontend-web/src/pages/einkauf/rechnungseingaenge-liste.tsx` ⚠️ ListReport
- [ ] `packages/frontend-web/src/pages/einkauf/auftragsbestaetigungen-liste.tsx` ⚠️ ListReport
- [ ] `packages/frontend-web/src/pages/einkauf/lieferanten-liste.tsx` ⚠️ ListReport
- [ ] `packages/frontend-web/src/pages/einkauf/anlieferavis-liste.tsx` ⚠️ ListReport

***REMOVED******REMOVED*** Phase 5: ListReport System Erweiterung (Priorität: Hoch)

***REMOVED******REMOVED******REMOVED*** 5.1 System-Erweiterung
- [ ] `packages/frontend-web/src/components/patterns/ListReport.tsx` - i18n-Unterstützung hinzufügen
- [ ] `packages/frontend-web/src/components/mask-builder/ListReport.tsx` - i18n-Unterstützung hinzufügen

**Anforderungen:**
- `useTranslation` Hook in ListReport-Komponente integrieren
- Konfiguration dynamisch über i18n laden
- Spalten-Header übersetzen
- Filter-Labels übersetzen
- Aktionen übersetzen

**Betroffene Seiten:**
- Alle `*-liste.tsx` Dateien in CRM, Finance, Sales, Purchase Domains

***REMOVED******REMOVED*** Phase 6: Validierung und Abschluss (Priorität: Hoch)

***REMOVED******REMOVED******REMOVED*** 6.1 Übersetzungs-Vollständigkeit
- [ ] Alle verwendeten Übersetzungsschlüssel in `translation.json` vorhanden?
- [ ] Keine hardcoded deutschen Texte mehr in migrierten Komponenten?
- [ ] Alle Entity-Typen übersetzt?
- [ ] Alle Status-Werte übersetzt?
- [ ] Alle Aktionen übersetzt?
- [ ] Alle Feld-Labels übersetzt?

***REMOVED******REMOVED******REMOVED*** 6.2 Code-Qualität
- [ ] TypeScript-Fehler prüfen
- [ ] ESLint-Warnungen beheben
- [ ] Konsistenz der i18n-Verwendung sicherstellen
- [ ] Alle Komponenten getestet

***REMOVED******REMOVED******REMOVED*** 6.3 Dokumentation
- [ ] i18n-integration.md aktualisieren
- [ ] Migration-Status aktualisieren
- [ ] Best Practices dokumentieren

***REMOVED******REMOVED*** Migrations-Checkliste pro Seite

Für jede zu migrierende Seite:

- [ ] `useTranslation` Hook hinzugefügt
- [ ] `getEntityTypeLabel` importiert und verwendet
- [ ] Entity-Typ definiert (`const entityType = '...'`)
- [ ] Alle hardcoded deutschen Texte durch `t()` ersetzt
- [ ] Feld-Labels über `t('crud.fields.*')` geladen
- [ ] Aktionen über `t('crud.actions.*')` geladen
- [ ] Status-Labels über `getStatusLabel()` geladen
- [ ] Titel über `getListTitle()` / `getDetailTitle()` geladen
- [ ] Fehlende Übersetzungen in `translation.json` hinzugefügt
- [ ] Linter-Fehler behoben
- [ ] Komponente getestet

***REMOVED******REMOVED*** Prioritäten-Matrix

***REMOVED******REMOVED******REMOVED*** 🔴 Kritisch (sofort)
1. ListReport System Erweiterung (blockiert viele Listen-Seiten)
2. CRM Detail-Seiten (häufig genutzt)
3. Finance Detail-Seiten (häufig genutzt)

***REMOVED******REMOVED******REMOVED*** 🟡 Wichtig (nächste Woche)
4. CRM Listen-Seiten (nach ListReport-Erweiterung)
5. Finance Listen-Seiten (nach ListReport-Erweiterung)
6. Sales Listen-Seiten (nach ListReport-Erweiterung)
7. Purchase Listen-Seiten (nach ListReport-Erweiterung)

***REMOVED******REMOVED******REMOVED*** 🟢 Optional (später)
8. Übersichts-Seiten (Dashboard, etc.)
9. Spezial-Seiten (Bank-Abgleich, UStVA, etc.)

***REMOVED******REMOVED*** Technische Notizen

***REMOVED******REMOVED******REMOVED*** Mask Builder System
- Konfiguration muss in Komponente verschoben werden, um `useTranslation` zu nutzen
- Schema-Validierung muss mit `t()` erstellt werden
- Pattern: `createConfig(t, entityTypeLabel)` Funktion

***REMOVED******REMOVED******REMOVED*** FormBuilder System
- Verwendet JSON-Schemas aus `domain-schemas/`
- Hardcoded Texte in Toast-Nachrichten und Labels
- Pattern: `useTranslation` + `getEntityTypeLabel` + `getSuccessMessage`

***REMOVED******REMOVED******REMOVED*** ListReport System
- Externe Konfiguration macht i18n schwierig
- Lösung: System erweitern oder Konfiguration in Komponente verschieben
- Pattern: Noch zu definieren

***REMOVED******REMOVED*** Fortschritt-Tracking

***REMOVED******REMOVED******REMOVED*** Gesamt-Statistik
- **Gesamt Seiten**: ~60
- **Abgeschlossen**: 10
- **In Bearbeitung**: 0
- **Ausstehend**: ~50
- **Fortschritt**: ~17%

***REMOVED******REMOVED******REMOVED*** Domain-Statistik
- **Purchase**: 6/13 (46%)
- **Sales**: 4/10 (40%)
- **CRM**: 0/14 (0%)
- **Finance**: 0/13 (0%)

***REMOVED******REMOVED*** Nächste Schritte

1. **ListReport System erweitern** (blockiert viele Seiten)
2. **CRM Detail-Seiten migrieren** (kunden-stamm, kontakt-detail, etc.)
3. **Finance Detail-Seiten migrieren** (kreditoren-stamm, dunning-editor, etc.)
4. **Listen-Seiten migrieren** (nach ListReport-Erweiterung)
5. **Validierung durchführen**

