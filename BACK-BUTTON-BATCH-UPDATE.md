***REMOVED*** Batch-Update: Zurück-Buttons für verbleibende Detail-Seiten

***REMOVED******REMOVED*** Status-Audit (Detailliert)

***REMOVED******REMOVED******REMOVED*** ✅ Bereits vorhanden (verifiziert)
1. **Fibu:**
   - `fibu/debitoren.tsx` - ✅ Neu hinzugefügt
   - `fibu/kreditoren.tsx` - ✅ Neu hinzugefügt

2. **CRM:**
   - `crm/kontakt-detail.tsx` - ✅ Vorhanden (ArrowLeft + "Zurück")
   - `crm/lead-detail.tsx` - ✅ Vorhanden (ArrowLeft + "Zurück")

3. **Agrar:**
   - `agrar/saatgut-stamm.tsx` - ✅ Vorhanden (ArrowLeft + handleCancel)
   - `agrar/duenger-stamm.tsx` - ✅ Vorhanden (ArrowLeft + handleCancel)

***REMOVED******REMOVED******REMOVED*** 🔧 Verwendet ObjectPage/Mask-Builder (automatischer Zurück-Button)
Diese Seiten verwenden die `ObjectPage`-Komponente aus `@/components/mask-builder`, die bereits einen integrierten Zurück-Mechanismus haben sollte:

- `einkauf/angebot-stamm.tsx`
- `einkauf/anfrage-stamm.tsx`
- `einkauf/bestellung-stamm.tsx`

**Empfehlung:** ObjectPage-Komponente prüfen, ob Zurück-Button integriert ist.

***REMOVED******REMOVED******REMOVED*** 🔧 Zu ergänzen (manuelle Implementierung erforderlich)
Diese Seiten haben noch keinen Zurück-Button und verwenden KEIN ObjectPage:

1. **CRM:**
   - `crm/aktivitaet-detail.tsx`
   - `crm/betriebsprofil-detail.tsx`

2. **Finance:**
   - `finance/dunning-editor.tsx`

3. **Sales:**
   - `sales/credit-note-editor.tsx`

4. **Einkauf:**
   - `einkauf/rechnungseingang.tsx`
   - `einkauf/anlieferavis.tsx`
   - `einkauf/auftragsbestaetigung.tsx`

5. **Agrar:**
   - `agrar/psm/abgabedokumentation.tsx`

6. **Verkauf:**
   - `verkauf/kunden-stamm.tsx` (ggf. bereits vorhanden)

7. **Workflows:**
   - `workflows/approval.tsx`

---

***REMOVED******REMOVED*** Implementierungs-Strategie

***REMOVED******REMOVED******REMOVED*** Phase 1: ObjectPage-Komponente prüfen ✅
**Datei:** `packages/frontend-web/src/components/mask-builder/ObjectPage.tsx`

**Prüfen:**
- Hat ObjectPage bereits einen Zurück-Button?
- Falls nein: Hinzufügen via Props (`showBackButton?: boolean`, `onBack?: () => void`)

**Pattern:**
```typescript
interface ObjectPageProps {
  config: MaskConfig;
  showBackButton?: boolean;
  onBack?: () => void;
  backLabel?: string;
  backRoute?: string;
}

// In ObjectPage-Header:
{showBackButton && (
  <BackButton 
    to={backRoute} 
    onClick={onBack} 
    label={backLabel || 'Zurück'} 
  />
)}
```

***REMOVED******REMOVED******REMOVED*** Phase 2: Manuelle Ergänzung (8 Seiten)

***REMOVED******REMOVED******REMOVED******REMOVED*** Template für alle verbleibenden Seiten:

```typescript
// 1. Import hinzufügen
import { BackButton } from '@/components/BackButton'

// 2. Header-Section anpassen
<div className="flex items-center justify-between">
  <div>
    <h1>Titel</h1>
    <p>Beschreibung</p>
  </div>
  <BackButton to="/parent-route" label="Zurück zur Übersicht" />
</div>
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Konkrete Parent-Routes:

| Detail-Seite | Parent-Route | Label |
|-------------|--------------|-------|
| `crm/aktivitaet-detail.tsx` | `/crm/aktivitaeten` | Zurück zu Aktivitäten |
| `crm/betriebsprofil-detail.tsx` | `/crm/betriebsprofile-liste` | Zurück zu Betriebsprofilen |
| `finance/dunning-editor.tsx` | `/finance/dunning` | Zurück zur Mahnwesen-Übersicht |
| `sales/credit-note-editor.tsx` | `/sales/credit-notes` | Zurück zu Gutschriften |
| `einkauf/rechnungseingang.tsx` | `/einkauf/rechnungseingaenge-liste` | Zurück zu Rechnungseingängen |
| `einkauf/anlieferavis.tsx` | `/einkauf/anlieferavis-liste` | Zurück zu Lieferavisen |
| `einkauf/auftragsbestaetigung.tsx` | `/einkauf/auftragsbestaetigungen-liste` | Zurück zu Auftragsbestätigungen |
| `agrar/psm/abgabedokumentation.tsx` | `/agrar/psm` | Zurück zu PSM-Übersicht |
| `workflows/approval.tsx` | `/workflows` | Zurück zu Workflows |

---

***REMOVED******REMOVED*** Ausführungs-Plan

***REMOVED******REMOVED******REMOVED*** Schritt 1: ObjectPage prüfen & erweitern (falls nötig)
```bash
***REMOVED*** ObjectPage-Komponente lesen
cat packages/frontend-web/src/components/mask-builder/ObjectPage.tsx

***REMOVED*** Falls kein Zurück-Button: Erweitern
***REMOVED*** Props hinzufügen + BackButton-Komponente integrieren
```

***REMOVED******REMOVED******REMOVED*** Schritt 2: Verbleibende 8 Seiten ergänzen

**Automatisiert (PowerShell-Skript):**
```powershell
.\scripts\add-back-buttons.ps1
***REMOVED*** Dann manuell Parent-Routes anpassen
```

**Oder manuell:**
1. Datei öffnen
2. BackButton importieren
3. Header-Section anpassen (flex-Layout + BackButton)
4. Speichern & Lint-Check

***REMOVED******REMOVED******REMOVED*** Schritt 3: Testing
Für jede Seite:
- [ ] Zurück-Button sichtbar
- [ ] Click navigiert zur korrekten Parent-Route
- [ ] Keine Loops
- [ ] Mobile-Responsive (falls implementiert)

---

***REMOVED******REMOVED*** Zusammenfassung

**Gesamt-Seiten:** ~18 Detail-Seiten  
**Bereits fertig:** 6 (Fibu, CRM, Agrar-Stamm)  
**ObjectPage (auto):** 3 (Einkauf-Stamm)  
**Manuell zu ergänzen:** 8 Seiten  

**Geschätzte Zeit:**  
- ObjectPage-Prüfung: 10 Min
- Manuelle Ergänzung (8× 5 Min): 40 Min  
- Testing & Lint: 20 Min  
**Total: ~70 Min**

---

***REMOVED******REMOVED*** Next Action

1. ✅ ObjectPage-Komponente prüfen
2. 🔧 Falls kein Zurück-Button: ObjectPage erweitern
3. 🔧 8 verbleibende Seiten manuell ergänzen
4. ✅ Smoke-Test durchführen

