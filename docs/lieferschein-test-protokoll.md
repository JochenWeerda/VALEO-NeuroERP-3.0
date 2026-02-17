# Lieferschein-Erfassungsmaske Test-Protokoll

## Test-Datum
2026-02-17

## Test-Umgebung
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Datenbank: PostgreSQL (Docker)

## Test-Szenario 1: Kundenauswahl (Debitor)

### Schritt 1: Maske öffnen
- ✅ URL: http://localhost:3000/verkauf/lieferschein-erfassung
- ✅ Seite lädt erfolgreich
- ✅ Keine Login-Maske beim direkten Aufruf

### Schritt 2: Debitor-Konto-Feld finden
- 🔄 Suche nach "Debitor-Kto." Feld
- 🔄 Klicke auf "..." Button neben dem Feld

### Schritt 3: Kundenauswahl-Dialog öffnen
- ⏳ Warte auf Dialog-Öffnung
- ⏳ Prüfe, ob Login-Maske erscheint (sollte NICHT passieren)

### Schritt 4: Kunde auswählen
- ⏳ Wähle einen Kunden aus der Liste
- ⏳ Prüfe, ob Kunde korrekt übernommen wird

## Test-Szenario 2: Artikelauswahl

### Schritt 1: Artikel-Dialog öffnen
- ⏳ Klicke auf "..." Button bei Artikel-Nr.
- ⏳ Prüfe, ob Login-Maske erscheint (sollte NICHT passieren)

### Schritt 2: Artikel auswählen
- ⏳ Wähle einen Artikel aus der Liste
- ⏳ Prüfe, ob Artikel korrekt übernommen wird

## Test-Szenario 3: Lieferschein speichern

### Schritt 1: Position hinzufügen
- ⏳ Fülle alle Pflichtfelder aus
- ⏳ Klicke auf "Zeile OK"

### Schritt 2: Speichern
- ⏳ Klicke auf "Speichern"
- ⏳ Prüfe, ob Lieferschein erfolgreich gespeichert wird

## Bekannte Probleme

### Problem 1: Login-Maske erscheint bei Kundenauswahl
- **Status**: ⏳ Wird getestet
- **Erwartung**: Sollte NICHT passieren
- **Ursache**: Möglicherweise 401-Fehler bei API-Call

### Problem 2: Login-Maske erscheint bei Artikelauswahl
- **Status**: ⏳ Wird getestet
- **Erwartung**: Sollte NICHT passieren
- **Ursache**: Möglicherweise 401-Fehler bei API-Call

## Lösungsansätze

1. **Mock-Benutzer verwenden**: Wenn OIDC nicht konfiguriert ist, sollte ein Mock-Benutzer automatisch erstellt werden
2. **API-Authentifizierung**: Backend sollte in Dev-Mode ohne Token funktionieren
3. **Axios-Interceptor**: Sollte nur bei konfiguriertem OIDC zur Login-Seite weiterleiten

