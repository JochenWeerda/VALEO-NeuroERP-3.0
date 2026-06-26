# Modul Annahme LKW – Plan und Ablauf

## Ziel
LKW-Annahme von der Registrierung bis zur abgeschlossenen Abfertigung (optional mit Qualitätsprüfung) durchgängig abbilden.

## Ablauf (End-to-End)

1. **Registrierung** – LKW meldet sich (per QR/Handy oder am Terminal)
   - Kennzeichen, Lieferant, Lieferschein-Nr., Artikel, Ankunftszeit, Priorität
   - Optional: Fotos (Kennzeichen, Lieferschein/Barcode) per Upload
   - → Eintrag in Warteschlange (Status: **wartend**)

2. **Warteschlange** – Übersicht aller LKW
   - Position, Kennzeichen, Lieferant, Artikel, Ankunft, Wartezeit, Status
   - Aktionen: **Bearbeiten** → öffnet Qualitäts-Check für diesen Eintrag
   - Status: wartend → **in-bearbeitung** (bei Start Qualitäts-Check) → **abgeschlossen** (nach Prüfung/Abrechnung)

3. **Qualitäts-Check** (optional, pro LKW)
   - LKW-Daten (Artikel, Lieferschein) werden aus der Warteschlange übernommen
   - Sichtprüfung, Messungen (Feuchtigkeit, Protein, Verunreinigung), Ergebnis (freigegeben/bedingt/gesperrt)
   - Nach Speichern: Eintrag kann auf **abgeschlossen** gesetzt werden (oder bleibt in-bearbeitung bis Abrechnung)

4. **QR-Code** – Mobilzugang
   - Seite zeigt QR; Scan öffnet LKW-Registrierung im Browser (iOS/Android)
   - Upload von Fotos direkt in der Registrierungsmaske

5. **Abrechnung** (bestehende Seite)
   - Abrechnung/Abwicklung der Anlieferung (unverändert genutzt)

## Technik

### Backend (compat)
- **POST /api/v1/annahme/lkw-registrierung** – erzeugt Eintrag, speichert in Cache, fügt ID zu `annahme:lkw:ids` hinzu
- **GET /api/v1/annahme/warteschlange** – liefert alle LKW-Einträge aus Cache (position, wartezeit, status)
- **GET /api/v1/annahme/warteschlange/{id}** – ein Eintrag (für Qualitäts-Check Vorbefüllung)
- **PATCH /api/v1/annahme/warteschlange/{id}** – Status aktualisieren (in-bearbeitung, abgeschlossen)
- **POST /api/v1/annahme/upload** – Datei-Upload für Kennzeichen/Lieferschein

### Frontend
- **Warteschlange** – Liste aus GET warteschlange, Buttons „QR-Code“, „LKW anmelden“, „Bearbeiten“ → Qualitäts-Check mit state.eintragId
- **Qualitäts-Check** – lädt LKW per ID, befüllt Artikel/Lieferschein; setzt Status in-bearbeitung beim Öffnen, optional abgeschlossen nach Speichern
- **LKW-Registrierung** – Wizard mit Upload; Submit → POST lkw-registrierung inkl. attachment_ids

### Persistenz
- LKW-Einträge und Upload-Metadaten im Redis-/In-Memory-Cache (TTL 7 Tage)
- Liste der IDs unter `annahme:lkw:ids`; je Eintrag `annahme:lkw:{id}` mit kennzeichen, lieferant, lieferschein_nr, artikel, ankunftszeit, prioritaet, status, attachment_ids
- Später: optional Migration auf DB-Tabelle für Annahme-Queue

### Frontend-API (lib/api/inventory.ts)
- `useWarteschlange()` – Liste
- `useWarteschlangeEintrag(id)` – ein Eintrag (für Qualitäts-Check)
- `usePatchWarteschlangeStatus()` – Status auf „in-bearbeitung“ oder „abgeschlossen“ setzen
