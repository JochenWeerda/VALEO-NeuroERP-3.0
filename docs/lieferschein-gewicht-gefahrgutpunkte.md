# Lieferschein-Erfassung: Gewicht & Gefahrgut-Punkte

**Datum:** 2025-01-16  
**Status:** ✅ Implementiert

## Übersicht

Die Lieferschein-Erfassungsmaske berechnet und validiert automatisch:
- **Gesamtgewicht** aller Positionen
- **Gesamt-Gefahrgut-Punkte** aller Positionen

## 1. Gewichtsberechnung

### 1.1 Datenstruktur

**Position Type:**
```typescript
export type Position = {
  // ... andere Felder
  gewicht: number // Gewicht pro Einheit (aus Artikel)
  gesamtGewicht: number // Gesamtgewicht (gewicht × menge)
}
```

**CurrentPositionDetails:**
```typescript
type CurrentPositionDetails = {
  // ... andere Felder
  artikelGewicht: number // Gewicht pro Einheit (aus Artikel)
}
```

### 1.2 Implementierung

#### Artikelauswahl
- Beim Auswählen eines Artikels wird `article.weight` oder `article.gewicht` geladen
- Das Gewicht wird in `currentPosition.artikelGewicht` gespeichert

#### Position hinzufügen
- Beim Klicken auf "Zeile OK" wird `gesamtGewicht = artikelGewicht × menge` berechnet
- Das Gesamtgewicht wird in der Position gespeichert

#### Summen-Berechnung
```typescript
const gesamtGewicht = state.positionen.reduce(
  (sum, pos) => sum + (pos.gesamtGewicht || 0), 
  0
)
```

#### Laden bestehender Lieferscheine
- Beim Laden wird das Artikel-Gewicht aus der API nachgeladen (`/api/v1/articles/{artikel_id}`)
- Das Gesamtgewicht wird neu berechnet: `artikelGewicht × menge`

### 1.3 Anzeige

**Summen-Zeile:**
- Feld: "Gewicht:"
- Format: `${summen.gewicht.toFixed(2)} kg`
- Beispiel: "125.50 kg"

## 2. Gefahrgut-Punkte

### 2.1 Datenstruktur

**Position Type:**
```typescript
export type Position = {
  // ... andere Felder
  gefPunkt: string // Gefahrgut-Punkte als String (für Anzeige in Tabelle)
  gefahrgutPunkte: number // Gefahrgut-Punkte pro Einheit (numerisch, aus Artikel)
  gesamtGefahrgutPunkte: number // Gesamt-Gefahrgut-Punkte (gefahrgutPunkte × menge)
}
```

**CurrentPositionDetails:**
```typescript
type CurrentPositionDetails = {
  // ... andere Felder
  artikelGefahrgutPunkte: number // Gefahrgut-Punkte pro Einheit (aus Artikel)
}
```

### 2.2 Implementierung

#### Artikelauswahl
- Beim Auswählen eines Artikels werden die Gefahrgut-Punkte geladen:
  - Primär: `article.gefahrgut_punkte` oder `article.gefahrgutPunkte`
  - Fallback: Aus `article.gefahrgutklasse` berechnen (falls als Zahl gespeichert)
- Die Gefahrgut-Punkte werden in `currentPosition.artikelGefahrgutPunkte` gespeichert

#### Position hinzufügen
- Beim Klicken auf "Zeile OK" wird `gesamtGefahrgutPunkte = artikelGefahrgutPunkte × menge` berechnet
- **Validierung:** Prüfung, ob die Summe 1000 Punkte überschreitet
- Bei Überschreitung wird eine Fehlermeldung angezeigt und die Position nicht hinzugefügt

#### Summen-Berechnung
```typescript
const gesamtGefahrgutPunkte = state.positionen.reduce(
  (sum, pos) => sum + (pos.gesamtGefahrgutPunkte || 0), 
  0
)
```

#### Laden bestehender Lieferscheine
- Beim Laden wird das Artikel-Gefahrgut-Punkte aus der API nachgeladen (`/api/v1/articles/{artikel_id}`)
- Das Gesamt-Gefahrgut-Punkte wird neu berechnet: `artikelGefahrgutPunkte × menge`

### 2.3 Validierung: Maximal 1000 Gefahrgut-Punkte

**Regel:** Pro Lieferung dürfen maximal 1000 Gefahrgut-Punkte geladen werden.

**Implementierung:**
```typescript
// Validierung: Maximal 1000 Gefahrgut-Punkte pro Lieferung
const aktuelleGefahrgutPunkte = state.positionen.reduce(
  (sum, pos) => sum + (pos.gesamtGefahrgutPunkte || 0), 
  0
)
const neueGesamtGefahrgutPunkte = aktuelleGefahrgutPunkte + gesamtGefahrgutPunkte

if (neueGesamtGefahrgutPunkte > 1000) {
  push(`Fehler: Die maximale Anzahl von 1000 Gefahrgut-Punkten pro Lieferung würde überschritten werden. Aktuell: ${aktuelleGefahrgutPunkte.toFixed(0)}, zusätzlich: ${gesamtGefahrgutPunkte.toFixed(0)}, Gesamt: ${neueGesamtGefahrgutPunkte.toFixed(0)}`)
  return
}
```

### 2.4 Anzeige

**Summen-Zeile:**
- Feld: "Gef.-Pun.:"
- Format: `${summen.gefahrgutPunkte.toFixed(0)}` (ganze Zahl)
- Beispiel: "450"

**Visuelle Warnung:**
- **Gelb** (`bg-yellow-100 border-yellow-500`): > 800 Punkte (Warnung)
- **Rot** (`bg-red-100 border-red-500`): > 1000 Punkte (Fehler)
- Tooltip: "Warnung: Maximal 1000 Gefahrgut-Punkte erlaubt!" (bei > 1000)

**Positionen-Tabelle:**
- Spalte: "Gef.-Pun."
- Zeigt `gefPunkt` (String) für jede Position an

## 3. API-Integration

### 3.1 Artikel-API

**Endpoint:** `GET /api/v1/articles/{article_id}`

**Erwartete Felder:**
```json
{
  "id": "uuid",
  "weight": 12.5,  // Gewicht in kg pro Einheit
  "gefahrgut_punkte": 50,  // Gefahrgut-Punkte pro Einheit (optional)
  "gefahrgutklasse": "3.1"  // Gefahrgutklasse (Fallback für Punkte)
}
```

### 3.2 Backend-Schema

**Artikel-Modell:**
- `weight` (DECIMAL(8, 2)): Gewicht pro Einheit
- `gefahrgutklasse` (String(40)): Gefahrgutklasse
- **TODO:** `gefahrgut_punkte` Feld hinzufügen (aktuell aus `gefahrgutklasse` berechnet)

## 4. Dateien

### Frontend
- `packages/frontend-web/src/pages/verkauf/lieferschein-erfassung.tsx`
  - Position Type erweitert
  - Summen-Berechnung erweitert
  - Validierung implementiert
  - Anzeige in Summen-Zeile

### Backend
- `app/infrastructure/models/__init__.py`
  - Article Model: `weight` (bereits vorhanden)
  - Article Model: `gefahrgutklasse` (bereits vorhanden)
  - **TODO:** `gefahrgut_punkte` Feld hinzufügen

## 5. Testfälle

### 5.1 Gewicht
- ✅ Artikel mit Gewicht auswählen → Gewicht wird geladen
- ✅ Position hinzufügen → Gesamtgewicht wird berechnet
- ✅ Mehrere Positionen → Gesamtgewicht wird summiert
- ✅ Bestehenden Lieferschein laden → Gewicht wird nachgeladen

### 5.2 Gefahrgut-Punkte
- ✅ Artikel mit Gefahrgut-Punkten auswählen → Punkte werden geladen
- ✅ Position hinzufügen → Gesamt-Punkte werden berechnet
- ✅ Mehrere Positionen → Gesamt-Punkte werden summiert
- ✅ Summe < 1000 → Position wird hinzugefügt
- ✅ Summe > 1000 → Fehlermeldung, Position wird nicht hinzugefügt
- ✅ Visuelle Warnung bei > 800 Punkten
- ✅ Bestehenden Lieferschein laden → Punkte werden nachgeladen

## 6. Nächste Schritte

### Backend
- [ ] `gefahrgut_punkte` Feld zum Article Model hinzufügen
- [ ] Migration erstellen
- [ ] API-Schema erweitern

### Frontend
- [ ] Testfälle für Edge Cases (z.B. Artikel ohne Gewicht/Punkte)
- [ ] Verbesserung der Fehlermeldungen
- [ ] Optional: Warnung bei > 800 Punkten auch beim Hinzufügen

---

**Status:** ✅ Implementiert und getestet  
**Version:** 1.0.0

