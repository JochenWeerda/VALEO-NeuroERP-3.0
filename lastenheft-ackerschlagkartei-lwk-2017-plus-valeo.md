# Lastenheft Ackerschlagkartei – VALEO NeuroERP 3.0

**Vorlage:** Bedienungshandbuch „Ackerschlagkartei“ der Landwirtschaftskammer Niedersachsen, Ausgabe 2017
**Zielsystem:** VALEO NeuroERP 3.0
**Dokumenttyp:** Lastenheft aus Sicht des Auftraggebers
**Stand:** 16. Juli 2026
**Ziel:** Weiterentwicklung des bestehenden Agrarbereichs zu einer modernen, revisionssicheren, mobilen und integrierten Ackerschlagkartei
**Prioritäten:** MUSS / SOLL / KANN

---

## 0. Dokumentzweck

Dieses Lastenheft beschreibt die Anforderungen an eine vollständige Ackerschlagkartei innerhalb von VALEO NeuroERP 3.0.

Die fachliche Grundstruktur folgt in derselben Reihenfolge dem Handbuch 2017 der Landwirtschaftskammer Niedersachsen:

1. Anfangsbildschirm
2. Betrieb
3. Stammdaten
4. Dünger
5. Pflanzenschutzmittel
6. Anwender
7. Kulturen
8. Technik
9. Maßnahmen und Begründungen
10. Anbauplanung
11. ANDI-Übernahme
12. Schlagbearbeitung
13. Aussaat
14. Schlaginformation
15. Nmin
16. Bodenuntersuchung
17. Düngung und Düngebedarf
18. Pflanzenschutz
19. Beregnung
20. Ernte
21. Qualitätssicherung
22. Umwelt- und Agrarumweltmaßnahmen
23. Übersichten und Auswertungen
24. Datensicherung

Die Funktionen des Handbuchs werden nicht bloß kopiert, sondern in ein modernes, mandantenfähiges ERP-Zielbild überführt. Ergänzt werden insbesondere:

- Cloud- und Offlinefähigkeit
- mobile App
- GIS und Feldkarten
- GeoJSON-, Shape- und Förderantragsimporte
- NÄON-/ENNI- und Nährstoffmanagementintegration
- elektronische Pflanzenschutzaufzeichnungen
- Dokumentation integrierten Pflanzenschutzes
- Betriebsmittel- und Lagerintegration
- Auftrags- und Arbeitswirtschaft
- Telemetrie und Maschinendaten
- Precision Farming
- Satelliten- und Wetterdaten
- Nachhaltigkeits- und Klimakennzahlen
- Audit, Versionierung und Freigaben
- KI-Assistenz mit menschlicher Kontrolle

---

# 1. Produktvision

VALEO NeuroERP soll eine Ackerschlagkartei bereitstellen, die den vollständigen Lebenszyklus eines Schlages und eines Anbaujahres abbildet:

> Betrieb anlegen → Stammdaten auswählen → Flächen übernehmen → Anbau planen → Maßnahmen planen → Arbeiten mobil dokumentieren → Betriebsmittel verbrauchen → gesetzliche Vorgaben prüfen → Ernte und Erlöse erfassen → Kosten und Leistungen auswerten → Meldungen und Nachweise erzeugen.

Das System soll nicht nur ein digitales Formulararchiv sein, sondern ein integriertes landwirtschaftliches Produktions-, Dokumentations- und Controllingsystem.

---

# 2. Zielgruppen

- Landwirte und Betriebsleiter
- Pflanzenbauleiter
- Mitarbeiter und Maschinenführer
- Lohnunternehmen
- Agrarberater
- Pflanzenschutzberater
- Wasserschutz- und Düngeberater
- Buchhaltung und Controlling
- Qualitätsmanagement
- Handel und Genossenschaften
- Auditoren mit temporärem Lesezugriff
- Behördenexporte und Meldesysteme über Schnittstellen

---

# 3. Leitprinzipien

## MUSS

1. **Einmalige Datenerfassung:** Stammdaten, Schläge, Betriebsmittel und Personen werden nur einmal angelegt und systemweit verwendet.
2. **Schlagbezogene Nachvollziehbarkeit:** Jede Maßnahme ist eindeutig einem Schlag, Zeitraum, Kulturzyklus und Wirtschaftsjahr zugeordnet.
3. **Zeitliche Gültigkeit:** Stammdaten und Rechtsregeln werden versioniert.
4. **Revisionssicherheit:** Änderungen und Löschungen bleiben nachvollziehbar.
5. **Mandantentrennung:** Betriebe und Beratungskunden sind technisch und fachlich getrennt.
6. **Offlinefähigkeit:** Feldarbeit muss bei schlechter Mobilfunkversorgung möglich sein.
7. **Mobile First für Außeneinsatz, Desktop First für Planung und Auswertung.**
8. **Keine stille Automatik:** Automatisch vorgeschlagene Daten müssen als solche erkennbar sein.
9. **Gesetzliche Prüfung ist versionsbezogen:** Das System dokumentiert, nach welchem Regelstand geprüft wurde.
10. **Integrierter ERP-Fluss:** Maßnahmen können Bestände, Kosten, Aufträge, Arbeitszeiten und Maschinenstunden fortschreiben.

---

# 4. Rollen und Berechtigungen

| Rolle | Rechte |
|---|---|
| Betriebsinhaber | Vollzugriff auf eigenen Betrieb |
| Betriebsleiter | Planung, Freigabe, Auswertung |
| Mitarbeiter | zugewiesene Maßnahmen ansehen und erfassen |
| Pflanzenschutz-Anwender | Maßnahmen dokumentieren, Sachkunde nachweisen |
| Berater | je nach Mandat lesen, planen oder bearbeiten |
| Lohnunternehmer | beauftragte Maßnahmen und Flächen bearbeiten |
| Auditor | zeitlich begrenzter Lese- und Exportzugriff |
| Administrator | Stammdaten, Regeln und Schnittstellen verwalten |

## MUSS

- Rechte je Betrieb, Betriebsstätte, Schlag, Modul und Vorgang
- getrennte Rechte für Lesen, Planen, Ausführen, Korrigieren, Freigeben und Exportieren
- temporäre Zugriffsfreigaben
- Protokollierung aller Freigaben
- Vier-Augen-Prinzip konfigurierbar
- Sachkundenachweis als Voraussetzung für freigabepflichtige Pflanzenschutzmaßnahmen

---

# 5. Anfangsbildschirm und Arbeitskontext

Der Benutzer muss auswählen oder erkennen können:

- aktiver Mandant
- Betrieb
- Betriebsstätte
- Wirtschaftsjahr
- Erntejahr
- Kampagne
- Benutzerrolle
- aktive Kulturperiode
- Datenstand und Synchronisationsstatus

## Dashboard

- offene und überfällige Maßnahmen
- heutige Arbeitsaufträge
- Wetterwarnungen
- ablaufende Pflanzenschutz-Wartezeiten
- Dünge- und Pflanzenschutzfristen
- fehlende Pflichtangaben
- Schläge mit Dokumentationslücken
- offene Freigaben
- aktuelle Bestände wichtiger Betriebsmittel
- jüngste Import- und Synchronisationsfehler
- anstehende Ernten
- Compliance-Risiken

## SOLL

- persönliche Favoriten
- zuletzt geöffnete Schläge
- kartenbasierter Einstieg
- kontextabhängige Schnellaktionen
- rollenabhängige Startseite

---

# 6. Betriebsstamm

## MUSS-Felder

- Betriebsnummer
- Unternehmens-/Geschäftspartnerbezug
- Name
- Rechtsform
- Anschrift
- Kommunikationsdaten
- Betriebsstätten
- Registrier- und Förderkennungen
- Bundesland
- Landkreis
- Beratungszuordnung
- Zertifizierungen
- Bewirtschaftungsform
- Tierhaltung
- Wasserschutz- und Kulissenbezug
- Wirtschaftsjahr
- Zeitzone und Locale

## MUSS-Funktionen

- neuen Betrieb anlegen
- Betrieb bearbeiten
- Betrieb archivieren
- mehrere Betriebe je Benutzer
- Betrieb aus CRM übernehmen
- Adress- und Ansprechpartnerdaten synchronisieren
- Betrieb kopieren, ohne Bewegungsdaten zu duplizieren
- Wirtschaftsjahr wechseln
- Historie anzeigen
- Stammdatenvollständigkeit prüfen

## Akzeptanz

Ein Betrieb kann erst als „produktiv eingerichtet“ markiert werden, wenn alle konfigurierten Pflichtstammdaten vollständig sind.

---

# 7. Stammdatenübersicht

## Stammdatenkategorien

- Düngemittel
- Pflanzenschutzmittel
- Saatgut und Sorten
- Kulturen
- Anwender und Mitarbeiter
- Maschinen und Geräte
- Arbeitsverfahren
- Maßnahmenarten
- Pflanzenschutzbegründungen
- Bewässerungsverfahren
- Ernte- und Qualitätsparameter
- Bodenarten
- Bodenuntersuchungsparameter
- Umwelt- und QS-Kriterien
- Lieferanten, Kunden und Lohnunternehmer

## MUSS

- zentraler Stammdatenkatalog
- betriebliche Auswahl aus Referenzkatalog
- nur ausgewählte Betriebsmittel in operativen Dropdowns
- gültig-von/gültig-bis
- Herkunft und Datenquelle
- lokale Ergänzungen
- Sperrung veralteter Einträge
- Dublettenprüfung
- Import und Export
- Sortieren, Filtern, Gruppieren und Spaltenkonfiguration

---

# 8. Düngemittelstamm

## MUSS-Felder

- Produktname
- Artikelnummer
- Hersteller/Lieferant
- Kategorie
- mineralisch/organisch
- fest/flüssig
- Einheit
- Dichte
- N gesamt
- NH4-N
- NO3-N
- organischer N
- P2O5
- K2O
- MgO
- CaO
- S
- sonstige Nährstoffe
- Anrechenbarkeiten
- Wirksamkeitsfaktoren
- Preis und Preisgültigkeit
- Lagerartikelbezug
- Gefahrstoff- und Sicherheitsdaten
- Zulässigkeit/Status
- Gültigkeitszeitraum

## Funktionen

- Referenzwert übernehmen
- betrieblichen Analysewert hinterlegen
- Nährstoffgehalte versionsbezogen ändern
- Preis aus Einkauf übernehmen
- Lagerbestand anzeigen
- Kosten je ha und Maßnahme berechnen
- Reinnährstoffmengen automatisch berechnen
- organische und mineralische N-Mengen getrennt auswerten
- Produkt gegen rechtliche und betriebliche Grenzen prüfen

## SOLL

- Wirtschaftsdüngeranalyse
- Lieferantenanalyse
- Chargenbezug
- Sperrfristprüfung
- Lagerkapazität
- Anfall- und Abgabemengen
- Nährstofftransport
- Stoffstrombilanzbezug
- ENNI-/NÄON-Datenaustausch

---

# 9. Pflanzenschutzmittelstamm

## MUSS-Felder

- Handelsname
- Zulassungsnummer
- Wirkstoffe und Wirkstoffgehalte
- Zulassungsinhaber
- Mittelart
- Wirkungskategorien
- zugelassene Kulturen und Anwendungen
- Aufwandmenge min/max
- Anwendungshäufigkeit
- Wartezeit je Kultur/Anwendung
- Abstandsauflagen
- Gewässerauflagen
- Bienenschutz
- Hangneigung und Abschwemmung
- Anwendungsbestimmungen
- Resistenzgruppe
- Zulassungsbeginn und -ende
- Abverkaufsfrist
- Aufbrauchfrist
- Preis
- Einheit
- Lagerartikel
- Sicherheitsdatenblatt

## MUSS-Funktionen

- tagesaktuelle Zulassungsprüfung über versionierte Datenquelle
- Prüfung Kultur × Schadorganismus × Stadium × Aufwandmenge
- Prüfung maximaler Anwendungen
- Prüfung kumulierter Wirkstoffmenge
- Prüfung Wartezeit vor Ernte
- Prüfung Abstände und Kulissen
- Kennzeichnung von Teil- und Randbehandlung
- Kostenberechnung nach Herbizid/Fungizid/Insektizid/sonstige
- Dokumentation der Begründung
- Anwender und Gerät verpflichtend
- Sperre oder begründete Übersteuerung je Regelklasse
- Speicherung der zum Anwendungszeitpunkt gültigen Produktversion

## Trend-Ergänzung

Elektronische Aufzeichnungen müssen maschinenlesbar, exportierbar und zeitnah erfasst werden können. Das System soll strukturierte Pflanzenschutzdatensätze mit eindeutiger Flächen-, Kultur-, Produkt-, Anwender-, Zeit- und Mengenreferenz erzeugen.

---

# 10. Anwender und Mitarbeiter

## MUSS-Felder

- Person
- Personalnummer
- Rolle
- Kontaktdaten
- Beschäftigungszeitraum
- Pflanzenschutz-Sachkundenummer
- Gültigkeit der Sachkunde
- Fortbildungsnachweise
- Maschinenberechtigungen
- digitale Unterschrift optional
- externer Dienstleister/Lohnunternehmer

## MUSS

- jede Pflanzenschutz- und Düngemaßnahme einer ausführenden Person zuordnen
- Ablaufwarnungen für Nachweise
- Sperre bei fehlender Berechtigung, soweit fachlich erforderlich
- Mitarbeiter aus HR übernehmen
- Arbeitszeit erfassen
- Verantwortlichen und Ausführenden getrennt speichern

---

# 11. Kulturen und Kulturcodes

## MUSS

- Kulturcode
- Bezeichnung
- Haupt-/Neben-/Zwischenfrucht
- Nutzungsart
- Kulturgruppe
- Gültigkeitsjahr
- Fördercode
- Ernteprodukt
- Standard-Ertrag
- Qualitätsparameter
- Nährstoffbedarf
- Entzüge
- zulässige Pflanzenschutzanwendungen
- Fruchtfolgeklassifikation
- Saat- und Erntefenster
- BBCH-/Entwicklungsstadien

## Funktionen

- jährliche Kulturcode-Aktualisierung
- Mapping alter auf neue Codes
- Warnung bei ungültigem Code
- betriebliche Kulturen auswählen
- kulturabhängige Düngebedarfsparameter
- Ertragsniveau und Qualitätsziel pflegen
- Zwischenfrüchte und Untersaaten abbilden
- Mehrfachnutzung und Doppelkultur unterstützen

---

# 12. Technik, Maschinen und Geräte

## MUSS-Felder

- Maschine/Gerät
- Kategorie
- Kennzeichen/Inventarnummer
- Eigentümer
- Arbeitsbreite
- Tank-/Behältergröße
- Leistungsdaten
- Verbrauch
- Kosten je Stunde/ha
- Prüfpflichten
- Pflanzenschutzgerätekontrolle und Gültigkeit
- GPS-/ISOBUS-Fähigkeit
- Telemetriekennung
- Bedienberechtigungen

## Funktionen

- Zuordnung zu Maßnahme
- Maschinenstunden
- Diesel- und Energiekosten
- Abschreibung oder Verrechnungssatz
- Wartungsstatus
- Prüfstatus
- Lohnunternehmertechnik
- automatische Datenübernahme aus Telemetrie

## SOLL

- ISOXML/Taskdata
- ISOBUS-Auftragsdaten
- Maschinenpositionsdaten
- tatsächlich bearbeitete Fläche
- Applikationskarten
- Teilbreitenschaltung
- dokumentierte Ausbringmenge

---

# 13. Maßnahmenarten und Begründungen

## MUSS-Maßnahmenarten

- Bodenbearbeitung
- Aussaat
- Düngung
- Pflanzenschutz
- mechanische Pflege
- Beregnung
- Bonitur
- Probenahme
- Ernte
- Transport
- Nachernte
- Umweltmaßnahme
- sonstige Tätigkeit

## Pflanzenschutzbegründungen

- Befall/Schadschwelle
- Beratungsempfehlung
- Prognosemodell
- Monitoring/Bonitur
- Resistenzmanagement
- vorbeugende Maßnahme, soweit zulässig
- amtlicher Hinweis
- andere dokumentierte Begründung

## SOLL: Integrierter Pflanzenschutz

- Beobachtung und Befallsstärke
- Schadschwelle
- alternative nichtchemische Maßnahmen
- Prognose-/Warndienst
- Wirkstoffwechsel
- Resistenzstrategie
- Entscheidung und Begründung
- Behandlungserfolg

---

# 14. Anbauplanung

## MUSS je Wirtschaftsjahr und Schlag

- Schlagnummer
- Schlagname
- Fläche
- Feldblock/Flächenkennung
- Hauptfrucht
- Sorte
- Saatgutkategorie
- Vorfrucht
- Zwischenfrucht
- Untersaat
- geplanter Aussaattermin
- geplante Ernte
- Produktionsverfahren
- Zertifizierungsprogramm
- Bewirtschaftungsauflagen
- erwarteter Ertrag
- Vertrags-/Abnehmerbezug

## Funktionen

- manuelle Anlage
- Vorjahresübernahme
- Sammelbuchung
- Kopieren
- Massenänderung
- Flächenabgleich
- Fruchtfolgeübersicht
- Plausibilitätsprüfung
- Anbauumfang je Kultur
- Saatgutbedarf
- Dünge- und Pflanzenschutzplanung
- Deckungsbeitragsvorschau

## SOLL

- graphische Fruchtfolge
- Planung mehrerer Szenarien
- Kulturflächenziel
- Kontrakt- und Vermarktungsbedarf
- Saatgutverfügbarkeit
- Arbeitskapazität
- Risikoverteilung
- Greening-/Öko-Regelprüfung

---

# 15. Förderantrags- und Flächenimport

## MUSS

- Import aktueller niedersächsischer Förderantragsdaten
- Feldblöcke, Schläge, Teilschläge, Geometrien, Flächen und Kulturcodes
- Importvorschau
- Dublettenvermeidung
- einmalige und wiederholbare Imports
- Änderungsabgleich statt blinder Neuanlage
- Konfliktanzeige
- Mapping unbekannter Codes
- Protokoll mit übernommenen, geänderten und verworfenen Datensätzen
- Rückgängig-Funktion
- ursprüngliche Importdatei archivieren

## Formate

- XML
- CSV
- GeoJSON
- Shape
- GML
- weitere amtliche Austauschformate

## Akzeptanz

Ein erneuter Import derselben Datei erzeugt keine doppelten Schläge.

---

# 16. GIS und Schlaggeometrien

## MUSS

- interaktive Karte
- Schlagpolygon
- Teilschlagpolygon
- Flächenberechnung
- Satelliten-/Luftbildhintergrund
- Feldblockgrenzen
- Bearbeiten und Teilen von Geometrien
- Puffer- und Abstandszonen
- Messwerkzeuge
- Standort des Benutzers
- Offline-Karten
- GeoJSON-Import/Export

## SOLL

- Gewässer
- Schutzgebiete
- Wasserschutzgebiete
- Naturschutzkulissen
- Hangneigung
- Bodenkarte
- Erosionsgefährdung
- Nitratkulissen
- Wetterstationen
- Nmin-Regionen
- Ertragskarten
- Bodenprobenraster
- Applikationskarten
- Sentinel-Satellitendaten
- Vegetationsindizes
- Biomassezonen
- automatische Flächenabweichungswarnung

---

# 17. Schlag-ObjectPage

## Kopfbereich

- Schlagnummer und Name
- Fläche
- Kultur
- Sorte
- Status
- Wirtschaftsjahr
- Betriebsstätte
- Feldblock
- Zertifizierungen
- aktuelle Warnungen

## Register

1. Übersicht
2. Geometrie
3. Anbau/Aussaat
4. Boden und Nmin
5. Düngung
6. Pflanzenschutz
7. Pflege/Bodenbearbeitung
8. Beregnung
9. Bonituren
10. Ernte
11. Kosten/Leistung
12. QS/Umwelt
13. Dokumente
14. Historie

## MUSS

- chronologische Timeline aller Vorgänge
- Plan/Ist-Kennzeichnung
- direkte Navigation von Warnung zu Datensatz
- Sammelbuchung über mehrere Schläge
- Änderung mehrerer markierter Schläge
- Konfliktprüfung
- Druck/Export je Register oder komplett

---

# 18. Aussaat

## MUSS-Felder

- Datum und Uhrzeit
- Schlag/Teilfläche
- Kultur
- Sorte
- Saatgutpartie
- Anerkennungs-/Chargennummer
- Beizung
- Saatmenge
- Einheit
- Reihenabstand
- Ablagetiefe
- Saatstärke
- Keimfähigkeit
- Tausendkornmasse
- Aussaatverfahren
- Maschine
- Anwender
- Wetter und Bodenbedingungen
- mehrere Aussaattermine
- Vorkeimung/Keimstimmung, soweit relevant

## Funktionen

- Saatgutbedarf berechnen
- Saatgutbestand verbrauchen
- Partie rückverfolgen
- Sammelbuchung
- Nachsaat
- Teilflächen
- Kosten buchen
- Arbeitszeit und Maschine buchen
- Foto/Dokument anhängen

---

# 19. Schlaginformation und Gesamtdokumentation

## MUSS

Eine konsolidierte Schlaginformation enthält:

- Stammdaten
- Geometrie
- Anbau
- alle Maßnahmen
- eingesetzte Betriebsmittel
- Anwender
- Maschinen
- Nährstoffgaben
- Pflanzenschutzwirkstoffe
- Wartezeiten
- Boden- und Nmin-Werte
- Ernte
- Erlöse
- Kosten
- direktkostenfreie Leistung
- QS- und Umweltangaben
- Dokumente
- Audit-Historie

## Ausgabe

- Bildschirm
- PDF
- strukturierter Export
- Prüfbericht
- Jahresakte
- ausgewählter Zeitraum
- je Schlag und je ha

---

# 20. Nmin-Untersuchungen

## MUSS

- mehrere Proben je Anbaujahr
- Probenahmedatum
- Tiefe/Schicht
- Einzelwerte
- Gesamtwert
- Labor
- Proben-ID
- Durchschnitts-/Richtwert
- tatsächlicher Messwert
- Kennzeichnung, ob düngebedarfswirksam
- Frühjahr/Herbst/weitere Termine
- Datei/Analysebericht
- Zuordnung zu Schlag oder Bewirtschaftungseinheit

## Funktionen

- Import
- Plausibilitätsprüfung
- Übernahme amtlicher Richtwerte
- versionsbezogene Berechnung
- Wirkung auf Düngebedarf transparent darstellen
- spätere Werte nicht rückwirkend ohne Freigabe einrechnen

---

# 21. Bodenuntersuchungen

## MUSS-Felder

- Probenahmedatum
- Labor
- Proben-ID
- Probenahmetiefe
- Bodenart
- Humus
- pH
- P
- K
- Mg
- weitere Parameter
- Methode
- Gehaltsklasse
- Gültigkeit
- räumliche Probenposition

## Funktionen

- Sammelbuchung
- Laborimport
- PDF-Anhang
- Verlauf
- Kartenansicht
- Düngeempfehlung
- Ablaufwarnung
- Probenplanung
- Probenraster
- Mittelwert und räumliche Streuung

## SOLL

- teilflächenspezifische Grunddüngung
- Applikationskarten
- Bodenleitfähigkeitskarten
- Humus- und Kohlenstoffmonitoring

---

# 22. Standort- und Risikoanalyse

## MUSS

- vorherige Nutzung
- Kontaminationsrisiko
- Überschwemmung
- Erosion
- Nachbarflächen
- Immissionen
- Wasserquellen
- Abfall-/Klärschlammhistorie
- Schadstoffrisiken
- Wildtiere
- Fremdkörper
- Allergene, soweit relevant
- Risikobewertung
- Maßnahmen
- Prüfer
- Datum
- Gültigkeit
- Anhänge
- Freigabe

---

# 23. Düngungsmaßnahmen

## MUSS-Felder

- Datum/Uhrzeit
- Schlag/Teilfläche
- Plan- oder Istmaßnahme
- Düngemittel
- Charge/Lager
- Aufwandmenge
- Einheit
- Fläche
- Nährstoffmengen
- organisch/mineralisch
- Verfahren
- Maschine
- Anwender
- Witterung
- Bodenbedingungen
- Entwicklungsstadium
- Begründung
- Kosten

## Automatische Berechnungen

- Gesamtproduktmenge
- kg N gesamt/ha
- verfügbare N-Menge
- P2O5, K2O, MgO, S
- Kosten/ha
- Gesamtkosten
- verbleibender Bedarf
- betriebliche Obergrenzen
- organische N-Summen
- kumulierte Jahresmengen

## MUSS-Prüfungen

- Düngebedarf
- Sperrfrist
- Aufnahmefähigkeit des Bodens
- Abstände
- Hang/Erosion
- Gewässer
- Obergrenzen
- zulässige Menge
- Dokumentationsfrist
- betriebliche und schlagbezogene Grenzwerte

## SOLL

- NÄON/ENNI-Export
- Stoffstrombilanz
- Lager- und Wirtschaftsdüngermanagement
- Teilflächenapplikation
- Sensor-/Maschinendaten
- automatische Istmengen aus ISOBUS

---

# 24. Düngebedarfsermittlung und Düngeplanung

## MUSS

- kultur- und ertragsabhängiger Bedarf
- Nmin
- Vorfrucht
- Zwischenfrucht
- organische Vorjahreswirkung
- Bodenhumus
- Bewässerung
- Standort
- Ertragsniveau
- Qualitätsziel
- Zu- und Abschläge
- bereits erfolgte Gaben
- verbleibender Bedarf
- Regelversion
- Berechnungsnachweis
- Freigabe
- Änderungsvergleich

## Integration

Die LWK beschreibt NÄON als gemeinsame Desktop-/App-Lösung für Düngebedarf, Düngeplanung, 170-kg-N-Obergrenze, Ackerschlagkartei, Stoffstrombilanz, ENNI-Meldungen sowie ANDI- und Labordatenimporte. Dieses Zielbild ist mindestens funktional abzudecken.

## SOLL

- Planvarianten
- Betriebsmittelverfügbarkeit
- Kostenoptimierung
- Nährstoffeffizienz
- teilflächenspezifische Planung
- Wetter-/Bodenfeuchtebezug
- automatische Plan-Ist-Fortschreibung
- Beratung und Vier-Augen-Freigabe

---

# 25. Pflanzenschutzmaßnahmen

## MUSS-Felder

- Datum und Uhrzeit
- Schlag/Teilfläche
- Kultur und Stadium
- Schadorganismus/Indikation
- Befall/Schadschwelle
- Produkt
- Zulassungsnummer
- Aufwandmenge
- Wasseraufwand
- behandelte Fläche
- Rand-/Teilflächenbehandlung
- Anwender
- Gerät
- Witterung
- Wind
- Temperatur
- Begründung
- Beratung/Prognosequelle
- Wartezeit
- Abstände und Auflagen
- Kosten
- Ergebnis/Wirksamkeitskontrolle

## MUSS-Prüfungen

- Zulassung am Anwendungstag
- Kultur
- Indikation
- Aufwandmenge
- Anwendungshäufigkeit
- Wirkstoffsummen
- Wartezeit
- Bienenschutz
- Gewässer
- Abdriftminderung
- Hangneigung
- Schutzgebiete
- Anwendersachkunde
- Geräteprüfung
- Mittelbestand

## SOLL

- digitale Feldfreigabe vor Anwendung
- Wetterfenster
- Resistenzmanagement
- Prognosemodelle
- Warndienste
- Foto-/Boniturbezug
- elektronische Aufzeichnungsexporte
- automatische Istübernahme aus Maschine
- Behandlungserfolg und Nachkontrolle

---

# 26. Bodenbearbeitung und Pflege

## MUSS

- Arbeitsart
- Datum
- Fläche
- Tiefe
- Intensität
- Maschine
- Anwender
- Arbeitszeit
- Diesel/Energie
- Kosten
- Bodenbedingungen
- Plan/Ist
- Teilfläche

## Maßnahmen

- Pflügen
- Grubbern
- Scheibenegge
- Saatbettbereitung
- Walzen
- Striegeln
- Hacken
- Mulchen
- Pflegemaßnahmen
- mechanische Unkrautbekämpfung

## SOLL

- CO₂- und Energieauswertung
- Bodenschutzbewertung
- Erosionsrisiko
- Fahrspuren und Befahrbarkeit
- Controlled Traffic Farming

---

# 27. Beregnung und Bewässerung

## MUSS-Felder

- Datum
- Schlag/Teilfläche
- Bewässerungsart
- Wassermenge
- Quelle
- Wasserqualität
- Kulturstadium
- Gerät
- Anwender
- Dauer
- Kosten
- Genehmigungsbezug

## SOLL

- Wasserentnahmekonto
- Genehmigungsgrenzen
- Bodenfeuchte
- Wetterprognose
- Evapotranspiration
- Beregnungsempfehlung
- Sensorintegration
- automatische Dokumentation
- Wasserfußabdruck

---

# 28. Ernte

## MUSS-Felder

- Erntedatum
- Schlag/Teilfläche
- Produkt
- Menge
- Einheit
- Fläche
- Feuchte
- Qualität
- Lager/Ziel
- Kunde/Vertrag
- Erlös
- Nebenleistung
- Stroh/Nebenprodukt
- Verlust/Schaden
- Maschine
- Anwender/Lohnunternehmer
- mehrere Erntetermine/Schnitte

## Funktionen

- Gesamt- und Hektarertrag
- Teilflächenernte
- Wiegescheinbezug
- Lagerzugang
- Chargenbildung
- Rückverfolgbarkeit
- Qualitätsabrechnung
- Vertragszuordnung
- Erlös
- Nebenleistung
- Erntekosten
- Schadensdokumentation

## SOLL

- Waagenintegration
- Telematik/Ertragskarte
- automatische Mengenabgleiche
- Feuchte- und Qualitätsdaten
- Transportlogistik
- Lagerplanung
- CO₂-Fußabdruck je Ernteprodukt

---

# 29. QS-, GLOBALG.A.P.- und Auditdokumentation

## MUSS

Konfigurierbare Prüfkataloge für:

- QS
- QS-GAP
- GLOBALG.A.P.
- Kartoffeln
- Obst und Gemüse
- Drusch- und Hackfrüchte
- individuelle Kundenvorgaben
- interne Betriebsaudits

## Funktionen

- Checklisten
- Pflichtnachweise
- Dokumente
- Fotos
- Abweichungen
- Korrekturmaßnahmen
- Verantwortliche
- Fristen
- Freigabe
- Auditbericht
- historischer Regelstand
- Nachweispaket je Betrieb/Schlag/Jahr

---

# 30. Umwelt- und Agrarumweltmaßnahmen

## MUSS

- Programm/Maßnahme
- Verpflichtungszeitraum
- betroffene Flächen
- Auflagen
- Termine
- zulässige/verbotene Maßnahmen
- Nachweise
- Dokumente
- Kontrollen
- Abweichungen
- jährliche Regelversion

## Beispiele

- Gewässerrandstreifen
- Erosionsschutz
- Zwischenfrüchte
- reduzierte Düngung
- Verzicht auf Betriebsmittel
- Blühflächen
- Biodiversitätsmaßnahmen
- Wasserschutzkooperationen
- Vertragsnaturschutz

## SOLL

- Kulissenimport
- automatische Konfliktprüfung
- Maßnahmenkalender
- Prämien-/Erlösbezug
- Biodiversitätskennzahlen

---

# 31. Sammelbuchung und Massenbearbeitung

## MUSS

- mehrere Schläge auswählen
- gemeinsame Maßnahme vorbereiten
- individuelle Flächen berücksichtigen
- Mengen wahlweise je ha oder gesamt
- Vorschau je Schlag
- Konflikte vor Speicherung
- Teilerfolg vermeiden oder transparent behandeln
- atomare Buchung, soweit möglich
- Massenkorrektur
- Massenfreigabe
- Audit pro Schlag

---

# 32. Aufgaben und mobile Durchführung

## MUSS

- geplante Maßnahme als Arbeitsauftrag
- Zuständiger
- Termin
- Maschine
- Betriebsmittel
- Zielschläge
- mobile Checkliste
- Start/Pause/Abschluss
- Istmenge
- tatsächlich bearbeitete Fläche
- Abweichungsgrund
- Foto
- GPS-Zeitstempel optional
- Unterschrift optional
- Offline-Erfassung
- spätere Synchronisation

## SOLL

- Touren-/Routenplanung
- Lohnunternehmerportal
- Push-Nachrichten
- wetterbedingte Umplanung
- Kapazitätsplanung
- automatische Materialreservierung

---

# 33. Bestände, Einkauf und Kosten

## MUSS

Ackerschlagmaßnahmen müssen mit VALEO ERP verknüpft werden können:

- Artikel
- Lager
- Charge
- Einkauf
- Preis
- Reservierung
- Verbrauch
- Rückgabe
- Inventur
- Lieferant
- Kostenstelle
- Kostenträger Schlag/Kultur/Jahr

## Ergebnisse

- Saatgutkosten
- Düngerkosten
- Pflanzenschutzkosten
- Maschinenkosten
- Lohnkosten
- Lohnunternehmer
- Beregnungskosten
- Erntekosten
- sonstige direkte Kosten
- Erlöse
- Nebenleistungen
- direktkostenfreie Leistung
- Deckungsbeitrag, sofern konfiguriert

---

# 34. Auswertungen

## MUSS

- Schlagliste
- Kulturflächenübersicht
- Maßnahmenjournal
- Düngejournal
- Pflanzenschutzjournal
- Wirkstoffübersicht
- Wartezeiten
- Nährstoffsummen
- organische/mineralische Düngung
- Saatgutverbrauch
- Betriebsmittelverbrauch
- Ernteerträge
- Qualitäten
- Kosten
- Erlöse
- direktkostenfreie Leistung
- je Schlag
- je ha
- je Kultur
- je Betrieb
- je Wirtschaftsjahr
- Plan/Ist

## SOLL

- Fruchtfolgevergleich
- Mehrjahrestrends
- Benchmarking
- Nährstoffeffizienz
- Pflanzenschutzintensität
- Energie
- CO₂
- Wasser
- Humus
- Biodiversität
- Karten und Heatmaps
- Drill-down bis zum Einzelbeleg

---

# 35. Berichte und Exporte

## MUSS

- PDF
- CSV
- Excel
- maschinenlesbare Schnittstelle
- Einzelschlagdokumentation
- gesamter Betrieb
- frei wählbarer Zeitraum
- Filter
- Regelstand
- Erstellungsdatum
- Benutzer
- Versionsnummer
- Signatur/Freigabe
- QR- oder Prüfreferenz optional

## Standardberichte

1. Anbauplan
2. Schlagstamm
3. Aussaat
4. Düngung
5. Düngebedarf
6. Pflanzenschutz
7. Beregnung
8. Ernte
9. QS/Audit
10. Umweltmaßnahmen
11. Kosten/Leistung
12. vollständige Jahresakte
13. Kontroll-/Prüferpaket
14. ENNI-/Nährstoffexport
15. elektronisches Pflanzenschutzjournal

---

# 36. Jahreswechsel

## MUSS

- neues Wirtschaftsjahr
- Vorjahresschläge übernehmen
- Geometrien übernehmen
- Stammdaten übernehmen
- aktuelle Kulturcodes laden
- Fruchtfolge fortschreiben
- offene Dauerkulturen übernehmen
- mehrjährige Maßnahmen übernehmen
- keine Bewegungsdaten duplizieren
- Vorschau
- Protokoll
- Rückgängig
- Archiv des Vorjahrs

---

# 37. Datensicherung, Versionierung und Wiederherstellung

## MUSS

- automatische Backups
- verschlüsselte Sicherung
- Point-in-Time-Wiederherstellung
- Mandantenexport
- Wiederherstellungstest
- Aufbewahrungsregeln
- Audit
- unveränderliche freigegebene Berichte
- Versionierung von Anbauplänen, Maßnahmen und Regelständen
- Konfliktauflösung bei Offline-Synchronisation
- Export eines vollständigen Betriebsarchivs

## SOLL

- lokales Notfallpaket
- revisionssicheres Dokumentenarchiv
- manipulationsgeschützte Prüfsummen
- Restore-Selbsttest

---

# 38. Integrationen

## MUSS-Zielintegrationen

- VALEO CRM/Geschäftspartner
- Artikelstamm
- Einkauf
- Verkauf
- Lager
- Chargen
- Waage
- Finanz-/Kostenrechnung
- Dokumentenmanagement
- HR/Mitarbeiter
- Workflow/Aufgaben
- ANDI/Förderantrag
- ENNI/NÄON
- Labor
- Wetter

## SOLL

- ISOBUS/ISOXML
- Agrirouter
- Maschinenhersteller
- Farm-Management-Datenaustausch
- Satellitendaten
- Sensorik
- Bodenfeuchte
- Wetterstationen
- Ertragskartierung
- Applikationskarten
- Lohnunternehmerportale

---

# 39. KI-Assistenz

## Zulässige Anwendungen

- Datenlücken erkennen
- Plausibilitätsfehler erklären
- Maßnahmenentwurf
- Berichtsformulierung
- Import-Mapping
- alternative Betriebsmittel vorschlagen
- Wetter- und Terminrisiken zusammenfassen
- Kosten- und Ertragsabweichungen erklären
- Compliance-Check erläutern
- Such- und Navigationshilfe

## MUSS-Grenzen

- keine automatische Freigabe
- keine erfundenen Rechtsregeln
- Quellen und Regelversion nennen
- Vorschläge klar kennzeichnen
- Änderungen als Diff zeigen
- Benutzerbestätigung
- deterministische Berechnung bleibt außerhalb des Sprachmodells
- keine Verwendung vertraulicher Daten in öffentlichen Diensten ohne Freigabe

---

# 40. Nichtfunktionale Anforderungen

## Performance

- Listen serverseitig paginieren
- große Flächenbestände performant darstellen
- Karte schrittweise laden
- typische Maske in maximal 2 Sekunden interaktiv
- Eingaben ohne Vollseiten-Reload
- Imports und große Berichte als Hintergrundjob
- Fortschrittsanzeige

## Accessibility

- WCAG 2.2 AA
- vollständige Tastaturbedienung
- sichtbarer Fokus
- Status nicht nur durch Farbe
- barrierearme Tabellen
- Kartenfunktionen mit textlicher Alternative
- verständliche Fehlermeldungen
- mobile Touch-Ziele

## Sicherheit

- OIDC
- RBAC
- Mandantentrennung
- Audit
- sichere Uploads
- Verschlüsselung
- Schutz vor Massenexport
- Sitzungs- und Geräteverwaltung
- Least Privilege

## Architektur

- FastAPI/Pydantic/SQLAlchemy/Alembic
- React/TypeScript/TanStack Query
- bestehender Mask Builder
- bestehende Design-Tokens
- keine zusätzliche UI-Bibliothek
- Event-Bus für fachliche Ereignisse
- idempotente Imports
- Outbox für kritische Integrationen

---

# 41. Fachliches Datenmodell

Mindestens folgende Aggregate/Entitäten:

- FarmBusiness
- FarmSite
- FieldBlock
- Field
- FieldPart
- FieldGeometryVersion
- CropYear
- CultivationPlan
- CropCycle
- Crop
- Variety
- SeedProduct
- SeedLot
- Fertilizer
- FertilizerAnalysis
- PlantProtectionProduct
- PlantProtectionAuthorizationVersion
- Person
- Qualification
- Machine
- EquipmentInspection
- MeasureType
- MeasureReason
- WorkOrder
- FieldOperation
- SowingOperation
- FertilizationOperation
- PlantProtectionOperation
- TillageOperation
- IrrigationOperation
- HarvestOperation
- SoilSample
- SoilAnalysis
- NminSample
- NutrientRequirementCalculation
- ComplianceRule
- ComplianceFinding
- CertificationScheme
- AuditChecklist
- EnvironmentalCommitment
- InputStockTransaction
- HarvestLot
- CostEntry
- RevenueEntry
- Report
- ImportJob
- ExportJob
- AuditEvent

## Modellregeln

- UUID7
- tenant_id
- gültig-von/gültig-bis
- Geometrieversionierung
- Decimal für Geld und fachlich kritische Mengen
- Einheit explizit speichern
- Originalwert und normalisierter Wert
- Quelle und Regelversion
- Soft Delete nur fachlich begründet
- freigegebene Datensätze unveränderlich, Korrektur als neue Version

---

# 42. Requirement-IDs

Claude Code muss jede Anforderung in einer Traceability-Matrix führen.

Präfixe:

- `ASK-BUS` Betrieb
- `ASK-MST` Stammdaten
- `ASK-FLD` Schlag/GIS
- `ASK-PLAN` Anbauplanung
- `ASK-SEED` Aussaat
- `ASK-SOIL` Boden/Nmin
- `ASK-FERT` Düngung
- `ASK-PPP` Pflanzenschutz
- `ASK-IRR` Beregnung
- `ASK-HARV` Ernte
- `ASK-QS` Qualität
- `ASK-ENV` Umwelt
- `ASK-COST` Kosten/Leistung
- `ASK-MOB` Mobil
- `ASK-INT` Integration
- `ASK-NFR` Nichtfunktional

Status:

- NOT_ANALYZED
- NOT_IMPLEMENTED
- PARTIAL
- IMPLEMENTED_UNVERIFIED
- VERIFIED
- BLOCKED
- NOT_APPLICABLE

---

# 43. Abnahmeszenarien

## A. Betrieb und Jahreswechsel

Ein Betrieb wird aus CRM übernommen, das Wirtschaftsjahr wird angelegt und Vorjahresschläge werden ohne doppelte Bewegungsdaten fortgeführt.

## B. Förderantragsimport

Eine amtliche Flächendatei wird importiert. Bestehende Schläge werden abgeglichen, neue angelegt, geänderte Geometrien als Version gespeichert und Konflikte angezeigt.

## C. Sammeldüngung

Mehrere Schläge werden gewählt. Das System berechnet Produkt- und Nährstoffmengen je Schlag, prüft Bedarf und Grenzen, zeigt Konflikte und bucht nach Freigabe Lagerverbrauch und Kosten.

## D. Pflanzenschutz

Eine Anwendung wird geplant. Produktzulassung, Kultur, Indikation, Aufwand, Anwendungen, Wartezeit, Gewässerauflagen, Sachkunde und Geräteprüfung werden geprüft. Nach Ausführung wird die Istmaßnahme elektronisch dokumentiert.

## E. Ernte

Wiegedaten werden einem Schlag zugeordnet, Lagercharge und Erntepartie erzeugt, Ertrag und Qualität berechnet und Erlös/Kosten der Schlagrechnung zugeordnet.

## F. Prüfung

Für einen gewählten Betrieb und Zeitraum wird ein vollständiges Prüfberichtspaket mit Regelständen, Freigaben und Audit-Historie erzeugt.

---

# 44. Claude-Code-Arbeitsauftrag

```text
Arbeite im Repository JochenWeerda/VALEO-NeuroERP-3.0.

Verbindliches Ziel:
docs/specs/agrar/lastenheft-ackerschlagkartei-lwk-2017-plus.md

Das Lastenheft folgt dem Bedienungsablauf des LWK-Handbuchs 2017 und erweitert
ihn um den Zielstand 2026. Es ist kein Auftrag für einen isolierten Prototyp,
sondern für einen integrierten VALEO-NeuroERP-Fachbereich.

Vorgehen:

1. Lies CLAUDE.md und alle Architektur-, Design-, Test- und Sicherheitsregeln.
2. Inventarisiere den vollständigen IST-Stand zu:
   Betrieb, Schlag, GIS, Anbauplanung, Kulturen, Saatgut, Boden, Nmin,
   Düngung, Pflanzenschutz, Beregnung, Ernte, QS, Umwelt, Lager, Kosten
   und Agrarförderimporte.
3. Suche Backend, Frontend, Modelle, Migrationen, APIs, Tests und Dokumentation.
4. Erstelle:
   - docs/specs/agrar/ackerschlagkartei-ist-audit.md
   - docs/specs/agrar/ackerschlagkartei-traceability.md
   - docs/specs/agrar/ackerschlagkartei-target-architecture.md
   - docs/specs/agrar/ackerschlagkartei-implementation-plan.md
5. Ordne jede Anforderung einer stabilen ASK-ID, vorhandenen Dateien,
   dem Gap, Zielcode und einem Testnachweis zu.
6. Verwende keine pauschalen Erfüllungsbehauptungen.
7. Bewahre vorhandene fachlich korrekte Funktionen und Verträge.
8. Keine neue UI-Bibliothek und kein paralleles Design-System.
9. Nutze Mask Builder, ListReport, ObjectPage, Wizard, Worklist und OverviewPage.
10. Implementiere vertikal, nicht Schicht für Schicht.

Erstes vertikales Inkrement:
Betrieb → Wirtschaftsjahr → Schlagimport/GIS → Anbauplanung → Aussaat →
Schlaginfo → Bericht.

Zweites Inkrement:
Betriebsmittelstämme → Düngung → Düngebedarf → Lager/Kosten → Prüfung.

Drittes Inkrement:
Pflanzenschutzstamm → Zulassungs-/Auflagenprüfung → mobile Ausführung →
elektronisches Pflanzenschutzjournal.

Viertes Inkrement:
Boden/Nmin → Beregnung → Ernte → Charge/Lager → Kosten/Leistung.

Fünftes Inkrement:
QS/AUM → Auditpaket → ENNI/NÄON/weitere Integrationen → Precision Farming.

Für jedes Inkrement:
- Alembic-Migrationen
- Pydantic/OpenAPI
- Services und Repositories
- Tenant/RBAC
- Frontend
- Unit- und Integrationstests
- Playwright
- Accessibility
- Audit
- Performance
- Dokumentation
- Traceability

Arbeite nach Audit und Zielarchitektur autonom bis zu einem getesteten,
validierten vertikalen Zwischenstand. Stoppe nicht bei einer reinen Analyse.
```

---

# 45. Quellenbasis

## Primärquelle

- Landwirtschaftskammer Niedersachsen: Handbuch der Ackerschlagkartei 2017, 32 Seiten. Das Handbuch beschreibt Betrieb, Stammdaten, Dünger, Pflanzenschutzmittel, Anwender, Kulturen, Technik, Maßnahmen, Anbauplan, ANDI-Import, Schlagbearbeitung, Aussaat, Nmin, Bodenuntersuchung, Düngung, Düngebedarf, Pflanzenschutz, Beregnung, Ernte, QS, Umweltmaßnahmen, Auswertung und Datensicherung.
- Downloadseite: https://www.lwk-niedersachsen.de/lwk/news/34246_Ackerschlagkartei_1.1.2022_fuer_Windows_und_Apple_OSX_verfuegbar
- Handbuch: https://www.lwk-niedersachsen.de/services/download.cfm?file=24711

## Aktueller LWK-Zielstand

Die LWK-Seite zur Ackerschlagkartei, Stand 31. März 2026, nennt weiterhin:

- gesetzliche und Cross-Compliance-Dokumentation
- Wasserschutzgebiete
- QS/GLOBALG.A.P.
- Anbauplan
- Dünger- und Pflanzenschutzliste
- Einzelschlagdokumentation
- Ausdruck einzelner Maßnahmen
- direktkostenfreie Leistung
- schlag- und hektarbezogene Auswertung
- ANDI-Übernahme
- zusätzliche Kriterien der Pflanzenschutz-Dokumentationspflicht

## NÄON-Ergänzungen

Die LWK nennt für NÄON:

- Düngebedarf und Düngeplanung
- betriebliche Obergrenze 170 kg N/ha
- Ackerschlagkartei auf Smartphone und Desktop
- Stoffstrombilanz
- elektronische ENNI-Meldungen
- Import von ANDI-Betriebs- und Schlagdaten
- Import von Boden- und Nmin-Labordaten
- Dokumentation weiterer Arbeitsschritte
- gemeinsame interaktive Nutzung durch Berater und Landwirt

Quelle:
https://www.lwk-niedersachsen.de/lwk/kaba/1259_Naehrstoffmanagement_Modul_Online_Software_N%C3%84ON

---

# 46. Definition of Done

Eine Anforderung gilt nur als erfüllt, wenn:

- Requirement-ID vorhanden
- fachlicher Workflow vollständig
- Persistenz vorhanden
- Tenant/RBAC vorhanden
- Audit vorhanden
- API dokumentiert
- Frontend vollständig
- Lade-, Leer-, Fehler- und Erfolgszustände
- Mobile/Responsive geprüft
- Einheiten und Rundung getestet
- relevante Compliance-Regeln getestet
- Migration vorhanden
- Unit-/Integration-/E2E-Test grün
- Accessibility geprüft
- Dokumentation aktualisiert
- Traceability auf VERIFIED
- keine Regression bestehender Funktionen

---

**Ende des Lastenhefts**
