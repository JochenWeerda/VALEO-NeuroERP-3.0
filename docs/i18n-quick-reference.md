# i18n Quick Reference

## Schnellstart

### 1. Imports
```typescript
import { useTranslation } from 'react-i18next';
import { getEntityTypeLabel, getFieldLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers';
```

### 2. Hook initialisieren
```typescript
const { t } = useTranslation();
const entityType = 'farmer';
const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Farmer');
```

### 3. Häufig verwendete Übersetzungen

#### Entity-Typ
```typescript
const entityTypeLabel = getEntityTypeLabel(t, 'farmer', 'Farmer');
```

#### Felder
```typescript
t('crud.fields.name')        // "Name"
t('crud.fields.status')       // "Status"
t('crud.fields.type')        // "Typ"
t('crud.fields.date')        // "Datum"
```

#### Aktionen
```typescript
t('crud.actions.create')     // "Erstellen"
t('crud.actions.edit')       // "Bearbeiten"
t('crud.actions.delete')     // "Löschen"
t('crud.actions.cancel')     // "Stornieren"
t('crud.actions.save')       // "Speichern"
```

#### Status
```typescript
getStatusLabel(t, 'ACTIVE', 'Active')    // "Aktiv"
getStatusLabel(t, 'PENDING', 'Pending')  // "Ausstehend"
```

#### Nachrichten
```typescript
getSuccessMessage(t, 'create', 'farmer')  // "Farmer erfolgreich erstellt"
getErrorMessage(t, 'delete', 'contract')  // "Fehler beim Löschen von Vertrag"
```

## Komponenten-Patterns

### CRUD-Dialog
```typescript
<CrudDeleteDialog
  entityType={entityTypeLabel}  // Übersetzt!
  entityName={entity.name}
  // ...
/>
```

### Tabellen-Header
```typescript
<TableHead>{t('crud.fields.name')}</TableHead>
<TableHead>{t('crud.fields.status')}</TableHead>
```

### Buttons
```typescript
<Button>{t('crud.actions.create')}</Button>
<Button>{t('crud.actions.edit')}</Button>
<Button>{t('crud.actions.delete')}</Button>
```

### Titel
```typescript
<h2>{entityTypeLabel}</h2>
<h2>{getListTitle(t, entityTypeLabel)}</h2>
<h2>{getDetailTitle(t, entityTypeLabel, entity.name)}</h2>
```

## Neue Übersetzungen hinzufügen

### 1. In `translation.json`:
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

### 2. In Komponente verwenden:
```typescript
const entityTypeLabel = getEntityTypeLabel(t, 'myEntity', 'My Entity');
<TableHead>{t('crud.fields.myField')}</TableHead>
```

## Wichtige Regeln

1. ✅ **Immer** `getEntityTypeLabel()` für Entity-Typen verwenden
2. ✅ **Immer** `t('crud.fields.*')` für Feld-Labels verwenden
3. ✅ **Immer** `t('crud.actions.*')` für Aktionen verwenden
4. ✅ **Immer** `getStatusLabel()` für Status-Werte verwenden
5. ❌ **Nie** hardcoded deutsche Texte verwenden
6. ❌ **Nie** Entity-Typ direkt als String übergeben (außer als Fallback)

## Vollständige Dokumentation

Siehe [i18n-integration.md](./i18n-integration.md) für vollständige Dokumentation.

