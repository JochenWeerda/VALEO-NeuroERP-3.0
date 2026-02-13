# i18n Migration Status

## Übersicht

Dieses Dokument zeigt den aktuellen Status der i18n-Migration für alle Domains.

## ✅ Vollständig migriert

### Agribusiness Domain
- ✅ `pages/agribusiness/farmers.tsx`
- ✅ `pages/agribusiness/field-service-tasks.tsx`

### Contracts Domain
- ✅ `pages/contracts-v2.tsx`

### Sales Domain
- ✅ `pages/sales/angebote-liste.tsx`

## 🔄 In Bearbeitung

### Sales Domain
- ⏳ `pages/sales/invoice-editor.tsx`
- ⏳ `pages/sales/delivery-editor.tsx`
- ⏳ `pages/sales/credit-note-editor.tsx`
- ⏳ `pages/sales/orders-modern.tsx`
- ⏳ `pages/sales/order-editor.tsx`
- ⏳ `pages/sales/rechnungen-liste.tsx`
- ⏳ `pages/sales/lieferungen-liste.tsx`
- ⏳ `pages/sales/auftraege-liste.tsx`

### CRM Domain
- ⏳ `pages/crm/kunden-liste.tsx` (verwendet ListReport)
- ⏳ `pages/crm/kunden-stamm.tsx`
- ⏳ `pages/crm/kontakte-liste.tsx`
- ⏳ `pages/crm/kontakt-detail.tsx`
- ⏳ `pages/crm/leads.tsx`
- ⏳ `pages/crm/lead-detail.tsx`
- ⏳ `pages/crm/betriebsprofile-liste.tsx`
- ⏳ `pages/crm/betriebsprofil-detail.tsx`
- ⏳ `pages/crm/aktivitaeten.tsx`
- ⏳ `pages/crm/aktivitaet-detail.tsx`

### Finance Domain
- ⏳ `pages/finance/debitoren-liste.tsx`
- ⏳ `pages/finance/kreditoren-stamm.tsx`
- ⏳ `pages/finance/kasse.tsx`
- ⏳ `pages/finance/mahnwesen.tsx`
- ⏳ `pages/finance/dunning-editor.tsx`
- ⏳ `pages/finance/bank-abgleich.tsx`
- ⏳ `pages/finance/ustva.tsx`
- ⏳ `pages/finance/zahlungslauf-kreditoren.tsx`
- ⏳ `pages/finance/lastschriften-debitoren.tsx`
- ⏳ `pages/finance/buchungserfassung.tsx`

### Purchase/Einkauf Domain
- ⏳ `pages/einkauf/bestellungen-liste.tsx` (verwendet ListReport)
- ⏳ `pages/einkauf/bestellung-anlegen.tsx`
- ⏳ `pages/einkauf/bestellung-stamm.tsx`
- ⏳ `pages/einkauf/angebote-liste.tsx`
- ⏳ `pages/einkauf/angebot-stamm.tsx`
- ⏳ `pages/einkauf/anfragen-liste.tsx`
- ⏳ `pages/einkauf/anfrage-stamm.tsx`
- ⏳ `pages/einkauf/rechnungseingaenge-liste.tsx`
- ⏳ `pages/einkauf/rechnungseingang.tsx`
- ⏳ `pages/einkauf/auftragsbestaetigungen-liste.tsx`
- ⏳ `pages/einkauf/auftragsbestaetigung.tsx`

### Inventory Domain
- ⏳ `pages/inventory/epcis/index.tsx`
- ⏳ `pages/inventory-dashboard.tsx`
- ⏳ `pages/inventory-reports.tsx`
- ⏳ `pages/stock-management.tsx`

### Weitere Domains
- ⏳ Futtermittel Domain
- ⏳ Agrar Domain
- ⏳ Quality Domain
- ⏳ Weitere Domains

## 📋 Migration-Priorität

### Phase 1: Kern-Domains (Höchste Priorität)
1. **Sales Domain** - Verkaufsprozesse
2. **CRM Domain** - Kundenbeziehungen
3. **Finance Domain** - Finanzprozesse
4. **Purchase Domain** - Einkaufsprozesse

### Phase 2: Unterstützende Domains
5. **Inventory Domain** - Lagerverwaltung
6. **Agribusiness Domain** - Landwirtschaft (teilweise fertig)

### Phase 3: Spezialisierte Domains
7. **Futtermittel Domain**
8. **Agrar Domain**
9. **Quality Domain**
10. **Weitere Domains**

## 🔧 Technische Herausforderungen

### ListReport System
Viele Seiten verwenden das `ListReport` Komponenten-System, das eine Konfiguration außerhalb der React-Komponente hat. Für diese Seiten ist eine Erweiterung des ListReport-Systems erforderlich, um i18n zu unterstützen.

**Lösungsansatz:**
1. ListReport-Komponente erweitern, um i18n zu unterstützen
2. Konfiguration dynamisch über i18n laden
3. Oder: Konfiguration in die Komponente verschieben

### Mask Builder System
Einige Seiten verwenden das `mask-builder` System, das ebenfalls eine Erweiterung benötigt.

## 📊 Statistiken

- **Vollständig migriert:** 4 Seiten
- **In Bearbeitung:** ~100+ Seiten
- **Geschätzte Gesamtanzahl:** ~150+ Seiten

## 🎯 Nächste Schritte

1. **ListReport i18n-Erweiterung:** System erweitern, um i18n zu unterstützen
2. **Weitere Sales-Seiten:** Invoice, Delivery, Order Editor migrieren
3. **CRM-Seiten:** Kunden- und Kontakt-Seiten migrieren
4. **Finance-Seiten:** Debitoren/Kreditoren-Seiten migrieren
5. **Purchase-Seiten:** Bestellungen-Seiten migrieren

## 📚 Referenzen

- [i18n Integration Dokumentation](./i18n-integration.md)
- [i18n Quick Reference](./i18n-quick-reference.md)
- [i18n Migration Guide](./i18n-migration-guide.md)


