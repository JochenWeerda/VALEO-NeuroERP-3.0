# i18n-Integration Dokumentation

## Übersicht

Diese Dokumentation beschreibt die vollständige Integration von i18n (Internationalisierung) in das CRUD-Framework basierend auf Odoo 19.0 deutschen Übersetzungen. Alle CRUD-Komponenten und Frontend-Seiten wurden auf i18n umgestellt, um eine konsistente und wartbare Übersetzungsstruktur zu gewährleisten.

## Änderungsübersicht

### 1. Übersetzungsdateien

#### `packages/frontend-web/src/i18n/locales/de/translation.json`
**Status:** Erweitert

Vollständige deutsche Übersetzungen für alle CRUD-Operationen:

- **`crud.actions`** - Aktionen (Erstellen, Bearbeiten, Löschen, Stornieren, etc.)
- **`crud.dialogs`** - Dialog-Texte (Delete, Cancel, Amend)
- **`crud.fields`** - Feld-Labels (Name, Status, Typ, etc.)
- **`crud.messages`** - Erfolgs- und Fehlermeldungen
- **`crud.audit`** - Audit-Trail Texte
- **`crud.print`** - Druck/Export-Texte
- **`crud.entities`** - Entity-Typ-Namen (Farmer, Contract, Task, etc.)
- **`crud.list`** - Listen-Ansicht Texte
- **`crud.detail`** - Detail-Ansicht Texte

### 2. CRUD-Komponenten (i18n-Integration)

#### `packages/frontend-web/src/features/crud/components/CrudDeleteDialog.tsx`
**Status:** Umgestellt auf i18n

**Änderungen:**
- `useTranslation` Hook hinzugefügt
- Alle hardcoded deutschen Texte durch `t()` Aufrufe ersetzt
- Entity-Typ-Übersetzung über `getEntityTypeLabel()` Helper

**Verwendete Übersetzungsschlüssel:**
- `crud.dialogs.delete.title`
- `crud.dialogs.delete.description`
- `crud.dialogs.delete.descriptionGeneric`
- `crud.dialogs.delete.warning`
- `crud.dialogs.delete.reasonRequired`
- `crud.dialogs.delete.reasonPlaceholder`
- `crud.dialogs.delete.reasonMinLength`
- `crud.dialogs.delete.confirmButton`
- `crud.dialogs.delete.cancelButton`
- `crud.dialogs.delete.confirming`
- `crud.dialogs.delete.errorRequired`
- `crud.dialogs.delete.errorMinLength`

#### `packages/frontend-web/src/features/crud/components/CrudCancelDialog.tsx`
**Status:** Umgestellt auf i18n

**Änderungen:**
- `useTranslation` Hook hinzugefügt
- Alle hardcoded deutschen Texte durch `t()` Aufrufe ersetzt
- Entity-Typ-Übersetzung über `getEntityTypeLabel()` Helper

**Verwendete Übersetzungsschlüssel:**
- `crud.dialogs.cancel.title`
- `crud.dialogs.cancel.description`
- `crud.dialogs.cancel.descriptionGeneric`
- `crud.dialogs.cancel.warning`
- `crud.dialogs.cancel.reasonRequired`
- `crud.dialogs.cancel.reasonPlaceholder`
- `crud.dialogs.cancel.reasonMinLength`
- `crud.dialogs.cancel.confirmButton`
- `crud.dialogs.cancel.cancelButton`
- `crud.dialogs.cancel.confirming`
- `crud.dialogs.cancel.errorRequired`
- `crud.dialogs.cancel.errorMinLength`

#### `packages/frontend-web/src/features/crud/components/CrudAuditTrailPanel.tsx`
**Status:** Umgestellt auf i18n

**Änderungen:**
- `useTranslation` Hook hinzugefügt
- Action-Labels dynamisch über `getActionLabel()` geladen
- Alle Tabellen-Header und Texte über i18n

**Verwendete Übersetzungsschlüssel:**
- `crud.audit.title`
- `crud.audit.loading`
- `crud.audit.noChanges`
- `crud.audit.timestamp`
- `crud.audit.action`
- `crud.audit.user`
- `crud.audit.changedFields`
- `crud.audit.reason`
- `crud.audit.actions.*` (create, update, delete, cancel, amend, restore)

#### `packages/frontend-web/src/features/crud/components/CrudPrintButton.tsx`
**Status:** Umgestellt auf i18n

**Änderungen:**
- `useTranslation` Hook hinzugefügt
- Alle Button-Texte und Fehlermeldungen über i18n

**Verwendete Übersetzungsschlüssel:**
- `crud.print.export`
- `crud.print.exporting`
- `crud.print.exportAsPDF`
- `crud.print.exportAsExcel`
- `crud.print.errorPDF`
- `crud.print.errorExcel`

### 3. i18n Helper-Funktionen

#### `packages/frontend-web/src/features/crud/utils/i18n-helpers.ts`
**Status:** Neu erstellt

**Funktionen:**

1. **`getEntityTypeLabel(t, entityType, fallback?)`**
   - Übersetzt Entity-Typ-Namen
   - Verwendet `crud.entities.*` Namespace
   - Fallback auf übergebenen Wert oder Original

2. **`getFieldLabel(t, fieldName, fallback?)`**
   - Übersetzt Feld-Namen
   - Verwendet `crud.fields.*` Namespace
   - Automatische Formatierung bei fehlender Übersetzung

3. **`getActionLabel(t, action, fallback?)`**
   - Übersetzt Aktionen (create, update, delete, etc.)
   - Verwendet `crud.actions.*` Namespace

4. **`getStatusLabel(t, status, fallback?)`**
   - Übersetzt Status-Werte
   - Verwendet `status.*` Namespace

5. **`getSuccessMessage(t, operation, entityType)`**
   - Generiert Erfolgsmeldungen für CRUD-Operationen
   - Verwendet `crud.messages.*Success` Pattern

6. **`getErrorMessage(t, operation, entityType)`**
   - Generiert Fehlermeldungen für CRUD-Operationen
   - Verwendet `crud.messages.*Error` Pattern

7. **`getListTitle(t, entityType)`**
   - Generiert Listen-Titel
   - Verwendet `crud.list.title` Template

8. **`getDetailTitle(t, entityType, entityName)`**
   - Generiert Detail-Titel
   - Verwendet `crud.detail.title` Template

9. **`getEntityTypeKey(entity)`**
   - Extrahiert Entity-Typ-Schlüssel aus Entity-Objekten
   - Unterstützt verschiedene Entity-Strukturen

#### `packages/frontend-web/src/features/crud/utils/index.ts`
**Status:** Neu erstellt

Exportiert alle i18n Helper-Funktionen für einfachen Import.

### 4. Frontend-Seiten (i18n-Integration)

#### `packages/frontend-web/src/pages/agribusiness/farmers.tsx`
**Status:** Vollständig auf i18n umgestellt

**Änderungen:**
- `useTranslation` Hook hinzugefügt
- Entity-Typ über `getEntityTypeLabel()` geladen
- Alle UI-Texte über i18n
- Tabellen-Header über `t('crud.fields.*')`
- Button-Texte über `t('crud.actions.*')`
- Listen-Titel über `getListTitle()`
- Detail-Titel über `getDetailTitle()`

**Verwendete Patterns:**
```typescript
const { t } = useTranslation();
const entityType = 'farmer';
const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Farmer');

// Tabellen-Header
<TableHead>{t('crud.fields.name')}</TableHead>

// Button-Texte
<Button>{t('crud.actions.edit')}</Button>

// Titel
<h2>{entityTypeLabel}</h2>
```

#### `packages/frontend-web/src/pages/agribusiness/field-service-tasks.tsx`
**Status:** Vollständig auf i18n umgestellt

**Änderungen:**
- Gleiche Patterns wie `farmers.tsx`
- Status-Labels über `getStatusLabel()` übersetzt
- Entity-Typ: `fieldServiceTask`

#### `packages/frontend-web/src/pages/contracts-v2.tsx`
**Status:** Vollständig auf i18n umgestellt

**Änderungen:**
- Gleiche Patterns wie andere Seiten
- Amendment-Dialog vollständig auf i18n umgestellt
- Entity-Typ: `contract`
- Amendment-spezifische Übersetzungen verwendet

## Verwendungsbeispiele

### 1. Neue CRUD-Komponente erstellen

```typescript
import React from 'react';
import { useTranslation } from 'react-i18next';
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers';

export function MyCrudComponent({ entityType }: Props) {
  const { t } = useTranslation();
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'MyEntity');

  return (
    <div>
      <h2>{entityTypeLabel}</h2>
      <button>{t('crud.actions.create')}</button>
      <button>{t('crud.actions.edit')}</button>
      <button>{t('crud.actions.delete')}</button>
    </div>
  );
}
```

### 2. Neue Frontend-Seite erstellen

```typescript
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  getEntityTypeLabel, 
  getListTitle, 
  getDetailTitle,
  getFieldLabel 
} from '@/features/crud/utils/i18n-helpers';
import { CrudDeleteDialog } from '@/features/crud/components';

export default function MyEntityPage() {
  const { t } = useTranslation();
  const entityType = 'myEntity';
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'My Entity');

  return (
    <div>
      <h2>{entityTypeLabel}</h2>
      <table>
        <thead>
          <tr>
            <th>{t('crud.fields.name')}</th>
            <th>{t('crud.fields.status')}</th>
          </tr>
        </thead>
      </table>
      
      <CrudDeleteDialog
        entityType={entityTypeLabel}
        // ... andere Props
      />
    </div>
  );
}
```

### 3. Neue Übersetzungen hinzufügen

In `packages/frontend-web/src/i18n/locales/de/translation.json`:

```json
{
  "crud": {
    "entities": {
      "myEntity": "Meine Entität"
    },
    "fields": {
      "myCustomField": "Mein benutzerdefiniertes Feld"
    },
    "actions": {
      "myCustomAction": "Meine benutzerdefinierte Aktion"
    }
  }
}
```

### 4. Entity-spezifische Übersetzungen

Für Entity-spezifische Übersetzungen können Sie den Entity-Namen im Schlüssel verwenden:

```json
{
  "crud": {
    "entities": {
      "farmer": "Farmer",
      "contract": "Vertrag"
    },
    "dialogs": {
      "delete": {
        "title": "{{entityType}} löschen",
        "description": "Möchten Sie wirklich {{entityName}} löschen?"
      }
    }
  }
}
```

Verwendung:
```typescript
t('crud.dialogs.delete.title', { entityType: entityTypeLabel })
t('crud.dialogs.delete.description', { entityName: 'Mein Farmer' })
```

## Best Practices

### 1. Entity-Typ-Namen
- **Immer** `getEntityTypeLabel()` verwenden statt hardcoded Strings
- Entity-Typ-Schlüssel in `crud.entities.*` definieren
- Fallback-Wert als dritten Parameter angeben

```typescript
// ✅ Richtig
const entityTypeLabel = getEntityTypeLabel(t, 'farmer', 'Farmer');

// ❌ Falsch
const entityTypeLabel = 'Farmer';
```

### 2. Feld-Labels
- **Immer** `t('crud.fields.*')` verwenden
- Neue Felder in `crud.fields.*` definieren
- Bei fehlender Übersetzung `getFieldLabel()` verwenden

```typescript
// ✅ Richtig
<TableHead>{t('crud.fields.name')}</TableHead>

// ✅ Auch richtig (mit Fallback)
<TableHead>{getFieldLabel(t, 'customField', 'Custom Field')}</TableHead>
```

### 3. Aktionen
- **Immer** `t('crud.actions.*')` verwenden
- Konsistente Aktion-Namen verwenden (create, update, delete, cancel, etc.)

```typescript
// ✅ Richtig
<Button>{t('crud.actions.create')}</Button>
<Button>{t('crud.actions.edit')}</Button>
<Button>{t('crud.actions.delete')}</Button>
```

### 4. Status-Labels
- **Immer** `getStatusLabel()` verwenden
- Status-Werte in `status.*` definieren

```typescript
// ✅ Richtig
<Badge>{getStatusLabel(t, status, status)}</Badge>
```

### 5. Nachrichten
- **Immer** `getSuccessMessage()` / `getErrorMessage()` verwenden
- Entity-Typ automatisch übersetzen lassen

```typescript
// ✅ Richtig
const successMsg = getSuccessMessage(t, 'create', 'farmer');
// => "Farmer erfolgreich erstellt"

const errorMsg = getErrorMessage(t, 'delete', 'contract');
// => "Fehler beim Löschen von Vertrag"
```

### 6. Dialoge
- **Immer** Entity-Typ als übersetzten Wert übergeben
- Template-Variablen korrekt verwenden

```typescript
// ✅ Richtig
<CrudDeleteDialog
  entityType={entityTypeLabel}  // Übersetzt, nicht 'Farmer'
  entityName={farmer.fullName}
  // ...
/>
```

## Übersetzungsstruktur

### Hierarchie

```
translation.json
├── common.*              # Allgemeine Übersetzungen
├── status.*              # Status-Werte
└── crud.*                # CRUD-spezifische Übersetzungen
    ├── actions.*         # Aktionen
    ├── dialogs.*         # Dialog-Texte
    │   ├── delete.*      # Delete-Dialog
    │   ├── cancel.*      # Cancel-Dialog
    │   └── amend.*       # Amendment-Dialog
    ├── fields.*          # Feld-Labels
    ├── messages.*        # Nachrichten
    ├── audit.*           # Audit-Trail
    ├── print.*           # Druck/Export
    ├── entities.*        # Entity-Typ-Namen
    ├── list.*            # Listen-Ansicht
    └── detail.*          # Detail-Ansicht
```

### Template-Variablen

Viele Übersetzungen unterstützen Template-Variablen:

```json
{
  "crud": {
    "dialogs": {
      "delete": {
        "title": "{{entityType}} löschen",
        "description": "Möchten Sie wirklich {{entityName}} löschen?"
      }
    },
    "messages": {
      "createSuccess": "{{entityType}} erfolgreich erstellt"
    },
    "list": {
      "title": "{{entityType}} Liste"
    },
    "detail": {
      "title": "{{entityType}}: {{entityName}}"
    }
  }
}
```

## Erweiterungen

### Neue Entity-Typen hinzufügen

1. Übersetzung in `translation.json` hinzufügen:
```json
{
  "crud": {
    "entities": {
      "newEntity": "Neue Entität"
    }
  }
}
```

2. In der Komponente verwenden:
```typescript
const entityType = 'newEntity';
const entityTypeLabel = getEntityTypeLabel(t, entityType, 'New Entity');
```

### Neue Dialoge erstellen

1. Übersetzungen in `translation.json` hinzufügen:
```json
{
  "crud": {
    "dialogs": {
      "myDialog": {
        "title": "{{entityType}} Aktion",
        "description": "Beschreibung...",
        "confirmButton": "Bestätigen",
        "cancelButton": "Abbrechen"
      }
    }
  }
}
```

2. In der Komponente verwenden:
```typescript
const { t } = useTranslation();
const entityTypeLabel = getEntityTypeLabel(t, entityType);

<Dialog>
  <DialogTitle>
    {t('crud.dialogs.myDialog.title', { entityType: entityTypeLabel })}
  </DialogTitle>
  <DialogDescription>
    {t('crud.dialogs.myDialog.description')}
  </DialogDescription>
</Dialog>
```

### Neue Felder hinzufügen

1. Übersetzung in `translation.json` hinzufügen:
```json
{
  "crud": {
    "fields": {
      "myNewField": "Mein neues Feld"
    }
  }
}
```

2. In der Komponente verwenden:
```typescript
<TableHead>{t('crud.fields.myNewField')}</TableHead>
```

## Migration bestehender Komponenten

### Schritt 1: Imports hinzufügen
```typescript
import { useTranslation } from 'react-i18next';
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers';
```

### Schritt 2: Hook initialisieren
```typescript
const { t } = useTranslation();
const entityType = 'myEntity';
const entityTypeLabel = getEntityTypeLabel(t, entityType, 'My Entity');
```

### Schritt 3: Texte ersetzen
```typescript
// Vorher
<h2>Farmer</h2>
<Button>Löschen</Button>

// Nachher
<h2>{entityTypeLabel}</h2>
<Button>{t('crud.actions.delete')}</Button>
```

### Schritt 4: Übersetzungen hinzufügen
Alle verwendeten Übersetzungsschlüssel in `translation.json` definieren.

## Fehlerbehebung

### Übersetzung wird nicht angezeigt
1. Prüfen, ob der Schlüssel in `translation.json` existiert
2. Prüfen, ob der Namespace korrekt ist (`crud.*`)
3. Prüfen, ob Template-Variablen korrekt übergeben werden

### Entity-Typ wird nicht übersetzt
1. Prüfen, ob Entity-Typ in `crud.entities.*` definiert ist
2. Fallback-Wert als dritten Parameter angeben
3. Prüfen, ob `getEntityTypeLabel()` verwendet wird

### Status wird nicht übersetzt
1. Prüfen, ob Status in `status.*` definiert ist
2. `getStatusLabel()` verwenden statt direktem `t()` Aufruf

## Referenzen

- **Odoo 19.0 Essentials (Deutsch):** https://github.com/odoo/documentation/blob/19.0/locale/de/LC_MESSAGES/essentials.po
- **i18next Dokumentation:** https://www.i18next.com/
- **React i18next:** https://react.i18next.com/

## Dateien-Übersicht

### Geänderte Dateien
- `packages/frontend-web/src/i18n/locales/de/translation.json`
- `packages/frontend-web/src/features/crud/components/CrudDeleteDialog.tsx`
- `packages/frontend-web/src/features/crud/components/CrudCancelDialog.tsx`
- `packages/frontend-web/src/features/crud/components/CrudAuditTrailPanel.tsx`
- `packages/frontend-web/src/features/crud/components/CrudPrintButton.tsx`
- `packages/frontend-web/src/pages/agribusiness/farmers.tsx`
- `packages/frontend-web/src/pages/agribusiness/field-service-tasks.tsx`
- `packages/frontend-web/src/pages/contracts-v2.tsx`

### Neue Dateien
- `packages/frontend-web/src/features/crud/utils/i18n-helpers.ts`
- `packages/frontend-web/src/features/crud/utils/index.ts`
- `docs/i18n-integration.md` (diese Datei)

## Nächste Schritte

1. **Weitere Sprachen hinzufügen:** Englisch, Französisch, etc.
2. **Weitere Entity-Typen:** Neue Entities automatisch übersetzen
3. **Validierung:** Übersetzungs-Vollständigkeit prüfen
4. **Tests:** Unit-Tests für i18n Helper-Funktionen
5. **Dokumentation:** API-Dokumentation für Helper-Funktionen

---

**Erstellt:** 2025-01-20  
**Version:** 1.0  
**Autor:** AI Assistant

