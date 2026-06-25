# Lieferschein-Erfassungsmaske Test-Zusammenfassung

## Test-Status: In Bearbeitung

### Vorbereitung
- ✅ Docker-Services laufen (Frontend, Backend, PostgreSQL)
- ✅ Datenbank enthält Test-Daten:
  - 6 Kunden/Debitoren
  - 18 Artikel
- ✅ Frontend läuft auf http://localhost:3000
- ✅ Lieferschein-Erfassungsmaske ist erreichbar

### Test-Ergebnisse

#### Test 1: Seitenaufruf
- ✅ URL: http://localhost:3000/verkauf/lieferschein-erfassung
- ✅ Seite lädt erfolgreich
- ✅ Keine Login-Maske beim direkten Aufruf
- ✅ Mock-Benutzer wird automatisch erstellt (wenn OIDC nicht konfiguriert)

#### Test 2: Kundenauswahl (Debitor) - ⏳ In Bearbeitung
- ⏳ Debitor-Konto-Feld gefunden
- ⏳ "..." Button wird geklickt
- ⏳ Prüfe, ob Login-Maske erscheint (sollte NICHT passieren)
- ⏳ Kunde wird ausgewählt

#### Test 3: Artikelauswahl - ⏳ Ausstehend
- ⏳ Artikel-Dialog wird geöffnet
- ⏳ Prüfe, ob Login-Maske erscheint (sollte NICHT passieren)
- ⏳ Artikel wird ausgewählt

#### Test 4: Lieferschein speichern - ⏳ Ausstehend
- ⏳ Position wird hinzugefügt
- ⏳ Lieferschein wird gespeichert

## Bekannte Probleme

### Problem: Login-Maske erscheint bei API-Calls
**Status**: ⏳ Wird getestet

**Mögliche Ursachen**:
1. Backend gibt 401 zurück, obwohl Mock-Benutzer vorhanden ist
2. Axios-Interceptor leitet zur Login-Seite weiter, obwohl OIDC nicht konfiguriert ist
3. API-Endpoint `/api/v1/crm/customers` erfordert Authentifizierung

**Lösungsansätze**:
1. ✅ Mock-Benutzer wird bereits erstellt (siehe `packages/frontend-web/src/lib/auth.ts`)
2. ✅ Axios-Interceptor prüft bereits auf OIDC-Konfiguration (siehe `packages/frontend-web/src/lib/axios.ts`)
3. ⏳ Backend sollte in Dev-Mode ohne Token funktionieren

## Nächste Schritte

1. **Browser-Test durchführen**:
   - Debitor-Konto "..." Button klicken
   - Prüfen, ob Login-Maske erscheint
   - Falls ja: Backend-Logs prüfen, API-Call analysieren

2. **Backend-Authentifizierung prüfen**:
   - Prüfen, ob `/api/v1/crm/customers` in Dev-Mode ohne Token funktioniert
   - Falls nein: Backend-Middleware anpassen

3. **Artikelauswahl testen**:
   - Gleiche Schritte wie bei Kundenauswahl

4. **Vollständigen Workflow testen**:
   - Kunde auswählen
   - Artikel auswählen
   - Position hinzufügen
   - Lieferschein speichern

