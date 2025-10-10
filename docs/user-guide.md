# VALEO NeuroERP User Guide

## Belegfluss (Document Flow)

### 1. Verkaufsprozess

#### 1.1 Auftrag erstellen

**Navigation**: Sales → New Order

**Schritte**:
1. **Kopfdaten eingeben**
   - Kunden auswählen (Lookup-Feld)
   - Datum automatisch gesetzt
   - Zahlungsbedingungen wählen

2. **Positionen hinzufügen**
   - Artikel über Lookup suchen
   - Menge und Preis eingeben
   - Automatische Berechnung der Zeilen-Summen

3. **Auftrag speichern**
   - Button "Auftrag speichern"
   - Nummer wird automatisch vergeben (SO-2025-XXXXXX)
   - Status: "Entwurf"

**Tastenkürzel**:
- `Ctrl+S`: Speichern
- `F2`: Neuer Artikel hinzufügen
- `Tab`: Nächstes Feld

#### 1.2 Auftrag freigeben

**Automatische Prüfungen**:
- ✅ Gesamtbetrag > 0€
- ✅ Alle Pflichtfelder ausgefüllt
- ✅ Policy-Checks (z.B. Betragsgrenzen)

**Freigabe-Prozess**:
1. **Einreichen zur Freigabe**
   - Button "Einreichen" klicken
   - Status wechselt zu "Pending"
   - Benachrichtigung an zuständige Personen

2. **Freigabe durch Controller**
   - Controller erhält Benachrichtigung
   - Prüfung der Auftragsdaten
   - Genehmigung oder Ablehnung

3. **Buchung**
   - Nach Freigabe: "Buchen" Button
   - Status wechselt zu "Approved" → "Posted"
   - Folgebelege können erstellt werden

#### 1.3 Lieferschein erstellen

**Aus Auftrag ableiten**:
1. Auftrag öffnen
2. "Lieferschein erstellen" klicken
3. Daten werden automatisch übernommen
4. Lieferadresse anpassen falls nötig
5. Speichern und freigeben

**Direkterstellung**:
- Sales → New Delivery
- Manuelle Dateneingabe

#### 1.4 Rechnung erstellen

**Aus Lieferschein ableiten**:
1. Lieferschein öffnen
2. "Rechnung erstellen" klicken
3. Preise und Konditionen werden übernommen
4. Buchungsdatum setzen
5. Speichern und freigeben

### 2. Einkaufsprozess

#### 2.1 Bestellung erstellen

**Navigation**: Purchasing → New Order

**Schritte**:
1. **Lieferanten auswählen**
   - Über Lookup-Feld suchen
   - Automatische Übernahme von Konditionen

2. **Artikel bestellen**
   - Artikel aus Katalog wählen
   - Mengen und Preise eingeben
   - EK-Preis-Kontrolle (nicht über VK verkaufen)

3. **Freigabe einholen**
   - Policy-Check für Bestellwert
   - Controller-Freigabe bei hohen Beträgen

#### 2.2 Wareneingang buchen

**Navigation**: Inventory → Goods Receipt

**Prozess**:
1. **Bestellung auswählen**
   - Offene Bestellungen anzeigen
   - Positionen zur Buchung auswählen

2. **Mengen erfassen**
   - Gelieferte Menge eingeben
   - Abweichungen dokumentieren
   - Qualitätsprüfung notieren

3. **Lagerbuchung**
   - Automatische Lagerstands-Aktualisierung
   - Reservierungen für Verkauf freigeben

### 3. Freigabe-Workflow (Approval Process)

#### 3.1 Status-Übersicht

```
Entwurf → Eingereicht → Freigegeben → Gebucht
                    ↓
                 Abgelehnt
```

**Status-Beschreibungen**:
- **Entwurf**: Bearbeitung möglich, keine Freigabe nötig
- **Eingereicht**: Wartet auf Freigabe durch Controller
- **Freigegeben**: Controller hat genehmigt, bereit zur Buchung
- **Gebucht**: Endstatus, keine Änderungen mehr möglich
- **Abgelehnt**: Zurückgewiesen, kann überarbeitet werden

#### 3.2 Benachrichtigungen

**Realtime-Updates**:
- 🔔 Toast-Benachrichtigungen bei Status-Änderungen
- 📊 System-Status-Anzeige im Header (🟢🟠🔴)
- 📱 Browser-Benachrichtigungen (falls aktiviert)

**E-Mail-Benachrichtigungen**:
- Freigabe-Anforderungen
- Genehmigungen/Ablehnungen
- Eskalationen bei Zeitüberschreitungen

#### 3.3 Rollen und Berechtigungen

**Vertriebsmitarbeiter (Sales)**:
- ✅ Aufträge erstellen und bearbeiten
- ✅ Aufträge zur Freigabe einreichen
- ❌ Direkte Buchung ohne Freigabe

**Controller**:
- ✅ Alle Aufträge einsehen
- ✅ Freigabe erteilen oder ablehnen
- ✅ Export-Funktionen nutzen
- ✅ Berichte und Analysen

**Administrator**:
- ✅ Voller Systemzugriff
- ✅ Konfiguration ändern
- ✅ Backup und Restore
- ✅ Benutzerverwaltung

### 4. Druck und Archiv (Print & Archive)

#### 4.1 Dokumente drucken

**PDF-Generierung**:
1. **Beleg öffnen**
   - Jeder Beleg hat "PDF drucken" Button

2. **Automatische Archivierung**
   - PDF wird automatisch archiviert
   - SHA-256 Hash für Integrität
   - Versionierung bei Änderungen

3. **Branding**
   - VALEO Logo und Firmendaten
   - Professionelles Layout
   - Status-Anzeige im Footer

**Druck-Optionen**:
- Direkter Download
- Druckvorschau im Browser
- Automatische Archivierung

#### 4.2 Archiv-Funktionen

**Dokumenten-Historie**:
- Alle Versionen eines Belegs
- Änderungsdatum und -uhrzeit
- Bearbeiter-Informationen

**Integritätsprüfung**:
- SHA-256 Hash-Verifikation
- Automatische Korruptions-Erkennung
- Wiederherstellung aus Backup

**Archiv-Suche**:
- Nach Belegnummer suchen
- Nach Datum filtern
- Nach Bearbeiter filtern

#### 4.3 Beleg-Verifikation

**QR-Code Verifikation**:
1. **QR-Code scannen**
   - Auf gedruckten Belegen
   - Öffnet Verifikations-Seite

2. **Automatische Prüfung**
   - ✅ Integrität OK
   - ✅ Hash übereinstimmt
   - ✅ Beleg existiert

3. **Verifikations-Ergebnis**
   - Grüne/rote Status-Anzeige
   - Detaillierte Informationen
   - Zeitstempel der Prüfung

### 5. Benutzeroberfläche (User Interface)

#### 5.1 Navigation

**Hauptmenü**:
- **Dashboard**: Übersicht und KPIs
- **Sales**: Verkaufsbelege verwalten
- **Purchasing**: Einkaufsprozesse
- **Inventory**: Lager und Warenbewegungen
- **Reports**: Berichte und Analysen

**Schnellzugriff**:
- Globale Suche (Strg+K)
- Letzte Belege
- Favoriten

#### 5.2 Formulare und Eingabe

**Intelligente Formulare**:
- **Auto-Lookup**: Automatische Vervollständigung
- **Prefill**: Automatische Vorbelegung
- **Validation**: Echtzeit-Prüfung der Eingaben

**Tastenkürzel**:
- `Strg+S`: Speichern
- `Strg+N`: Neu
- `F1`: Hilfe
- `Esc`: Abbrechen

#### 5.3 Echtzeit-Features

**Live-Updates**:
- Status-Änderungen ohne Neuladen
- Neue Benachrichtigungen
- System-Status-Anzeige

**Offline-Modus**:
- Lokale Speicherung bei Netzwerkausfall
- Automatische Synchronisation bei Wiederherstellung
- Konfliktlösung bei parallelen Änderungen

### 6. Berichte und Analysen (Reports & Analytics)

#### 6.1 Standard-Berichte

**Verkaufsberichte**:
- Umsatz nach Kunde/Artikel/Zeitraum
- Offene Aufträge und Lieferungen
- Zahlungseingänge und -ausstände

**Einkaufsberichte**:
- Bestellübersicht
- Lieferanten-Performance
- Lagerbestands-Entwicklung

**Workflow-Berichte**:
- Genehmigungszeiten
- Ablehnungsgründe
- Prozess-Effizienz

#### 6.2 Dashboard

**KPI-Anzeige**:
- Monatlicher Umsatz
- Offene Positionen
- Durchschnittliche Bearbeitungszeiten
- System-Performance

**Realtime-Metriken**:
- Aktive Benutzer
- Laufende Workflows
- System-Status

### 7. Fehlerbehebung (Troubleshooting)

#### 7.1 Häufige Probleme

**"Beleg kann nicht gespeichert werden"**
```
Mögliche Ursachen:
- Pflichtfelder nicht ausgefüllt
- Policy-Verletzung (z.B. Betragsgrenze)
- Netzwerkunterbrechung

Lösung:
- Alle roten Felder ausfüllen
- Policy-Warnungen beachten
- Erneut versuchen oder Administrator kontaktieren
```

**"Freigabe-Button nicht verfügbar"**
```
Mögliche Ursachen:
- Unzureichende Berechtigungen
- Policy-Blockade
- Beleg im falschen Status

Lösung:
- Status prüfen
- Bei Bedarf Administrator um Berechtigung bitten
- Policy-Anforderungen erfüllen
```

**"PDF-Druck funktioniert nicht"**
```
Mögliche Ursachen:
- Netzwerkproblem
- Druck-Server nicht erreichbar
- Korrupte Belegdaten

Lösung:
- Seite neu laden
- Später erneut versuchen
- Administrator informieren bei Dauerhaftigkeit
```

#### 7.2 Support kontaktieren

**Bei technischen Problemen**:
- Support-Ticket erstellen
- Screenshot der Fehlermeldung beifügen
- Browser und Betriebssystem angeben

**Bei fachlichen Fragen**:
- Abteilungsleiter informieren
- Prozessverantwortlichen kontaktieren
- Schulungsunterlagen konsultieren

### 8. Best Practices

#### 8.1 Dateneingabe

**Qualität vor Quantität**:
- Alle Felder sorgfältig ausfüllen
- Automatische Vorschläge nutzen
- Rechtschreibung beachten

**Konsistente Daten**:
- Einheitliche Namensgebung
- Standardisierte Adressen
- Vollständige Kontaktdaten

#### 8.2 Workflow-Management

**Zeitnahe Bearbeitung**:
- Aufträge zeitnah freigeben
- Eskalationen vermeiden
- Kommunikation mit Anforderern

**Qualitätssicherung**:
- Daten vor Freigabe prüfen
- Unklarheiten klären
- Vollständigkeit sicherstellen

#### 8.3 Sicherheit

**Passwort-Management**:
- Starke Passwörter verwenden
- Regelmäßig ändern
- Nicht teilen

**Datenschutz**:
- Nur berechtigte Daten einsehen
- Vertrauliche Informationen schützen
- Bei Unsicherheiten nachfragen

### 9. Tastenkürzel-Referenz

| Aktion | Windows/Linux | Mac |
|--------|---------------|-----|
| Speichern | Strg+S | Cmd+S |
| Neu | Strg+N | Cmd+N |
| Suchen | Strg+F | Cmd+F |
| Hilfe | F1 | F1 |
| Abbrechen | Esc | Esc |
| Nächstes Feld | Tab | Tab |
| Vorheriges Feld | Shift+Tab | Shift+Tab |
| Globale Suche | Strg+K | Cmd+K |

### 10. Glossar

**Belegfluss**: Der Prozess von der Belegerstellung bis zur Buchung
**Workflow**: Genehmigungsprozess mit Statusübergängen
**Policy**: Geschäftsregel zur automatischen Prüfung
**Lookup**: Automatische Vervollständigung bei der Eingabe
**Prefill**: Automatische Vorbelegung von Feldern
**Freigabe**: Genehmigung eines Belegs durch berechtigte Person
**Archiv**: Versionierte Speicherung von PDF-Dokumenten
**Verifikation**: Integritätsprüfung von archivierten Belegen