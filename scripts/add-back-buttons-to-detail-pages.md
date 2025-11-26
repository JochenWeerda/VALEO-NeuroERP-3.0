***REMOVED*** Back-Button Audit für Detail-Seiten

**Datum:** 2025-10-16  
**Ziel:** Alle Detail-Seiten mit Zurück-Navigation ausstatten

---

***REMOVED******REMOVED*** Status-Übersicht

***REMOVED******REMOVED******REMOVED*** ✅ Bereits vorhanden
- `crm/kontakt-detail.tsx` - Hat bereits Zurück-Button

***REMOVED******REMOVED******REMOVED*** ✅ Neu hinzugefügt
- `fibu/debitoren.tsx` - Zurück zur OP-Verwaltung

***REMOVED******REMOVED******REMOVED*** 🔧 Zu prüfen/ergänzen
- `crm/lead-detail.tsx`
- `crm/aktivitaet-detail.tsx`
- `crm/betriebsprofil-detail.tsx`
- `finance/dunning-editor.tsx`
- `sales/credit-note-editor.tsx`
- `einkauf/angebot-stamm.tsx`
- `einkauf/anfrage-stamm.tsx`
- `einkauf/bestellung-stamm.tsx`
- `einkauf/rechnungseingang.tsx`
- `einkauf/anlieferavis.tsx`
- `einkauf/auftragsbestaetigung.tsx`
- `agrar/saatgut-stamm.tsx`
- `agrar/duenger-stamm.tsx`
- `agrar/psm/abgabedokumentation.tsx`
- `verkauf/kunden-stamm-enhanced.tsx`
- `fibu/kreditoren.tsx` (von OP-Verwaltung erreichbar)

---

***REMOVED******REMOVED*** Pattern: Zurück-Button hinzufügen

***REMOVED******REMOVED******REMOVED*** Import
```typescript
import { BackButton } from '@/components/BackButton'
```

***REMOVED******REMOVED******REMOVED*** Verwendung (mit expliziter Route)
```typescript
<div className="flex items-center justify-between">
  <div>
    <h1>Titel der Seite</h1>
    <p className="text-muted-foreground">Beschreibung</p>
  </div>
  <BackButton to="/parent-route" label="Zurück zur Übersicht" />
</div>
```

***REMOVED******REMOVED******REMOVED*** Verwendung (History-basiert)
```typescript
<div className="flex items-center justify-between">
  <div>
    <h1>Titel der Seite</h1>
  </div>
  <BackButton />
</div>
```

---

***REMOVED******REMOVED*** Navigation-Mapping (Parent-Routes)

| Detail-Seite | Parent-Route | Button-Label |
|-------------|--------------|--------------|
| `/crm/kontakt/:id` | `/crm/kontakte-liste` | Zurück zur Kontakt-Liste |
| `/crm/lead/:id` | `/crm/leads` | Zurück zur Lead-Liste |
| `/crm/aktivitaet/:id` | `/crm/aktivitaeten` | Zurück zu Aktivitäten |
| `/crm/betriebsprofil/:id` | `/crm/betriebsprofile-liste` | Zurück zu Betriebsprofilen |
| `/fibu/debitoren` | `/fibu/op-verwaltung` | Zurück zur OP-Verwaltung |
| `/fibu/kreditoren` | `/fibu/op-verwaltung` | Zurück zur OP-Verwaltung |
| `/einkauf/angebot-stamm/:id` | `/einkauf/angebote-liste` | Zurück zur Angebots-Liste |
| `/einkauf/anfrage-stamm/:id` | `/einkauf/anfragen-liste` | Zurück zur Anfragen-Liste |
| `/einkauf/bestellung-stamm/:id` | `/einkauf/bestellungen-liste` | Zurück zur Bestellungen-Liste |
| `/agrar/saatgut-stamm/:id` | `/agrar/saatgut-liste` | Zurück zur Saatgut-Liste |
| `/agrar/duenger-stamm/:id` | `/agrar/duenger-liste` | Zurück zur Dünger-Liste |
| `/verkauf/kunden-stamm/:id` | `/verkauf/kunden-liste` | Zurück zur Kunden-Liste |

---

***REMOVED******REMOVED*** Alternative: History-Fallback

Wenn die Parent-Route unklar ist (z. B. bei Multi-Entry-Point-Seiten):

```typescript
<BackButton />  {/* Verwendet navigate(-1) */}
```

---

***REMOVED******REMOVED*** UI-Guideline

***REMOVED******REMOVED******REMOVED*** Desktop (≥768px)
- **Position:** Oben rechts (neben Titel)
- **Variante:** `outline`
- **Größe:** `default`
- **Icon:** ArrowLeft + Label

***REMOVED******REMOVED******REMOVED*** Mobile (<768px)
- **Position:** Oben links (über Titel)
- **Variante:** `ghost`
- **Größe:** `icon`
- **Nur Icon:** ArrowLeft (ohne Label)

***REMOVED******REMOVED******REMOVED*** Responsive Beispiel
```typescript
<div className="flex flex-col md:flex-row md:items-center md:justify-between">
  <div className="order-2 md:order-1">
    <h1>Titel</h1>
  </div>
  <div className="order-1 md:order-2 mb-4 md:mb-0">
    <BackButton to="/parent" className="md:hidden" size="icon" variant="ghost" />
    <BackButton to="/parent" className="hidden md:inline-flex" />
  </div>
</div>
```

---

***REMOVED******REMOVED*** Testing

Für jede hinzugefügte Seite:

1. ✅ Zurück-Button sichtbar
2. ✅ Click navigiert zur korrekten Parent-Route
3. ✅ Keine Loops (Zurück → Zurück → Zurück funktioniert)
4. ✅ Mobile: Icon-only, Desktop: Icon + Label (falls responsive)

