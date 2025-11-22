***REMOVED*** i18n Quick Reference

***REMOVED******REMOVED*** Schnellstart

***REMOVED******REMOVED******REMOVED*** 1. Imports
```typescript
import { useTranslation } from 'react-i18next';
import { getEntityTypeLabel, getFieldLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers';
```

***REMOVED******REMOVED******REMOVED*** 2. Hook initialisieren
```typescript
const { t } = useTranslation();
const entityType = 'farmer';
const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Farmer');
```

***REMOVED******REMOVED******REMOVED*** 3. Häufig verwendete Übersetzungen

***REMOVED******REMOVED******REMOVED******REMOVED*** Entity-Typ
```typescript
const entityTypeLabel = getEntityTypeLabel(t, 'farmer', 'Farmer');
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Felder
```typescript
t('crud.fields.name')        // "Name"
t('crud.fields.status')       // "Status"
t('crud.fields.type')        // "Typ"
t('crud.fields.date')        // "Datum"
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Aktionen
```typescript
t('crud.actions.create')     // "Erstellen"
t('crud.actions.edit')       // "Bearbeiten"
t('crud.actions.delete')     // "Löschen"
t('crud.actions.cancel')     // "Stornieren"
t('crud.actions.save')       // "Speichern"
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Status
```typescript
getStatusLabel(t, 'ACTIVE', 'Active')    // "Aktiv"
getStatusLabel(t, 'PENDING', 'Pending')  // "Ausstehend"
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Nachrichten
```typescript
getSuccessMessage(t, 'create', 'farmer')  // "Farmer erfolgreich erstellt"
getErrorMessage(t, 'delete', 'contract')  // "Fehler beim Löschen von Vertrag"
```

***REMOVED******REMOVED*** Komponenten-Patterns

***REMOVED******REMOVED******REMOVED*** CRUD-Dialog
```typescript
<CrudDeleteDialog
  entityType={entityTypeLabel}  // Übersetzt!
  entityName={entity.name}
  // ...
/>
```

***REMOVED******REMOVED******REMOVED*** Tabellen-Header
```typescript
<TableHead>{t('crud.fields.name')}</TableHead>
<TableHead>{t('crud.fields.status')}</TableHead>
```

***REMOVED******REMOVED******REMOVED*** Buttons
```typescript
<Button>{t('crud.actions.create')}</Button>
<Button>{t('crud.actions.edit')}</Button>
<Button>{t('crud.actions.delete')}</Button>
```

***REMOVED******REMOVED******REMOVED*** Titel
```typescript
<h2>{entityTypeLabel}</h2>
<h2>{getListTitle(t, entityTypeLabel)}</h2>
<h2>{getDetailTitle(t, entityTypeLabel, entity.name)}</h2>
```

***REMOVED******REMOVED*** Neue Übersetzungen hinzufügen

***REMOVED******REMOVED******REMOVED*** 1. In `translation.json`:
```json
{
  "crud": {
    "entities": {
      "myEntity": "Meine Entität"
    },
    "fields": {
      "myField": "Mein Feld"
    }
  }
}
```

***REMOVED******REMOVED******REMOVED*** 2. In Komponente verwenden:
```typescript
const entityTypeLabel = getEntityTypeLabel(t, 'myEntity', 'My Entity');
<TableHead>{t('crud.fields.myField')}</TableHead>
```

***REMOVED******REMOVED*** Wichtige Regeln

1. ✅ **Immer** `getEntityTypeLabel()` für Entity-Typen verwenden
2. ✅ **Immer** `t('crud.fields.*')` für Feld-Labels verwenden
3. ✅ **Immer** `t('crud.actions.*')` für Aktionen verwenden
4. ✅ **Immer** `getStatusLabel()` für Status-Werte verwenden
5. ❌ **Nie** hardcoded deutsche Texte verwenden
6. ❌ **Nie** Entity-Typ direkt als String übergeben (außer als Fallback)

***REMOVED******REMOVED*** Vollständige Dokumentation

Siehe [i18n-integration.md](./i18n-integration.md) für vollständige Dokumentation.

