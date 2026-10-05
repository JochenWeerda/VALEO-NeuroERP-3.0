---
title: "Lastenheft: Integriertes Fütterungsberatungs- und Rationsmanagement-System"
type: specification
audience: [produkt, fachlich, entwickler, qa, agent]
owner: Auftraggeber (Jochen Weerda)
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Verbindliches Lastenheft des Auftraggebers für den Ausbau des Fütterungs- und Rationsbereichs in VALEO NeuroERP 3.0.
---

# Lastenheft: Integriertes Fütterungsberatungs- und Rationsmanagement-System für VALEO NeuroERP 3.0

**Dokumenttyp:** Lastenheft aus Sicht des Auftraggebers
**Zielsystem:** VALEO NeuroERP 3.0
**Zielmodul:** Agrar / Tierernährung / Fütterungsberatung
**Stand:** 15.07.2026
**Status:** Arbeits- und Entwicklungsgrundlage für Claude Code
**Priorisierung:** MUSS / SOLL / KANN
**Referenzrahmen:** Funktionsumfang moderner Fütterungsberatungs- und Rationsmanagement-Lösungen; fachliche Zielabdeckung entsprechend der Fodjan-Hilfe
**Hinweis zur Quellenlage:** Die Website `https://fodjan.com/de/hilfe/` und ihre Unterseiten waren zum Erstellungszeitpunkt über die verfügbaren Webzugriffe technisch nicht abrufbar und nicht indexiert. Dieses Lastenheft beschreibt daher den angestrebten vollständigen Funktionsumfang eines gleichwertigen Fütterungsberatungs-Tools, ergänzt um den im Repository vorhandenen VALEO-IST-Stand. Vor Abnahme ist eine vollständige Seit-für-Seite-Traceability gegen die Fodjan-Hilfe nachzuholen.

---

## 1. Zweck des Dokuments

Dieses Lastenheft beschreibt aus Sicht des Auftraggebers, **welche fachlichen, funktionalen, qualitativen und integrativen Anforderungen** ein vollständiges Fütterungsberatungs-Tool innerhalb von VALEO NeuroERP erfüllen muss.

Es dient Claude Code als verbindliches Zielbild für die Weiterentwicklung des vorhandenen IST-Bereichs. Claude Code soll:

1. den vorhandenen Funktionsumfang im Repository vollständig analysieren,
2. die Differenz zwischen IST und diesem Lastenheft dokumentieren,
3. eine ausführbare Umsetzungsplanung erstellen,
4. die Anforderungen schrittweise produktionsreif implementieren,
5. bestehende Architektur-, Sicherheits-, Design- und Qualitätsregeln einhalten,
6. keine vorhandenen fachlich korrekten Funktionen ersetzen oder verschlechtern,
7. jeden umgesetzten Anforderungspunkt durch Tests und nachvollziehbare Akzeptanzkriterien belegen.

---

## 2. Ausgangslage und vorhandener IST-Stand

Im Repository existiert bereits ein umfangreicher Bereich zur Rationsoptimierung. Der aktuelle Backend-Stand enthält unter anderem:

- eine Rationsoptimierungs-API,
- einen optionalen Proxy zu einem externen Optimierungsdienst,
- einen internen LP-Solver auf Basis von `scipy.optimize.linprog`,
- ein Energiesystem auf Grundlage GfE 2023,
- ein Proteinsystem mit `sidP_FAN1`,
- DLG-Futterwerttabellen,
- Bedarfsmodelle nach Tiergruppe, Laktationsstadium und Leistung,
- Kostenminimum unter harten Nebenbedingungen,
- Kontrollen unter anderem für aNDFom, pabKH, Rohfett, RMD und Struktur,
- eine Erklärschicht mit Warnungen und Begründungen,
- eine Futtermittel-Referenzdatenbank,
- Preisannahmen und Futtermittelgruppen,
- Nährstoff-, Mineralstoff- und Faserkennzahlen.

Der vorhandene IST-Bereich ist fachlich bereits substanziell, stellt aber noch nicht automatisch ein vollständiges Beratungs-, Betriebs-, Controlling-, Dokumentations- und Kollaborationssystem dar.

Die Weiterentwicklung soll daher **nicht nur einen Solver**, sondern einen durchgängigen fachlichen Prozess abbilden:

> Betrieb und Tiere erfassen → Futtermittel und Analysen verwalten → Rationen planen → Varianten vergleichen → fachlich bewerten → freigeben → füttern → tatsächliche Fütterung und Leistung kontrollieren → Abweichungen erkennen → Maßnahmen ableiten → dokumentieren → berichten.

---

## 3. Produktvision

VALEO NeuroERP soll ein integriertes Fütterungsberatungs- und Rationsmanagement-System bereitstellen, das landwirtschaftliche Betriebe, Berater, Futtermittelhändler, Tierärzte und weitere berechtigte Fachpersonen in einem gemeinsamen, mandantenfähigen Arbeitsraum verbindet.

Das System soll:

- wissenschaftlich nachvollziehbare Rationen berechnen,
- Fütterung praxisnah planen,
- mehrere Betriebe und Tiergruppen verwalten,
- Futteranalysen und Preise aktuell halten,
- Rationsvarianten fachlich und wirtschaftlich vergleichen,
- Risiken und Grenzwertverletzungen verständlich erklären,
- Soll- und Ist-Fütterung gegenüberstellen,
- Tierleistungs- und Controllingdaten einbeziehen,
- Beratungsfälle dokumentieren,
- Empfehlungen und Aufgaben ableiten,
- Berichte und Futterpläne erzeugen,
- Daten aus Laboren, Herdenmanagement, ERP, Mischtechnik und mobilen Anwendungen integrieren,
- alle Änderungen revisionssicher und nachvollziehbar dokumentieren.

---

## 4. Zielgruppen und Rollen

### 4.1 Primäre Benutzerrollen

| Rolle | Ziel und typische Aufgaben |
|---|---|
| Fütterungsberater | Betriebe betreuen, Rationen rechnen, Varianten bewerten, Empfehlungen dokumentieren |
| Landwirt/Betriebsleiter | Tiergruppen, Futtermittel, Preise, Futterpläne und Ergebnisse verwalten |
| Herdenmanager | Soll-Ist-Fütterung, Tierleistung, Gruppenwechsel und Abweichungen kontrollieren |
| Futtermittel-Außendienst | Kunden beraten, Produkte fachlich einordnen, Angebote und Rationen verknüpfen |
| Tierarzt | Tiergesundheitsrelevante Kennzahlen und Fütterungsrisiken bewerten |
| Labor | Analysedaten bereitstellen oder validieren |
| Mischwagen-/Fütterungspersonal | Tagespläne einsehen, Mischungen durchführen und Ist-Mengen erfassen |
| Administrator | Stammdaten, Rechte, Einheiten, Normsysteme und Integrationen verwalten |
| Controlling/Geschäftsführung | Kosten, Effizienz, Beratungserfolg und betriebliche Kennzahlen analysieren |

### 4.2 Rechte- und Mandantenmodell

Das System MUSS:

- Mandanten strikt trennen,
- rollenbasierte Zugriffe unterstützen,
- Rechte auf Betrieb, Standort, Herde, Tiergruppe und Beratungsfall begrenzen können,
- Lese-, Bearbeitungs-, Freigabe- und Administrationsrechte differenzieren,
- externe Berater gezielt für einzelne Betriebe freischalten,
- zeitlich begrenzte Freigaben ermöglichen,
- jede fachlich relevante Änderung protokollieren.

---

## 5. Fachlicher Gesamtprozess

### 5.1 End-to-End-Prozess

1. Betrieb und Standorte anlegen oder aus CRM übernehmen.
2. Tierarten, Herden und Leistungsgruppen definieren.
3. Tier- und Leistungsdaten importieren oder manuell erfassen.
4. Futtermittelbestand und Futteranalysen erfassen.
5. Preise, Verfügbarkeiten und Mengengrenzen pflegen.
6. Bedarfsmodell und Normsystem auswählen.
7. Ausgangsration erstellen oder bestehende Ration kopieren.
8. Ration manuell bearbeiten oder optimieren.
9. Grenzwerte, Zielgrößen und fachliche Regeln prüfen.
10. Varianten vergleichen.
11. Beraterkommentar und Maßnahmen dokumentieren.
12. Ration freigeben und als Futterplan veröffentlichen.
13. Tages-, Misch- oder Liefermengen bereitstellen.
14. Tatsächlich gefütterte Mengen importieren oder erfassen.
15. Leistungs-, Gesundheits- und Fütterungskennzahlen kontrollieren.
16. Abweichungen erkennen und Aufgaben erzeugen.
17. Verlauf und Beratungserfolg dokumentieren.
18. Bericht, PDF, Export oder Kundenfreigabe erzeugen.

---

## 6. Funktionale Anforderungen

### 6.1 Betriebs- und Kundenverwaltung

#### MUSS

- Betriebe aus dem VALEO-CRM als Fütterungsbetriebe übernehmen.
- Mehrere Betriebsstätten je Geschäftspartner verwalten.
- Ansprechpartner, Berater, Tierarzt und sonstige Beteiligte zuordnen.
- Betriebsdaten wie Produktionsrichtung, Haltungsform, Fütterungssystem und Melksystem erfassen.
- Mehrere Herden, Ställe und Fütterungsbereiche je Betrieb verwalten.
- Betriebsbezogene Standardwerte und Präferenzen speichern.
- Beratungsstatus und letzte Beratung anzeigen.
- Dokumente, Analysen, Rationen, Aufgaben und Berichte in einer Betriebsakte bündeln.
- Historie aller fachlichen Änderungen anzeigen.

#### SOLL

- Betriebskennzahlen aus CRM, Warenwirtschaft und Finanzdaten nutzen.
- Geografische und logistische Informationen berücksichtigen.
- Beratungsvorlagen je Betriebstyp hinterlegen.
- Betriebe nach Risiko, Beratungsbedarf und Aktualität filtern.

#### Akzeptanzkriterien

- Ein CRM-Geschäftspartner kann ohne Doppelerfassung als Fütterungsbetrieb aktiviert werden.
- Die Fütterungsakte zeigt alle zugehörigen Rationen, Analysen, Tiergruppen und Beratungsvorgänge.
- Benutzer sehen nur freigegebene Betriebe.

---

### 6.2 Tierarten, Herden und Tiergruppen

#### MUSS

Das System MUSS mindestens folgende Strukturen unterstützen:

- Betrieb
- Standort
- Stall/Haltungsbereich
- Herde
- Tiergruppe
- optional Einzeltier

Je Tiergruppe müssen erfasst werden können:

- Tierart,
- Nutzungsrichtung,
- Rasse oder Genetik,
- Anzahl Tiere,
- durchschnittliches Lebendgewicht,
- Alter,
- Laktationsnummer,
- Laktationstag,
- Trächtigkeitsstatus,
- Milchleistung,
- Milchinhaltsstoffe,
- Tageszunahme,
- Futteraufnahme,
- Haltungs- und Umweltbedingungen,
- Leistungsziel,
- Gesundheits- oder Risikomerkmale,
- Gültigkeitszeitraum.

#### MUSS für Milchvieh

- Frischmelker,
- Hochleistungsgruppe,
- mittlere/späte Laktation,
- Altmelker,
- Trockensteher,
- Vorbereiter,
- Färsen,
- Kälber,
- Jungvieh.

#### SOLL

- Gruppenwechsel mit Gültigkeitsdatum.
- Historie der Gruppenparameter.
- Import aus Herdenmanagementsystemen.
- Ableitung durchschnittlicher Gruppenwerte aus Einzeltieren.
- automatische Warnung bei veralteten Tiergruppenparametern.

---

### 6.3 Futtermittel-Stammdaten

#### MUSS

Jedes Futtermittel muss mit folgenden Informationen verwaltet werden können:

##### Identität und Klassifikation

- eindeutige ID,
- Bezeichnung,
- Kurzbezeichnung,
- Futtermittelgruppe,
- Futterart,
- Herkunft,
- Hersteller/Lieferant,
- Handelsprodukt oder betriebseigenes Futtermittel,
- Grundfutter/Kraftfutter/Mineralfutter/Zusatzstoff,
- Konservierungsart,
- Bio-/VLOG-/QS-/GMP+-Status,
- Freigabestatus,
- Gültigkeitszeitraum.

##### Mengen- und Preisangaben

- Einheit in Frischmasse und Trockenmasse,
- Trockenmassegehalt,
- Dichte oder Schüttgewicht,
- Preis je Tonne, Dezitonne, Kilogramm oder kg TM,
- Fracht und Zuschläge,
- gültiger Zeitraum,
- Verfügbarkeit,
- Lagerbestand,
- Mindest- und Höchstmenge je Tier und Tag,
- Mindest- und Höchstanteil an der Gesamtration,
- Mindestabnahme oder Gebindegröße.

##### Nährstoffwerte

Das Datenmodell MUSS flexibel erweiterbar sein und mindestens unterstützen:

- TM,
- Rohasche,
- Rohprotein,
- nutzbares bzw. dünndarmverdauliches Protein,
- RNB/RMD beziehungsweise normsystemspezifische Proteinbilanz,
- Rohfett,
- Rohfaser,
- aNDFom,
- ADFom,
- ADL,
- Stärke,
- beständige Stärke,
- Zucker,
- NFC,
- organische Masse,
- Verdaulichkeiten,
- Energiekennzahlen,
- Calcium,
- Phosphor,
- Natrium,
- Magnesium,
- Kalium,
- Schwefel,
- Chlorid,
- DCAB,
- Spurenelemente,
- Vitamine,
- Aminosäuren,
- Fettsäuren,
- Gärparameter,
- pH-Wert,
- mikrobiologische Kennzahlen,
- Mykotoxine und Schadstoffe,
- Struktur- und Partikelkennzahlen.

#### SOLL

- eigene betriebliche Futtermittel,
- gemeinsame Mandantenbibliotheken,
- zentrale Referenzbibliothek,
- Produktvarianten,
- Versionsverwaltung,
- Verknüpfung mit VALEO-Artikelstamm,
- Preisübernahme aus Einkauf, Verkauf oder Kontrakten,
- Chargen- und Lagerbezug,
- Alternativ- und Ersatzfuttermittel,
- fachliche Eignung je Tiergruppe,
- Nachhaltigkeitskennzahlen wie CO₂-Fußabdruck, Flächennutzung und Herkunft.

---

### 6.4 Futteranalysen und Laborwerte

#### MUSS

- Neue Analyse manuell erfassen.
- Laborbericht als Datei anhängen.
- Analysewerte einem Futtermittel, einer Charge, einem Silo oder einer Ernte zuordnen.
- Probenahmedatum, Analysezeitpunkt, Labor und Methode dokumentieren.
- Frischmasse- und Trockenmassebezug korrekt behandeln.
- Einheiten automatisch umrechnen.
- Fehlende Werte kennzeichnen.
- Analysewerte validieren.
- unplausible Werte mit Warnungen versehen.
- mehrere Analysen historisch verwalten.
- aktive Analyse auswählen.
- Analysewerte mit Referenzwerten vergleichen.
- Gültigkeit und Alter der Analyse anzeigen.
- nachträgliche Änderungen revisionssicher protokollieren.

#### SOLL

- PDF-, CSV-, Excel-, XML- und API-Import.
- OCR-gestützte Übernahme.
- Laborschnittstellen.
- Mittelwertbildung aus mehreren Proben.
- gewichtete Mittelwerte nach Charge oder Silozone.
- Trenddarstellung.
- automatische Erinnerung an neue Proben.
- Schätzung fehlender Werte mit eindeutiger Kennzeichnung.
- Analysequalitäts-Score.

#### Akzeptanzkriterien

- Eine importierte Analyse wird nie ungeprüft als endgültiger Wert verwendet.
- Originalwert, Einheit, Umrechnung und verwendeter Rechenwert bleiben nachvollziehbar.
- Rationen zeigen eindeutig, auf welcher Analyseversion sie beruhen.

---

### 6.5 Bedarfsberechnung

#### MUSS

- Auswahl eines gültigen Bedarfs- und Bewertungssystems.
- Versionierung des Normsystems.
- Bedarf nach Tierart, Leistung, Gewicht, Alter, Laktationsstadium und physiologischem Zustand.
- Erhaltungsbedarf.
- Leistungsbedarf.
- Trächtigkeitsbedarf.
- Wachstumsbedarf.
- Mobilitäts- oder Weidezuschläge.
- Umwelt- und Temperaturkorrekturen.
- Ziel-Futteraufnahme.
- Energie-, Protein-, Mineralstoff- und Strukturbedarf.
- Erklärung der verwendeten Eingangsgrößen.
- Kennzeichnung geschätzter Werte.
- Nachvollziehbare Berechnungsformeln oder Regelreferenzen.
- Neuberechnung bei Änderung relevanter Parameter.

#### SOLL

- GfE-, DLG-, NRC-, NASEM- oder weitere Modelle als austauschbare Rechenprofile.
- betriebsspezifische Anpassungsfaktoren.
- Szenarien für Hitzestress.
- Szenarien für Weidegang.
- Gesundheits- und Übergangsphasenmodelle.
- Berücksichtigung von Futterselektion und Restfutter.
- Konfidenz- oder Datenqualitätsanzeige.

---

### 6.6 Rationserstellung

#### MUSS

- Neue Ration aus leerer Vorlage erstellen.
- Bestehende Ration kopieren.
- Ration aus Vorlage erzeugen.
- Futtermittel suchen, filtern und hinzufügen.
- Mengen in Frischmasse oder Trockenmasse eingeben.
- Automatische Umrechnung zwischen FM und TM.
- Tierzahl und Rationsdauer berücksichtigen.
- Tagesmenge je Tier, Gruppe und Betrieb berechnen.
- Nährstoffsummen laufend aktualisieren.
- Ziel-, Ist- und Grenzwerte gegenüberstellen.
- Überschreitungen und Unterdeckungen markieren.
- Rationskosten je Tier und Tag, je kg TM und je Leistungseinheit berechnen.
- Ration speichern, versionieren, kommentieren und freigeben.
- Entwurf, geprüft, freigegeben, aktiv und archiviert als Status unterstützen.
- Gültig-ab- und Gültig-bis-Datum.
- Änderungen zwischen Versionen anzeigen.
- Verantwortlichen Benutzer dokumentieren.

#### Bedienung

- Tabellenartige, schnelle Bearbeitung.
- Tastaturbedienung.
- Inline-Mengenänderung.
- Undo/Redo für noch nicht gespeicherte Änderungen.
- Sortierung nach Futterreihenfolge oder Mischreihenfolge.
- Fixieren einzelner Futtermittel.
- Min-/Max-Grenzen direkt in der Ration.
- sofort sichtbare Auswirkungen jeder Mengenänderung.
- keine versteckten automatischen Änderungen ohne Hinweis.

---

### 6.7 Rationsoptimierung

#### MUSS

Die Optimierung muss mehrere Zielarten unterstützen:

- Kostenminimum,
- maximale Zielerfüllung,
- minimale Abweichung von einer Ausgangsration,
- maximale Nutzung betriebseigener Futtermittel,
- minimale Futterumstellung,
- definierte Einsatzmengen,
- optimierte Nährstoffabdeckung,
- optional ökologische Zielgrößen.

#### Nebenbedingungen

- Mindest- und Höchstmengen je Futtermittel,
- Pflichtfuttermittel,
- gesperrte Futtermittel,
- fixe Mengen,
- Gruppen- und Summengrenzen,
- Trockenmasseaufnahme,
- Energie,
- Protein,
- Faser,
- Stärke,
- Zucker,
- Fett,
- Struktur,
- Mineralstoffe,
- DCAB,
- normsystemspezifische Kennzahlen,
- Preis- oder Verfügbarkeitsgrenzen,
- Lagerbestände,
- Misch- und Dosiergrenzen.

#### MUSS

- harte und weiche Nebenbedingungen unterscheiden.
- nicht lösbare Optimierungen verständlich erklären.
- konfliktverursachende Grenzen benennen.
- alternative Lösungsvorschläge anbieten.
- Solverstatus dokumentieren.
- verwendeten Algorithmus und Parameter versionieren.
- Ergebnis reproduzierbar speichern.
- manuelle Nachbearbeitung ermöglichen.
- Optimierung nie ungefragt als freigegebene Ration aktivieren.

#### SOLL

- Mehrzieloptimierung.
- Pareto-Varianten.
- Sensitivitätsanalyse.
- Shadow Prices oder Grenzkosten.
- automatische Futtermittelalternativen.
- Robustheitsprüfung bei schwankender TM oder Analysewerten.
- Monte-Carlo- oder Szenarioanalyse.
- Optimierung über mehrere Tiergruppen und begrenzte Gesamtbestände.
- standortübergreifende Optimierung.
- Nachhaltigkeitsoptimierung.

---

### 6.8 Fachliche Rationsbewertung

#### MUSS

Die Bewertung muss mehr sein als eine Ampel. Jede Bewertung muss enthalten:

- Kennzahl,
- Istwert,
- Zielwert oder Zielbereich,
- Einheit,
- Bewertung,
- fachliche Bedeutung,
- mögliche Ursache,
- mögliche Folge,
- Handlungsempfehlung,
- Datenquelle,
- Regel- oder Normsystemversion.

#### Bewertungskategorien

- Energieversorgung,
- Proteinversorgung,
- Pansenbilanz,
- Faser und Struktur,
- Stärke und Zucker,
- Fett,
- Mineralstoffe,
- Spurenelemente,
- Vitamine,
- Futteraufnahme,
- Grundfutteranteil,
- Kraftfutteranteil,
- Wasserbedarf,
- Gärqualität,
- Stabilität,
- Tiergesundheitsrisiken,
- Kosten und Wirtschaftlichkeit,
- Datenqualität.

#### MUSS

- Warnungen priorisieren.
- kritische, hohe, mittlere und informative Hinweise unterscheiden.
- widersprüchliche Ziele sichtbar machen.
- Auswirkungen einer Änderung erklären.
- Beratereinschätzung ergänzen lassen.
- Warnungen nicht nur farblich darstellen.
- Freigabe trotz Warnung nur mit Begründung erlauben, sofern konfiguriert.

---

### 6.9 Variantenvergleich

#### MUSS

- mindestens zwei Rationen vergleichen.
- Ausgangs- und Zielration gegenüberstellen.
- Änderungen je Futtermittel anzeigen.
- Änderungen je Nährstoff anzeigen.
- Kostenunterschiede ausweisen.
- Zielerfüllung vergleichen.
- Warnungen und Risiken vergleichen.
- Versionen eines Plans vergleichen.
- geeignete Druck- und Exportansicht.
- Beraterkommentar je Variante.

#### SOLL

- Szenarien wie Preisänderung, neue Analyse, Hitzestress oder Leistungsänderung.
- grafische Differenzdarstellung.
- automatische Empfehlung einer Vorzugsvariante mit Begründung.
- Vergleich über mehrere Tiergruppen.
- Break-even-Analyse.
- wirtschaftliche Bewertung je kg Milch, Tageszunahme oder Produktionseinheit.

---

### 6.10 Fütterungspläne und Mischanweisungen

#### MUSS

- Freigegebene Ration als Fütterungsplan veröffentlichen.
- Plan je Tiergruppe, Tag und Zeitraum.
- Mengen je Tier und Gruppe.
- Mengen in FM und TM.
- Gesamtmengen für den Mischvorgang.
- Mischreihenfolge.
- Chargen oder Silos optional auswählen.
- Hinweise zur Verarbeitung und Mischdauer.
- Anzahl Mischungen oder Teilmischungen.
- Skalierung nach aktueller Tierzahl.
- Rundungs- und Dosierregeln.
- druckbare und mobile Ansicht.
- PDF-Ausgabe.
- Planversion und Freigabestatus.
- klare Kennzeichnung veralteter Pläne.

#### SOLL

- Mischwagenexport.
- Fütterungsroboterexport.
- QR-Code.
- Offline-Verfügbarkeit.
- Rückmeldung der tatsächlich geladenen Mengen.
- Plan für mehrere Fütterungen pro Tag.
- automatische Aufteilung nach Mischwagenkapazität.
- Restfutterkorrektur.
- automatische Anpassung nach TM-Schnellmessung.

---

### 6.11 Soll-Ist-Fütterungscontrolling

#### MUSS

- Sollmengen aus aktivem Futterplan übernehmen.
- Istmengen manuell oder per Schnittstelle erfassen.
- Abweichung je Futtermittel, Mischung, Tiergruppe und Tag.
- absolute und prozentuale Abweichung.
- Auswirkung auf Nährstoffversorgung und Kosten.
- Verlauf über Zeit.
- Warnschwellen.
- Kommentierung und Ursachenklassifikation.
- Aufgaben aus Abweichungen erzeugen.
- nicht verfütterte oder ersetzte Komponenten dokumentieren.

#### SOLL

- Daten aus Mischwagen und Fütterungsrobotern.
- Restfuttermenge.
- TM-Korrektur.
- Futterverlust und Schwund.
- Mischgenauigkeit.
- Lade- und Mischzeiten.
- Fahrer-/Bedienerbezug.
- Standort- und Silobezug.
- automatische Anomalieerkennung.

---

### 6.12 Leistungs- und Erfolgscontrolling

#### MUSS

- Milchmenge oder Leistungskennzahl je Tiergruppe.
- Milchinhaltsstoffe beziehungsweise tierartspezifische Leistungsdaten.
- Futteraufnahme.
- Futterkosten.
- Futtereffizienz.
- Income over Feed Cost, sofern Daten vorhanden.
- Verlauf vor und nach Rationsänderung.
- Rationsversion im Zeitverlauf.
- Vergleich von Ziel und Ist.
- Anzeige von Datenlücken.
- Kommentierung externer Einflussfaktoren.

#### SOLL

- Milchharnstoff,
- Fett-Eiweiß-Quotient,
- Zellzahl,
- Ketose- und Azidoserisiken,
- Wiederkau- oder Aktivitätsdaten,
- Körperkondition,
- Kotbeurteilung,
- Sortierindex,
- Tiergesundheitsereignisse,
- Abgänge,
- Fruchtbarkeit,
- Klimadaten,
- Benchmarking zwischen Gruppen oder Betrieben,
- statistisch abgesicherte Erfolgsauswertung.

---

### 6.13 Beratung, Beobachtungen und Maßnahmen

#### MUSS

- Beratungsbesuch oder Remote-Beratung dokumentieren.
- Ausgangssituation erfassen.
- Beobachtungen strukturiert oder als Freitext.
- Fotos und Dokumente anhängen.
- fachliche Bewertung.
- Empfehlungen.
- Verantwortliche Person.
- Fälligkeit.
- Status der Maßnahme.
- Wiedervorlage.
- Verknüpfung zu Ration, Analyse und Tiergruppe.
- Abschluss und Wirksamkeitskontrolle.
- Beratungsbericht erzeugen.

#### SOLL

- Vorlagen und Checklisten.
- Spracheingabe.
- mobile Offline-Erfassung.
- automatische Vorschläge aus Abweichungen.
- Kundenfreigabe oder Kenntnisnahme.
- digitale Unterschrift.
- Erinnerungen und Eskalationen.
- Aufgabenintegration mit VALEO Workflow/CRM.

---

### 6.14 Futtermittelbedarf, Bestand und Einkauf

#### MUSS

- Bedarf aus aktiven Rationen hochrechnen.
- Zeitraum, Tierzahl und Sicherheitszuschlag berücksichtigen.
- Bedarf in FM, TM und Handelseinheit.
- Lagerbestand berücksichtigen.
- Reichweite berechnen.
- Unterdeckung anzeigen.
- Bezug zu VALEO-Artikelstamm.
- Preis und Lieferant berücksichtigen.
- geplante Futterwechsel einbeziehen.

#### SOLL

- Bestellvorschläge.
- Kontraktbezug.
- Reservierungen.
- Chargen und Mindesthaltbarkeit.
- automatische Reichweitenwarnung.
- saisonale Verfügbarkeiten.
- Lieferplan.
- alternative Futtermittel bei Engpass.
- Übergabe an Einkauf oder Verkauf.
- Berücksichtigung eigener Ernte und Silobestände.

---

### 6.15 Berichte und Ausgaben

#### MUSS

- Rationsübersicht.
- Fütterungsplan.
- Nährstoffbewertung.
- Variantenvergleich.
- Beratungsbericht.
- Futtermittelbedarf.
- Soll-Ist-Auswertung.
- Verlaufsbericht.
- Analysebericht.
- PDF-Export.
- CSV-/Excel-Export strukturierter Daten.
- Logo, Betrieb, Berater und Versionsangaben.
- klare Einheiten und Bezugsgrößen.
- Datum, Zeit, Status und Freigabe.
- revisionssichere Dokumentreferenz.

#### SOLL

- kundenindividuelle Vorlagen.
- mehrsprachige Ausgaben.
- automatischer Versand.
- Portalbereitstellung.
- digitale Signatur.
- Berichtspakete.
- konfigurierbare Kennzahlen.
- Diagramme mit barrierearmen Alternativtexten.

---

### 6.16 Zusammenarbeit und Freigaben

#### MUSS

- Entwurf durch Bearbeiter.
- fachliche Prüfung.
- Freigabe.
- Veröffentlichung.
- Archivierung.
- Kommentare mit Benutzer und Zeitpunkt.
- Änderungsanforderung.
- Benachrichtigung.
- Freigabehistorie.
- Schutz freigegebener Versionen vor stiller Änderung.

#### SOLL

- Vier-Augen-Prinzip.
- Kundenfreigabe.
- externe Gastbenutzer.
- Diskussion auf Kennzahl- oder Rationspositionsebene.
- Erwähnungen.
- Aufgaben und Wiedervorlagen.
- definierbare Freigabeworkflows je Mandant.

---

### 6.17 Suche, Navigation und Benutzeroberfläche

#### MUSS

- globale Suche nach Betrieb, Tiergruppe, Futtermittel, Ration und Analyse.
- kontextabhängige Navigation.
- Betriebsakte als zentraler Einstieg.
- klare Breadcrumbs.
- ListReport für Listen.
- ObjectPage für Detailansichten.
- Wizard für komplexe Erstanlage.
- Worklist für Beratungs- und Prüfaufgaben.
- OverviewPage für Betriebs- und Fütterungsübersichten.
- responsive Desktop-, Tablet- und mobile Ansichten.
- vollständige Tastaturbedienung.
- sichtbare Fokuszustände.
- WCAG 2.2 AA.
- deutsche Fachsprache.
- keine rein dekorativen Dashboard-Karten.
- hohe Informationsdichte bei guter Lesbarkeit.
- bestehende VALEO-Design-Tokens, Themes und Density-Modi verwenden.

#### SOLL

- gespeicherte Filter.
- persönliche Ansichten.
- Tabellenkonfiguration.
- Favoriten.
- Schnellaktionen.
- Command Palette.
- kontextbezogener Assistent.
- direkte Navigation von Warnung zu Ursache und Bearbeitungsstelle.

---

### 6.18 Mobiler Einsatz

#### MUSS

Mobile Nutzung für:

- Futterplan ansehen,
- Tierzahl ändern,
- Istmengen erfassen,
- Futtermittel oder Silo auswählen,
- Beobachtung dokumentieren,
- Foto anhängen,
- Maßnahme abhaken,
- Analyse oder Ration nachschlagen.

#### SOLL

- Offline-Modus.
- Synchronisationswarteschlange.
- Konfliktauflösung.
- Kamera/OCR.
- Barcode/QR-Code.
- Spracheingabe.
- Push-Benachrichtigungen.
- mobile Schnellmessung der Trockenmasse.

---

### 6.19 Schnittstellen

#### MUSS

- REST- oder vergleichbare versionierte API.
- Mandanten- und Rechteprüfung.
- idempotente Importprozesse.
- Fehlerprotokoll.
- Importvorschau.
- Validierungsbericht.
- Zuordnungs- und Mappingregeln.
- Wiederholbarkeit ohne Dubletten.
- Audit-Log.

#### Zielintegrationen

- VALEO CRM.
- VALEO Artikelstamm.
- Einkauf, Verkauf, Lager und Kontrakte.
- Dokumentenmanagement.
- Laborwerte.
- Herdenmanagement.
- Milchkontrolldaten.
- Mischwagen.
- Fütterungsroboter.
- Melksysteme.
- Waagen.
- Wetter- und Klimadaten.
- externe Preis- und Futterwertdatenbanken.

#### SOLL

- Webhooks.
- Event-Bus.
- CSV/Excel/SFTP.
- standardisierte Agrarformate, sofern verfügbar.
- Integrationsmonitoring.
- Mapping-Oberfläche.
- Testmodus/Sandbox.

---

### 6.20 KI- und Assistenzfunktionen

#### MUSS

KI darf nur unterstützend wirken. Sie darf keine fachliche Freigabe ersetzen.

Das System MUSS:

- verwendete Datenquellen nennen,
- Annahmen kennzeichnen,
- Unsicherheit anzeigen,
- Empfehlungen begründen,
- Änderungen vor Ausführung zeigen,
- Benutzerfreigabe verlangen,
- sensible Daten mandantenkonform verarbeiten,
- keine Werte erfinden,
- keine nicht nachvollziehbaren Rationsänderungen durchführen.

#### SOLL

- Erklärung von Warnungen.
- Ursachenanalyse.
- Vorschlag geeigneter Maßnahmen.
- Rationsvarianten.
- Ersatzfuttermittel.
- Analyse von Soll-Ist-Abweichungen.
- Entwurf von Beratungsberichten.
- Erkennung veralteter Daten.
- kontextbezogene Rückfragen.
- automatische, aber bestätigungspflichtige Aufgaben.

---

## 7. Nichtfunktionale Anforderungen

### 7.1 Qualität und Nachvollziehbarkeit

#### MUSS

- deterministische und reproduzierbare Berechnungen.
- Versionierung aller Regelwerke.
- Speicherung der verwendeten Eingabedaten.
- Speicherung des Solverstatus.
- Auditierbare Änderungshistorie.
- verständliche Fehlermeldungen.
- keine stillen Fallbacks bei fachlich relevanten Berechnungen.
- eindeutige Unterscheidung zwischen Messwert, Referenzwert, Schätzwert und manueller Eingabe.
- Einheiten- und Rundungsregeln zentral verwalten.

### 7.2 Performance

#### MUSS

- typische Detailseite unter normalen Bedingungen innerhalb von 2 Sekunden interaktiv.
- Mengenänderungen in der Ration unmittelbar sichtbar.
- lokale Neuberechnung ohne unnötige Vollseiten-Reloads.
- lange Listen virtualisieren.
- Optimierungsjobs mit Fortschritts- oder Statusanzeige.
- große Imports asynchron und wiederaufnehmbar.
- keine blockierende UI während Serveroperationen.
- Duplicate-Submit-Schutz.
- Caching von Referenzdaten.
- serverseitige Pagination und Filterung.

### 7.3 Verfügbarkeit und Betrieb

#### MUSS

- strukturierte Logs.
- technische und fachliche Metriken.
- Tracing.
- Health Checks.
- Fehlerkorrelation.
- sichere Wiederholung fehlgeschlagener Hintergrundjobs.
- Backup- und Restore-Konzept.
- Datenmigrationen über Alembic.
- definierte Rollback-Strategie.
- keine direkte Produktionseinführung ohne Feature Flag und Pilotbetrieb.

### 7.4 Sicherheit und Datenschutz

#### MUSS

- OIDC.
- rollenbasierte Autorisierung.
- Mandantentrennung.
- Verschlüsselung bei Übertragung.
- Schutz vor unberechtigtem Export.
- protokollierte Freigaben.
- Lösch- und Aufbewahrungsregeln.
- DSGVO-konforme Verarbeitung.
- minimale Berechtigungen.
- sichere Dateiimporte.
- Viren-/Malwareprüfung für Uploads.
- keine vertraulichen Betriebsdaten in öffentliche KI-Dienste ohne ausdrückliche Konfiguration.

### 7.5 Accessibility und UX

#### MUSS

- WCAG 2.2 AA.
- Kontrastprüfung.
- Screenreader-taugliche Formulare und Tabellen.
- Status nicht nur durch Farbe.
- Fokusmanagement in Dialogen.
- Fehlermeldungen am Feld und in Zusammenfassung.
- barrierearme Diagramme.
- Reduced Motion.
- Touch-Ziele.
- semantische HTML-Struktur.
- verständliche Einheiten.
- konsistente Fachbegriffe.

---

## 8. Fachliches Datenmodell

Claude Code soll das vorhandene Modell prüfen und mindestens folgende Aggregate beziehungsweise Entitäten abdecken:

- FeedingBusiness / Fütterungsbetrieb
- FarmSite / Betriebsstätte
- Herd
- AnimalGroup
- AnimalGroupSnapshot
- Feed
- FeedProduct
- FeedReferenceValue
- FeedAnalysis
- FeedAnalysisValue
- FeedBatch
- Silo
- NutrientDefinition
- UnitDefinition
- EvaluationSystem
- EvaluationSystemVersion
- RequirementProfile
- Ration
- RationVersion
- RationItem
- RationConstraint
- OptimizationRun
- OptimizationResult
- RationEvaluation
- Warning
- FeedingPlan
- FeedingPlanVersion
- MixingInstruction
- ActualFeeding
- PerformanceRecord
- Observation
- ConsultingCase
- Recommendation
- Measure/Task
- Approval
- Report
- ImportJob
- IntegrationMapping
- AuditEvent

### Modellierungsgrundsätze

- UUID7 für neue IDs, sofern Projektstandard.
- `tenant_id` in allen mandantenbezogenen Entitäten.
- Zeitgültigkeit für Stammdaten und Pläne.
- Soft Delete nur mit klarer fachlicher Regel.
- Geldwerte mit Decimal.
- keine Float-Arithmetik für abrechnungsrelevante Werte.
- Einheiten als explizite Daten, nicht nur als Feldnamen.
- Nährstoffe flexibel erweiterbar.
- Messwert, Bezugsbasis, Methode und Quelle gemeinsam speichern.
- freigegebene Versionen unveränderlich.
- abgeleitete Werte reproduzierbar.
- Audit-Events fachlich lesbar.

---

## 9. API-Anforderungen

### MUSS-Endpunktgruppen

- `/feeding/businesses`
- `/feeding/herds`
- `/feeding/animal-groups`
- `/feeding/feeds`
- `/feeding/feed-analyses`
- `/feeding/evaluation-systems`
- `/feeding/requirements`
- `/feeding/rations`
- `/feeding/rations/{id}/versions`
- `/feeding/rations/{id}/evaluate`
- `/feeding/rations/{id}/optimize`
- `/feeding/rations/{id}/compare`
- `/feeding/feeding-plans`
- `/feeding/actual-feedings`
- `/feeding/performance`
- `/feeding/consulting-cases`
- `/feeding/recommendations`
- `/feeding/reports`
- `/feeding/imports`
- `/feeding/integrations`

### API-Grundsätze

- OpenAPI vollständig.
- Pydantic-Schemas.
- konsistente Fehlerobjekte.
- ETags oder Optimistic Locking bei konkurrierenden Änderungen.
- Idempotency Keys für relevante Mutationen.
- Pagination.
- Filter.
- Sortierung.
- Feldvalidierung.
- fachliche Fehlercodes.
- Tenant- und RBAC-Prüfung.
- Versionierung.
- keine übergroßen Sammelendpunkte.
- Hintergrundjobs für Optimierung, Import und Berichtserstellung, sofern Laufzeit relevant.

---

## 10. Frontend-Zielstruktur

### Kernseiten

1. **Fütterungsübersicht** — offene Warnungen, auslaufende Pläne, veraltete Analysen, offene Maßnahmen, relevante Leistungsabweichungen.
2. **Betriebsliste** — Suche, Filter, Beratungsstatus, letzte Aktivität.
3. **Betriebsakte** — Übersicht, Tiergruppen, Futtermittel, Analysen, Rationen, Futterpläne, Controlling, Beratung, Dokumente, Historie.
4. **Tiergruppen-ObjectPage**
5. **Futtermittel-ObjectPage**
6. **Analyse-Wizard und Analyse-ObjectPage**
7. **Rationseditor** — Tabelleneditor, Nährstoffbewertung, Warnungsbereich, Kosten, Varianten, Verlauf, Optimierung.
8. **Variantenvergleich**
9. **Fütterungsplan**
10. **Soll-Ist-Controlling**
11. **Leistungscontrolling**
12. **Beratungsfall/Worklist**
13. **Berichte**
14. **Integrationsmonitor**

### Rationseditor: empfohlene Desktop-Struktur

- Kopfbereich mit Betrieb, Tiergruppe, Version, Status und Gültigkeit.
- linke oder zentrale Hauptfläche mit Rationspositionen.
- rechte kontextbezogene Bewertungs- und Warnungsleiste.
- Tabs oder Sektionen für: Ration, Nährstoffe, Mineralstoffe, Kosten, Bewertung, Varianten, Historie.
- feste primäre Aktionen: speichern, berechnen, optimieren, vergleichen, prüfen, freigeben.
- deutlicher Pending-, Fehler- und Erfolgstatus.

---

## 11. Abnahmekriterien je Kernprozess

### 11.1 Ration anlegen

**Gegeben:** Ein Betrieb, eine Tiergruppe und Futtermittel sind vorhanden.
**Wenn:** Der Berater eine neue Ration anlegt.
**Dann:**

- werden Bedarfswerte geladen,
- können Futtermittel hinzugefügt werden,
- werden FM/TM korrekt umgerechnet,
- werden Nährstoffsummen sofort berechnet,
- werden Warnungen verständlich angezeigt,
- kann die Ration als Entwurf gespeichert werden,
- bleibt die Änderungshistorie nachvollziehbar.

### 11.2 Ration optimieren

**Gegeben:** Zielwerte, Preise und Grenzen sind vollständig.
**Wenn:** Der Benutzer eine Optimierung startet.
**Dann:**

- wird der Auftrag gegen Doppelausführung geschützt,
- zeigt die UI einen Pending-Status,
- wird das Ergebnis reproduzierbar gespeichert,
- werden nicht erfüllte Grenzen erklärt,
- wird keine Ration automatisch freigegeben,
- kann der Benutzer Ergebnis und Ausgangsration vergleichen.

### 11.3 Analyse importieren

**Gegeben:** Ein Laborbericht liegt vor.
**Wenn:** Der Benutzer die Analyse importiert.
**Dann:**

- zeigt das System eine Vorschau,
- prüft Einheiten und Plausibilität,
- kennzeichnet fehlende oder unsichere Werte,
- verlangt eine Zuordnung,
- speichert Originaldatei und strukturierte Werte,
- aktualisiert keine aktive Ration ohne bewusste Entscheidung.

### 11.4 Futterplan veröffentlichen

**Gegeben:** Eine geprüfte Ration liegt vor.
**Wenn:** Ein berechtigter Benutzer sie freigibt.
**Dann:**

- wird eine unveränderliche Version erzeugt,
- werden Gültigkeit und Tierzahl gespeichert,
- wird ein Fütterungsplan erzeugt,
- werden Mischmengen korrekt skaliert,
- wird die Veröffentlichung protokolliert,
- ist eine spätere Änderung nur über eine neue Version möglich.

### 11.5 Soll-Ist-Kontrolle

**Gegeben:** Sollplan und Istmengen liegen vor.
**Wenn:** Der Benutzer die Kontrolle öffnet.
**Dann:**

- werden Mengenabweichungen dargestellt,
- werden Nährstoff- und Kostenfolgen berechnet,
- werden relevante Abweichungen priorisiert,
- können Ursache und Maßnahme dokumentiert werden,
- bleibt die Auswertung historisch erhalten.

---

## 12. Traceability-Matrix

Claude Code MUSS eine maschinenlesbare Traceability-Datei erstellen:

`docs/specs/feeding/requirements-traceability.md`

Für jede Anforderung:

| ID | Anforderung | Priorität | IST-Datei/API | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---:|---|---|---|---|---|---|

Statuswerte:

- `NOT_ANALYZED`
- `NOT_IMPLEMENTED`
- `PARTIAL`
- `IMPLEMENTED_UNVERIFIED`
- `VERIFIED`
- `BLOCKED`
- `NOT_APPLICABLE`

Jede Anforderung erhält eine stabile ID, zum Beispiel: `FEED-BUS-001`, `FEED-HERD-001`, `FEED-MAT-001`, `FEED-LAB-001`, `FEED-REQ-001`, `FEED-RAT-001`, `FEED-OPT-001`, `FEED-EVAL-001`, `FEED-PLAN-001`, `FEED-ACT-001`, `FEED-PERF-001`, `FEED-CONS-001`, `FEED-INT-001`, `FEED-NFR-001`.

---

## 13. Vorgehensauftrag an Claude Code

### Phase 0 – Schutzmaßnahmen

Claude Code MUSS vor Änderungen:

1. `CLAUDE.md` lesen.
2. Repository-Status prüfen.
3. vorhandene Tests, Architekturregeln und Konventionen erfassen.
4. bestehende Fütterungsdateien vollständig inventarisieren.
5. keine produktiven Daten oder Migrationen ungeprüft verändern.
6. einen eigenen Feature-Branch verwenden.
7. keine neue UI- oder Solver-Bibliothek ohne belegten Bedarf einführen.

### Phase 1 – IST-Audit

Claude Code soll mindestens durchsuchen:

- `app/api/v1/endpoints/rations_optimization.py`
- `app/agrar/rations/`
- zugehörige Schemas, Modelle, Services, Repositories und Tests
- Frontend-Seiten und Komponenten mit Begriffen: Ration, Fütterung, Futtermittel, Analyse, Herde, Tiergruppe, Milchvieh, Optimierung
- OpenAPI-Routen
- Migrationen
- Seed- und Referenzdaten
- Dokumentation
- Storybook
- E2E-Tests

Ergebnis:

- `docs/specs/feeding/ist-audit.md`
- vollständige Komponenten- und API-Landkarte
- Datenmodellübersicht
- bekannte technische Schulden
- Risikoliste
- keine pauschalen Aussagen ohne Dateinachweis

### Phase 2 – Gap-Analyse

Claude Code vergleicht jede Anforderung dieses Lastenhefts mit dem tatsächlichen Code.

Ergebnis: Traceability-Matrix, Gap-Liste, Priorisierung, Abhängigkeiten, Migrationsrisiken, Vorschlag für vertikale Lieferinkremente.

### Phase 3 – Zielarchitektur

Claude Code erstellt: Kontext- und Containerdarstellung, Domänenmodell, Aggregate und Verantwortlichkeiten, API-Zielbild, Eventmodell, Integrationskonzept, Rechtekonzept, Datenmigrationskonzept, Frontend-Seitenlandkarte, Teststrategie.

Keine Big-Bang-Neuentwicklung. Bestehende fachlich gute Bestandteile müssen weiterverwendet oder kontrolliert refaktoriert werden.

### Phase 4 – Vertikale Umsetzung

Empfohlene Reihenfolge:

- **Inkrement 1: Fachlicher Kern** — Tiergruppen, Futtermittel, Analysen, Bedarfsberechnung, Rationsversionen, Rationsbewertung, vollständige Tests.
- **Inkrement 2: Produktiver Rationseditor** — neue UI, manuelle Bearbeitung, Optimierung, Warnungen, Variantenvergleich, Freigaben.
- **Inkrement 3: Fütterungsplan** — Planversion, Mischanweisung, Skalierung, PDF, mobile Ansicht.
- **Inkrement 4: Soll-Ist-Controlling** — Istmengen, Abweichungen, Aufgaben, Verlauf.
- **Inkrement 5: Leistung und Beratung** — Leistungsdaten, Beratungsvorgang, Maßnahmen, Berichte.
- **Inkrement 6: Integrationen und Automatisierung** — Labor, Herdenmanagement, Mischwagen, ERP-Bestand, Einkauf/Verkauf, Event-Bus.

### Phase 5 – Validierung

Für jedes Inkrement: Unit-Tests, Integrationstests, API-Vertragstests, Berechnungs-Golden-Tests, Property-Based Tests für Einheiten und Grenzen, Solver-Reproduzierbarkeit, Frontend-Komponententests, Accessibility, Playwright E2E, Mandantenisolierung, RBAC, Performance, Migration Up/Down oder dokumentierte Rollback-Strategie.

### Phase 6 – Pilot und Rollout

- Feature Flag.
- Pilotmandant.
- Referenzbetrieb.
- Vergleich von Alt- und Neuberechnung.
- Abnahme durch fachkundigen Fütterungsberater.
- dokumentierte fachliche Testfälle.
- keine allgemeine Aktivierung vor bestandener Pilotabnahme.

---

## 14. Verbindlicher Claude-Code-Prompt

Der folgende Prompt kann Claude Code zusammen mit diesem Lastenheft übergeben werden:

```text
Arbeite im Repository JochenWeerda/VALEO-NeuroERP-3.0.

Dieses Dokument ist das verbindliche Lastenheft für den Ausbau des vorhandenen
Fütterungs- und Rationsbereichs:

docs/specs/feeding/lastenheft-fuetterungsberatung.md

Ziel ist kein isolierter Prototyp, sondern ein produktionsreifes, integriertes
Fütterungsberatungs- und Rationsmanagement-System innerhalb von VALEO NeuroERP.

Beginne nicht sofort mit breiten Codeänderungen.

1. Lies CLAUDE.md und alle relevanten Projektregeln.
2. Inventarisiere den vollständigen IST-Stand im Backend, Frontend, Datenmodell,
   in Migrationen, Tests und Dokumentation.
3. Lies insbesondere app/api/v1/endpoints/rations_optimization.py und den gesamten
   Bereich app/agrar/rations/.
4. Suche zusätzlich repositoryweit nach Ration, Fütterung, Futtermittel, Analyse,
   Herde, Tiergruppe, Milchvieh und Optimierung.
5. Erstelle:
   - docs/specs/feeding/ist-audit.md
   - docs/specs/feeding/requirements-traceability.md
   - docs/specs/feeding/target-architecture.md
   - docs/specs/feeding/implementation-plan.md
6. Ordne jede Lastenheftanforderung einem stabilen Requirement-ID, dem vorhandenen
   Code, dem Gap, der Zielumsetzung und mindestens einem Testnachweis zu.
7. Verwende Statuswerte NOT_ANALYZED, NOT_IMPLEMENTED, PARTIAL,
   IMPLEMENTED_UNVERIFIED, VERIFIED, BLOCKED oder NOT_APPLICABLE.
8. Erhalte vorhandene fachlich korrekte Berechnungen, API-Verträge und Tests.
9. Ersetze den bestehenden Solver nicht ohne belegte Notwendigkeit.
10. Plane vertikale, abnahmefähige Inkremente statt einer Big-Bang-Umstellung.
11. Nutze vorhandene VALEO-Architektur, Mask-Builder, Design-Tokens, OIDC,
    Mandantenmodell, FastAPI, SQLAlchemy, Alembic, React Query und bestehende
    Error-/Mutation-Lifecycle-Regeln.
12. Keine neue UI-Bibliothek und kein zweites paralleles Design-System.
13. Alle fachlich relevanten Berechnungen müssen reproduzierbar, versioniert,
    erklärbar und durch Golden-Tests abgesichert sein.
14. Alle freigegebenen Rationen und Fütterungspläne müssen unveränderlich
    versioniert und auditierbar sein.
15. KI-Funktionen dürfen beraten und erklären, aber niemals stillschweigend
    fachlich freigeben oder Werte erfinden.
16. Implementiere nach Audit und Gap-Analyse zuerst das kleinste vollständige
    vertikale Inkrement:
    Tiergruppe → Futtermittel/Analyse → Bedarf → Ration → Bewertung →
    Versionierung → Freigabe → Bericht.
17. Führe Typecheck, Lint, Unit-, Integrations-, E2E-, Accessibility-,
    Mandanten- und Build-Prüfungen aus.
18. Behebe alle durch deine Änderungen verursachten Fehler.
19. Dokumentiere am Ende:
    - analysierte Dateien,
    - implementierte Requirements,
    - Migrationen,
    - Tests und Ergebnisse,
    - verbleibende Gaps,
    - Risiken,
    - nächsten vertikalen Schritt.

Arbeite autonom bis zu einem validierten, getesteten Zwischenstand.
Stoppe nicht nach einer reinen Analyse, aber beginne erst mit Implementierung,
nachdem Audit, Traceability und Zielarchitektur konkret vorliegen.
```

---

## 15. Definition of Done

Eine Anforderung gilt erst als erfüllt, wenn:

- sie einer stabilen Requirement-ID zugeordnet ist,
- Backend und Frontend vollständig umgesetzt sind, sofern erforderlich,
- Mandanten- und Rechteprüfung vorhanden sind,
- Einheiten und Berechnungen getestet sind,
- Fehler-, Lade-, Leer- und Erfolgszustände vorhanden sind,
- Audit- und Versionsanforderungen eingehalten werden,
- Dokumentation aktualisiert ist,
- automatische Tests grün sind,
- fachliche Akzeptanzkriterien erfüllt sind,
- kein bestehender Kernprozess verschlechtert wurde,
- die Traceability auf VERIFIED steht.

---

## 16. Explizit nicht akzeptierte Lösungen

Nicht akzeptiert werden:

- reine UI-Demos ohne persistente Fachlogik,
- Mock-Daten in produktiven Pfaden,
- ein einzelner übergroßer Rations-Endpunkt,
- versteckte oder nicht reproduzierbare Berechnungen,
- ungekennzeichnete Schätzwerte,
- stilles Überschreiben freigegebener Rationen,
- Solver-Ergebnisse ohne Erklärung,
- Warnungen ausschließlich als Farben,
- fehlende Einheiten,
- Float-Verwendung für Geldberechnungen,
- fehlende Mandantentrennung,
- fehlende Versionshistorie,
- neue parallele Design-Systeme,
- neue UI-Bibliotheken ohne Architekturentscheidung,
- Abschalten oder Umgehen bestehender Tests,
- pauschales Markieren von Anforderungen als erfüllt ohne Code- und Testnachweis,
- KI-Antworten als Ersatz für deterministische fachliche Rechenlogik.

---

## 17. Offene Validierung gegen die Fodjan-Hilfe

Sobald die Fodjan-Hilfe technisch abrufbar ist, MUSS ein zusätzlicher Quellenabgleich erfolgen.

Ergebnisdatei: `docs/specs/feeding/fodjan-help-traceability.md`

Für jede Hilfeseite:

| URL | Seitentitel | erläuterte Funktion | Requirement-ID | Abdeckung | Gap | Bemerkung |
|---|---|---|---|---|---|---|

Abdeckungsstatus: `FULL`, `PARTIAL`, `MISSING`, `OUT_OF_SCOPE`, `SUPERSEDED`.

Claude Code darf das Lastenheft bei diesem Abgleich erweitern, aber keine bereits festgelegte MUSS-Anforderung ohne dokumentierte Auftraggeberentscheidung abschwächen oder entfernen.

---

## 18. Auftraggeber-Priorisierung

### Release A – Beratungsfähig

- Betrieb und Tiergruppen
- Futtermittel
- Analysen
- Bedarfsrechnung
- Rationseditor
- Bewertung
- Optimierung
- Varianten
- Versionierung
- Freigabe
- PDF-Bericht

### Release B – Betriebsfähig

- Fütterungsplan
- Mischanweisung
- Bedarf und Reichweite
- mobile Anzeige
- Istmengen
- Soll-Ist-Kontrolle

### Release C – Controllingfähig

- Leistungsdaten
- Futtereffizienz
- Kostencontrolling
- Beratung
- Maßnahmen
- Verlauf
- Benchmarking
