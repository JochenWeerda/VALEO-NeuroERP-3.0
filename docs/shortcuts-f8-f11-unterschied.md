# Unterschied zwischen Strg+F8 und F11

## Übersicht

In allen Eingabemasken (Lieferschein, Rechnung, Auftrag, etc.) gibt es zwei verschiedene Shortcuts für "Wie vorheriger Beleg":

## F11 (ohne Strg)

**Aktion**: `copy-previous-full`

**Funktion**: Kopiert **ALLE Daten** vom vorherigen Beleg:
- ✅ Kunde/Debitor
- ✅ Alle Positionen
- ✅ Alle Header-Daten (Niederlassung, Vertreter, etc.)

**Verwendung**: 
- Wenn Sie einen komplett identischen Beleg für denselben Kunden erstellen möchten
- Schnelle Wiederholung des letzten Belegs

**UI-Hinweis**: In der Maske als Link ">> wie vorheriger Beleg (F11)" sichtbar

## Strg+F8

**Aktion**: `copy-previous-positions`

**Funktion**: Kopiert **nur die Positionen** vom vorherigen Beleg:
- ✅ Aktuell ausgewählter Kunde bleibt erhalten (wird nicht geändert)
- ✅ Alle Positionen werden übernommen
- ✅ Header-Daten bleiben unverändert

**Verwendung**:
- **Hauptszenario**: Wenn zwei verschiedene Kunden die gleichen Artikel erhalten sollen
- Wenn Sie Positionen von einem Beleg auf einen anderen übertragen möchten
- Wenn Sie für einen anderen Kunden die gleichen Artikel liefern möchten

## Beispiel-Szenarien

### Szenario 1: Gleicher Kunde, gleiche Artikel
**Verwende**: **F11** (kopiert alles)
```
1. Neuen Beleg öffnen
2. F11 drücken
3. → Kunde + Positionen werden übernommen
4. Datum anpassen, speichern
```

### Szenario 2: Zwei verschiedene Kunden, gleiche Artikel
**Verwende**: **Strg+F8** (kopiert nur Positionen)
```
1. Neuen Beleg öffnen
2. Ersten Kunden auswählen (Strg+F1) → z.B. "Kunde A"
3. Artikel hinzufügen → z.B. "10x Artikel X, 5x Artikel Y"
4. Beleg speichern (Strg+F4)

5. Neuen Beleg öffnen
6. Zweiten Kunden auswählen (Strg+F1) → z.B. "Kunde B"
7. Strg+F8 drücken
8. → Nur Positionen werden übernommen (10x Artikel X, 5x Artikel Y)
   → Kunde B bleibt ausgewählt
9. Speichern (Strg+F4)
```

## Praktisches Beispiel

**Szenario**: Tägliche Lieferung der gleichen Artikel an mehrere Kunden

```
08:00 - Beleg für "Bäckerei Müller"
        → 20x Brot, 10x Brötchen, 5x Kuchen
        → F11 (wenn es der gleiche Kunde wie gestern ist)
        → ODER manuell anlegen

09:00 - Beleg für "Bäckerei Schmidt" (anderer Kunde!)
        → Gleiche Artikel: 20x Brot, 10x Brötchen, 5x Kuchen
        → Strg+F8 → Positionen werden übernommen
        → Nur Kunde ändern, Artikel bleiben gleich
```

## Implementierungsstatus

- ✅ Shortcut-Definitionen erstellt
- ✅ Handler registriert
- ⏳ Backend-Logik: Lade letzten Beleg vom aktuellen Benutzer (beleg-typ-spezifisch)
- ⏳ Frontend-Logik: Kopiere Daten in aktuellen State

## Nächste Schritte

1. **Backend-API**: 
   - `GET /api/v1/sales/delivery-notes/last` - Lade letzten Lieferschein
   - `GET /api/v1/sales/invoices/last` - Lade letzte Rechnung
   - `GET /api/v1/sales/orders/last` - Lade letzten Auftrag
   - etc. (beleg-typ-spezifisch)
2. **Frontend-Logik**: 
   - `copy-previous-full`: Setze `state.customer` + `state.positionen`
   - `copy-previous-positions`: Setze nur `state.positionen` (aktuell ausgewählter Kunde bleibt erhalten)
