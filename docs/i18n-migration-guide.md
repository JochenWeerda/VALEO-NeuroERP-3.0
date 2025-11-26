# i18n Migration Guide für weitere Domains

## Übersicht

Dieser Guide beschreibt, wie bestehende Frontend-Seiten auf i18n umgestellt werden können. Die Migration folgt einem konsistenten Pattern, das bereits für die Agribusiness- und Contracts-Domains implementiert wurde.

## Migration-Pattern

### Schritt 1: Imports hinzufügen

```typescript
import { useTranslation } from 'react-i18next';
import { 
  getEntityTypeLabel, 
  getFieldLabel, 
  getStatusLabel,
  getListTitle,
  getDetailTitle 
} from '@/features/crud/utils/i18n-helpers';
```

### Schritt 2: Hook initialisieren

```typescript
export default function MyEntityPage(): JSX.Element {
  const { t } = useTranslation();
  const entityType = 'myEntity';
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'My Entity');
  
  // ... rest of component
}
```

### Schritt 3: Hardcoded Texte ersetzen

#### Entity-Typ-Namen
```typescript
// ❌ Vorher
<h1>Angebote</h1>

// ✅ Nachher
<h1>{entityTypeLabel}</h1>
```

#### Feld-Labels
```typescript
// ❌ Vorher
<TableHead>Status</TableHead>
<TableHead>Datum</TableHead>

// ✅ Nachher
<TableHead>{t('crud.fields.status')}</TableHead>
<TableHead>{t('crud.fields.date')}</TableHead>
```

#### Aktionen
```typescript
// ❌ Vorher
<Button>Löschen</Button>
<Button>Bearbeiten</Button>
<Button>Erstellen</Button>

// ✅ Nachher
<Button>{t('crud.actions.delete')}</Button>
<Button>{t('crud.actions.edit')}</Button>
<Button>{t('crud.actions.create')}</Button>
```

#### Status-Labels
```typescript
// ❌ Vorher
const statusLabels = {
  'offen': 'Offen',
  'angenommen': 'Angenommen'
}

// ✅ Nachher
const statusLabels = {
  'offen': getStatusLabel(t, 'offen', 'Offen'),
  'angenommen': getStatusLabel(t, 'angenommen', 'Angenommen')
}
```

#### Titel
```typescript
// ❌ Vorher
<h1>Angebote Liste</h1>
<h2>Angebot: {angebot.nummer}</h2>

// ✅ Nachher
<h1>{getListTitle(t, entityTypeLabel)}</h1>
<h2>{getDetailTitle(t, entityTypeLabel, angebot.nummer)}</h2>
```

### Schritt 4: Übersetzungen hinzufügen

In `packages/frontend-web/src/i18n/locales/de/translation.json`:

```json
{
  "crud": {
    "entities": {
      "myEntity": "Meine Entität"
    },
    "fields": {
      "myField": "Mein Feld"
    }
  },
  "status": {
    "myStatus": "Mein Status"
  }
}
```

## Domain-spezifische Migration

### Sales Domain

**Bereits migriert:**
- ✅ `pages/sales/angebote-liste.tsx`

**Noch zu migrieren:**
- `pages/sales/invoice-editor.tsx`
- `pages/sales/delivery-editor.tsx`
- `pages/sales/credit-note-editor.tsx`
- `pages/sales/orders-modern.tsx`
- `pages/sales/order-editor.tsx`
- `pages/sales/rechnungen-liste.tsx`
- `pages/sales/lieferungen-liste.tsx`
- `pages/sales/auftraege-liste.tsx`

**Entity-Typen für Sales:**
- `offer` → "Angebot"
- `order` → "Auftrag"
- `invoice` → "Rechnung"
- `delivery` → "Lieferung"
- `creditNote` → "Gutschrift"

### CRM Domain

**Noch zu migrieren:**
- `pages/crm/kunden-liste.tsx`
- `pages/crm/kunden-stamm.tsx`
- `pages/crm/kontakte-liste.tsx`
- `pages/crm/kontakt-detail.tsx`
- `pages/crm/leads.tsx`
- `pages/crm/lead-detail.tsx`
- `pages/crm/betriebsprofile-liste.tsx`
- `pages/crm/betriebsprofil-detail.tsx`
- `pages/crm/aktivitaeten.tsx`
- `pages/crm/aktivitaet-detail.tsx`

**Entity-Typen für CRM:**
- `customer` → "Kunde"
- `contact` → "Kontakt"
- `lead` → "Lead"
- `account` → "Konto"
- `activity` → "Aktivität"

### Finance Domain

**Noch zu migrieren:**
- `pages/finance/debitoren-liste.tsx`
- `pages/finance/kreditoren-stamm.tsx`
- `pages/finance/kasse.tsx`
- `pages/finance/mahnwesen.tsx`
- `pages/finance/dunning-editor.tsx`
- `pages/finance/bank-abgleich.tsx`
- `pages/finance/ustva.tsx`
- `pages/finance/zahlungslauf-kreditoren.tsx`
- `pages/finance/lastschriften-debitoren.tsx`
- `pages/finance/buchungserfassung.tsx`

**Entity-Typen für Finance:**
- `debtor` → "Debitor"
- `creditor` → "Kreditor"
- `payment` → "Zahlung"
- `dunning` → "Mahnung"
- `bankReconciliation` → "Bankabgleich"

### Purchase/Einkauf Domain

**Noch zu migrieren:**
- `pages/einkauf/bestellungen-liste.tsx`
- `pages/einkauf/bestellung-anlegen.tsx`
- `pages/einkauf/bestellung-stamm.tsx`
- `pages/einkauf/angebote-liste.tsx`
- `pages/einkauf/angebot-stamm.tsx`
- `pages/einkauf/anfragen-liste.tsx`
- `pages/einkauf/anfrage-stamm.tsx`
- `pages/einkauf/rechnungseingaenge-liste.tsx`
- `pages/einkauf/rechnungseingang.tsx`
- `pages/einkauf/auftragsbestaetigungen-liste.tsx`
- `pages/einkauf/auftragsbestaetigung.tsx`

**Entity-Typen für Purchase:**
- `purchaseOrder` → "Kaufauftrag"
- `purchaseOffer` → "Einkaufsangebot"
- `purchaseRequest` → "Anfrage"
- `invoiceReceipt` → "Rechnungseingang"
- `orderConfirmation` → "Auftragsbestätigung"

### Inventory Domain

**Noch zu migrieren:**
- `pages/inventory/epcis/index.tsx`
- `pages/inventory-dashboard.tsx`
- `pages/inventory-reports.tsx`
- `pages/stock-management.tsx`

**Entity-Typen für Inventory:**
- `warehouse` → "Lager"
- `location` → "Standort"
- `product` → "Produkt"
- `stock` → "Bestand"

## Checkliste für Migration

- [ ] Imports hinzugefügt (`useTranslation`, Helper-Funktionen)
- [ ] Hook initialisiert (`const { t } = useTranslation()`)
- [ ] Entity-Typ definiert (`const entityType = '...'`)
- [ ] Entity-Typ-Label geladen (`getEntityTypeLabel()`)
- [ ] Alle hardcoded deutschen Texte ersetzt
- [ ] Feld-Labels über `t('crud.fields.*')` geladen
- [ ] Aktionen über `t('crud.actions.*')` geladen
- [ ] Status-Labels über `getStatusLabel()` geladen
- [ ] Titel über `getListTitle()` / `getDetailTitle()` geladen
- [ ] Übersetzungen in `translation.json` hinzugefügt
- [ ] Linter-Fehler behoben
- [ ] Komponente getestet

## Häufige Fehler

### 1. Entity-Typ nicht übersetzt
```typescript
// ❌ Falsch
<CrudDeleteDialog entityType="Farmer" />

// ✅ Richtig
<CrudDeleteDialog entityType={entityTypeLabel} />
```

### 2. Status nicht übersetzt
```typescript
// ❌ Falsch
<Badge>{status}</Badge>

// ✅ Richtig
<Badge>{getStatusLabel(t, status, status)}</Badge>
```

### 3. Fehlende Übersetzung
```typescript
// ❌ Falsch - Übersetzung fehlt in translation.json
t('crud.fields.myNewField')

// ✅ Richtig - Übersetzung hinzufügen
// In translation.json:
{
  "crud": {
    "fields": {
      "myNewField": "Mein neues Feld"
    }
  }
}
```

## Automatisierung

Für große Migrationen können Sie ein Skript verwenden, um häufig verwendete Patterns zu finden:

```bash
# Finde alle hardcoded deutschen Texte
grep -r "Löschen\|Bearbeiten\|Erstellen\|Status\|Datum\|Name" packages/frontend-web/src/pages/
```

## Nächste Schritte

1. **Priorisierung:** Wichtige Domains zuerst (Sales, CRM, Finance)
2. **Schrittweise Migration:** Eine Domain nach der anderen
3. **Testing:** Nach jeder Migration testen
4. **Dokumentation:** Migrierte Seiten dokumentieren

## Referenzen

- [i18n Integration Dokumentation](./i18n-integration.md)
- [i18n Quick Reference](./i18n-quick-reference.md)

