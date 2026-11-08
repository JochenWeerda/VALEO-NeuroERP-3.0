---
title: Lernende Ergaenzung verkuerzter WhatsApp-Bestellungen
type: explanation
audience: [product, entwickler, agent, disposition, qa]
owner: Codex
status: geplant
last_reviewed: 2026-10-12
description: User-Fachvertrag fuer heuristische Bestellmuster, belegtes Lernen, Unsicherheit, menschliche Korrektur und verfuegbare Liefertermine.
---

# Lernende Ergaenzung verkuerzter WhatsApp-Bestellungen

## Fachlicher Auftrag

User-Vorgabe vom 2026-10-11: Fehlendes Lieferdatum, Silo, Gebindegroesse und
gegebenenfalls Menge sind bei Dauerkunden haeufig implizit bekannt. Die
Ergaenzung soll **heuristisch lernend** erfolgen; bei zu grosser Unsicherheit
kommt ein Mensch hinzu. Eine starre Regel "immer den letzten Auftrag kopieren"
entspricht diesem Auftrag nicht. Das ausdrueckliche "wie letztes Mal" ist ein
zusaetzliches Signal, keine Voraussetzung fuer das Erkennen eines Musters.

Bestellt wird zum naechstmoeglichen Termin. Ist eine Lieferung am Folgetag
nicht moeglich, wird der Kunde informiert. Stueckgut wird haeufig auf festen
woechentlichen Touren geliefert; bekannte Tourgewohnheiten gehen in das
Verstaendnis ein. Sie ersetzen keine aktuelle Verfuegbarkeitspruefung. Dieser
Auftrag allein ordnet weder ein WhatsApp-Konto einem Mandanten zu noch beweist
er, dass ein Versand technisch stattgefunden hat.

## Nachgewiesener Ist-Stand

| Bestand | Aktueller Befund |
| --- | --- |
| `app/services/whatsapp_intake_service.py::extract` | LLM-Extraktion mit pauschalem confidence=0.9; Regex-Fallback mit 0.45. Keine kalibrierte Wahrscheinlichkeit fuer eine Historienergaenzung. |
| `_enrich` im selben Service | Aktiver Kunden-Business-Partner im eigenen Mandanten erforderlich; mehrere Kunden-/Artikeltreffer bleiben offen. Keine Historienergaenzung und kein Lernen aus Korrekturen. |
| `bestaetigen` im selben Service | Kunden-/Artikelreferenzen werden vor Write mandantengeprueft, Kontakt-Bediener aus Token; weiterhin kein unveraenderlicher Vorschlags-/Korrekturvergleich und keine echte Auftragsanlage. |
| `app/api/v1/endpoints/whatsapp_intake.py` | Alle fuenf Wege nutzen verifizierten OIDC-Mandanten und crm:read/crm:write; Eingangs-Replay und vollstaendige Urheber-/Korrekturabnahme bleiben offen. |
| `app/api/v1/endpoints/sales_orders.py::SalesOrderItemInput` | Artikel, Menge und Preis vorhanden; Einheit, Silo und Gebindegroesse fehlen in diesem Eingabevertrag. Historische Inbox-Bestaetigung ist daher kein Nachweis eines ausgefuehrten Auftrags. |
| Benachrichtigung | Persistente replaygeschuetzte Vorbereitung vorhanden; Browseranbindung und sichtbarer Versandnachweis offen. |

Dies ist ein **Fach- und Integrationsvertrag**, keine Behauptung einer bereits
implementierten lernenden Bestellverarbeitung. Die bisherigen festen
Extraktionswerte duerfen nicht als Freigabesicherheit weiterverwendet werden.
Erster Code-Schnitt: [Inbox-Zugriffsschutz](../quality-assurance/whatsapp-inbox-access-20261012.md).

## Lern- und Vorschlagsverfahren

1. Originalnachricht und explizite Angaben erhalten. Extraktion unterscheidet
   fehlend, explizit genannt, widerspruechlich und unlesbar. Auch eine explizite
   Null oder unzulaessige Mengenangabe wird nicht still durch Historie ersetzt.
2. Kunde, Lieferstelle und Artikel/Variante im verifizierten Mandantenkontext
   identifizieren. Aehnlicher Name allein berechtigt nicht zum Laden einer
   Historie. Mehrere passende Kunden/Artikel oder eine unbekannte Lieferstelle
   gehen in die menschliche Klaerung; kein beliebiger erster Treffer.
3. Vergleichbare bestaetigte Auftraege und nachvollziehbare Korrekturen
   begrenzt laden. Relevanz entsteht aus Kunde, Lieferstelle, Produktvariante,
   bisherigem Gebinde, Lieferart, zeitlicher Naehe und gegebenenfalls Saison.
   Modellseitig vorgeschlagene Merkmale sind keine verifizierten Referenzen.
4. Kandidaten und Alternativen heuristisch bewerten. Wiederholung, Aktualitaet,
   konkurrierende Muster und korrigierte Vorschlaege beeinflussen die Bewertung.
   Die Gewichte und die Freigabeentscheidung werden anhand belegter Ergebnisse
   angepasst. Fuer einen Cold Start bleibt die Unsicherheit sichtbar.
5. Menge, Einheit und Gebindegroesse gemeinsam betrachten: "eine Palette" und
   "eine Tonne" sind kein identischer Mengenwert. Silo/Lieferstelle und Artikel
   muessen zusammenpassen. Eine ausdrueckliche Artikel-/Gebindeaenderung kann
   alte Mengenmuster unbrauchbar machen. Keine Preisuebernahme aus diesem
   Bestellmustervertrag; Preise folgen dem bestehenden Preis-/Kontraktvertrag.
6. Pro fehlendem Feld einen Vorschlag mit Quellenbeleg, relevanten Alternativen,
   Modellversion und Unsicherheitsgruenden erzeugen. Die gemeinsame Sicherheit
   der Bestellung wird ebenfalls bewertet; ein hoher Kundenmatch-Wert macht
   eine unsichere Menge nicht sicher. Die KI darf keine eigene Wahrscheinlichkeit
   erfinden, die anschliessend als kalibrierte Sicherheit behandelt wird.
7. Nur ausreichend belegte und fachlich gueltige Ergaenzungen automatisch
   uebernehmen. Freigabeschwellen beruhen auf beobachteten Fehlern und deren
   Auswirkungen, feld-/risikobezogen und versioniert. Keine ungemessene globale
   Zahl wie 0.9 als Startfreigabe. Bis zur Kalibrierungsabnahme bleiben
   Ergaenzungen pruefpflichtige Vorschlaege.

Das Lernverfahren schaetzt fachliche Gewohnheiten. Berechtigungen, unveraenderte
explizite Kundenangaben, gueltige Einheiten und verfuegbare Kapazitaet bleiben
verbindliche Grenzen. Eine statistisch wahrscheinliche Ausnahme darf diese
Grenzen nicht aufheben.

## Human in the Loop und Rueckkopplung

Der bestehende Bestell-Inbox-Pruefweg zeigt Original, Ergaenzungen, Herkunft,
Alternativen und die konkret unsicheren Felder. Der Bearbeiter bestaetigt oder
korrigiert gezielt diese Felder. Eine Kundenrueckfrage wird nur vorbereitet,
wenn der Bearbeiter die fehlende Information nicht aus autorisierten Quellen
klaeren kann; keine pauschale Rueckfrage wegen jedes ausgelassenen Feldes.

Vorschlag, endgueltiger Wert, Entscheidung, gepruefter Urheber, Zeitpunkt und
Quellenbeleg bilden ein nachvollziehbares Feedbackereignis. Positive und
negative Korrekturen wirken auf spaetere Kandidaten. Manuell bestaetigte
Inhalte werden als solche markiert; die tatsaechliche Auftragserfuellung ist
ein separates staerkeres Ergebnis. Verwerfen bedeutet nicht automatisch,
dass jeder vorgeschlagene Feldwert falsch war.

Ungepruefte Entwuerfe, LLM-Ausgaben, technische Wiederholungen und eigene
automatische Uebernahmen zaehlen nicht als neue unabhängige Lernbeispiele.
Ein Auftrag liefert trotz mehrerer Importversuche nur ein Ergebnis. So kann
sich ein urspruenglicher Fehler nicht durch Wiederholung selbst bestaetigen.
Mandanten- und Kundenmuster bleiben getrennt; mandantenuebergreifendes Lernen
ist durch diesen Vertrag nicht freigegeben.

Fachliche Kundenkorrektur und betriebliche Dispositionsabweichung sind
verschiedene Feedbackarten. Mengenkuerzung wegen Kammerumverteilung,
Teilbelieferung wegen Tourknappheit und eine nur fuer den Notfall akzeptierte
Ersatzsorte werden **nicht** als normale Mengen-, Gebinde-, Silo- oder
Sortenpraeferenz gelernt. Wunsch, bestaetigte Bestellung, Allokation und
tatsaechliche Lieferung bleiben getrennte Merkmale. Das System darf aus
belegten Ausnahmeentscheidungen lernen, welche Notfallvorschlaege brauchbar
waren; es darf damit weder eine Notfallfreigabe selbst erteilen noch die
normalen Kundenmuster umdeuten. Eine dauerhafte Kundenaenderung benoetigt
eine gesondert nachvollziehbare fachliche Bestaetigung.

## Lieferplanung und Kundeninformation

Lieferwunsch und geplanter Liefertermin sind getrennte Angaben. Ein altes
Lieferdatum wird niemals als neues Lieferdatum kopiert. Historie liefert
bevorzugte Tour-/Zeitfenster; aktuelle Disposition liefert moegliche Termine
unter Beruecksichtigung von Bestand, Fahrzeug-/Silo-Eignung, Tourkapazitaet,
Annahmeschluss, Betriebs-/Feiertagskalender und Lieferstelle.

Ohne ausdruecklichen Wunsch wird der frueheste passende verfuegbare Termin
vorgeschlagen. Bei Stueckgut ist dies in der Regel der naechste verfuegbare
Termin der festen Kundentour, nicht pauschal morgen und nicht "heute plus
sieben Tage". Ein bekannter Wochenrhythmus kann einen anderen Termin nur
erklaeren, nicht eine ausgefallene oder volle Tour als verfuegbar ausgeben.

Kann nicht am Folgetag geliefert werden, wird eine Kundeninformation mit dem
geprueften Termin vorbereitet. Auch Stammkunden mit bekanntem Wochenrhythmus
werden von dieser User-Vorgabe nicht still ausgenommen. Ein ausdruecklicher
spaeterer Wunsch wird beruecksichtigt; die Nachricht stellt ihn nicht als
Verzoegerung dar. Ein nicht erfuellbarer ausdruecklicher Termin wird nie
ueberschrieben, sondern zusammen mit einer Alternative geklaert. Bei fehlender
Verfuegbarkeitsquelle wird kein Termin zugesagt; Disposition muss klaeren.

Nachrichten verwenden den bestehenden persistenten pending_browser-Auftrag,
einen fachlich stabilen Replay-Schluessel und den verifizierten Empfaenger.
Terminabweichung, Vorbereitung, Versand und Zustellung bleiben getrennte
Nachweise. Wiederholte Planung erzeugt keine doppelte Kundenmeldung.

## Seltene Last-minute-Disposition (User-Vorgabe 2026-10-12)

Bei dringenden spaeten Bestellungen koennen verfuegbare Touren und Beladung
eine vollstaendige Wunschlieferung am selben Tag verhindern. Ein Gliederzug
oder Sattelauflieger kann mehrere beladene Kammern/Kessel haben. Einzelne
Kammerinhalte koennen ausnahmsweise von einem bereits geplanten Kunden zu
einem dringenden Kunden umdisponiert werden. Entfernte Ladestellen werden
gegebenenfalls nur morgens angefahren; kundenspezifische Mischungen stehen
eventuell erst am naechsten Morgen bereit. Eine geeignete, akzeptierte
Ersatzsorte kann den dringenden Bedarf als Teilmenge ueberbruecken; die
Restmenge der bestellten Wunschsorte folgt zum geprueften naechsten Werktag.
Dies bleibt ausdruecklich eine Ausnahme, keine normale Erfuellungsstrategie.

### Entscheidungs- und Mengenvertrag

- Die urspruengliche Bestellung beider Kunden bleibt erhalten. Eine andere
  Tagesallokation ist keine stillschweigende Bestellmengenkuerzung oder
  Stornierung. Die beim abgebenden Kunden fehlende Menge bleibt offen,
  soweit keine ausdrueckliche fachliche Aenderung bestaetigt wurde.
- Ein Vorschlag benennt Dringlichkeitsgrund, Quellauftrag, Zielauftrag,
  Tour/Fahrzeug/Kammer, tatsaechlich verfuegbare Artikel-/Chargenmenge,
  Einheit, Lieferstelle/Silo und die Auswirkungen auf beide Lieferzusagen.
  Geplante Kammerkapazitaet ist kein Nachweis des wirklich geladenen Inhalts.
  Bereits entladene oder anderweitig gebundene Mengen sind nicht verfuegbar.
- KI schlaegt Alternativen vor; ein berechtigter Disponent gibt diese
  kundenuebergreifende Ausnahme frei. Die Ersatzsorte braucht dokumentierte
  Kundenakzeptanz oder eine bereits gueltige ausdrueckliche Ersatzfreigabe.
  Ein aehnlicher Name, KI-Score oder gleiche Artikelgruppe beweist keine
  Eignung. Artikel-/Qualitaets-, Einsatz-, Lieferstellen-/Silo- und
  Fahrzeug-/Kammerbedingungen sowie bestehende Fachsperren werden geprueft.
- Der Ersatzartikel wird als tatsaechlicher Artikel mit seiner eigenen
  Identitaet/Charge dokumentiert. Er wird nicht unter dem Artikel der
  Wunschsorte ausgebucht, geliefert oder abgerechnet. Anrechnung auf die
  bestellte Menge und etwaige Preisabweichung werden ausdruecklich festgelegt;
  keine pauschale Gleichsetzung verschiedener Einheiten oder Produkte.
- Quellallokation reduzieren, Zielallokation erhoehen, Restverpflichtungen
  fuehren und Freigabe/Audit speichern ist ein zusammenhaengender Vorgang.
  Dieselbe Kammermenge darf nicht zwei Kunden zugleich zugesagt werden.
  Parallele Disposition, Wiederholung oder Abbruch darf keine Doppelallokation
  und keine verlorene Restmenge erzeugen. Eine Ruecknahme stellt die
  betroffenen Allokationen nachvollziehbar wieder her.
- Die Folgetour fuer **beide** offenen Restmengen wird gegen aktuelle
  Ladebereitschaft, Annahmeschluss, Werktagskalender und Transportkapazitaet
  geprueft. "Naechster Morgen" oder "naechster Werktag" ist keine automatische
  Zusage. Fehlt die Verfuegbarkeit, muss die Disposition eine Alternative
  klaeren; die Restpflicht bleibt offen.
- Betroffene Kunden erhalten die fuer sie relevante Information ueber
  Artikel, Teilmenge, offene Restmenge und geprueften Folgetermin. Keine
  Offenlegung von Namen, Auftraegen oder Dringlichkeitsdetails anderer Kunden.
  Versand folgt dem bestehenden persistenten Browser-Auftragsvertrag.
  Gleicher LKW oder gleiche Ladestelle erlaubt keinen Mandantenwechsel.

### Beispiel mit bereits freigegebener mengenmaessiger Anrechnung

Ein Kunde hat 12 t bestellt. Eine tatsaechlich mit 4 t beladene Kammer wird
zum dringenden Kunden umdisponiert: Der erste Kunde erhaelt heute 8 t und
hat weiterhin 4 t offen. Der dringende Kunde hat 6 t Wunschsorte bestellt
und akzeptiert ausnahmsweise 4 t Ersatzsorte als anrechenbare Ueberbrueckung:
heute 4 t Ersatzsorte, weiterhin 2 t Wunschsorte offen. Beide Restmengen
erhalten einen gesondert geprueften Folgetermin. Das Beispiel setzt die
Ersatzfreigabe und Anrechnung voraus; es behauptet keine fachliche
Gleichwertigkeit der Sorten.

Das Lernsystem sieht weiterhin 12 t als Bestellung des ersten Kunden und
6 t der Wunschsorte als Bestellung des dringenden Kunden. Die Tageslieferungen
8 t bzw. 4 t Ersatz sind belegte Ausnahmeergebnisse, keine neuen Standardwerte.

### Integration und Ausnahmebetrieb

Im geprueften Python-Bestand von app/services und app/api/v1/endpoints ist
kein fachlicher Kammer-/Kessel-Allokationsvertrag fuer diesen Bestelleingang
nachgewiesen. Bestehende Rationsassistenz
`app/services/feeding_assist_service.py::substitutes` erzeugt Kandidaten fuer
Einzelfutter; sie beweist weder Ersatzfreigabe fuer eine kundenspezifische
Kraftfuttermischung noch Transport-, Kammer- oder Restmengenumbuchung. Keine
zweite Ausnahme-Auftragsdatenbank oder automatische Nutzung dieses
Rationspfads als Freigabe einfuehren.

Die Umsetzung benoetigt einen abgegrenzten Fachcommand auf bestehenden
Auftrags-/Dispositionsvertraegen mit den oben genannten atomaren Nachweisen.
Der normale Lern-/Bestellweg startet keine Kammerumbuchung. Der Ausnahmepfad
kennzeichnet Ursache, Freigabe und Auswirkungen dauerhaft. Ausnahmehaeufigkeit,
offene Restmengen, verspaetete Folgelieferungen und Folgen fuer abgebende Kunden
werden beobachtet. Wachsende Ausnahmehaeufigkeit wird der Disposition als
Kapazitaets-/Planungsproblem sichtbar; sie erweitert nicht selbst die
Freigaberegel. Keine ungemessene feste Prozentgrenze als User-Vorgabe erfinden.

## Integration und Betrieb

Die persistente Bestell-Inbox bleibt Einstieg. Kein zweites lernendes
Bestellmodell im Simulator und kein neuer separater Container/Datenspeicher
nur fuer diese Funktion. Historienadapter beziehen bestaetigte kanonische
Auftraege; fehlende Silo-/Gebindevertraege werden zuerst mit ihren Verbrauchern
geklaert, statt diese Werte lediglich in einer zweiten JSON-Historie zu fuehren.

Historien werden nach autorisiertem Mandant/Kunde/Artikel begrenzt abgefragt,
Kandidaten einmal je Eingang bewertet. Wiederholte Formulierungen benoetigen
keinen unbeschraenkten LLM-Aufruf und keine Vollhistorie im Prompt. Ein Cache
muss Kontext, Historien-/Modellversion und Widerruf beruecksichtigen. Feedback
wird inkrementell verarbeitet; nachvollziehbare Versionen erlauben Ruecknahme
einer schlechten Modellaktualisierung ohne Loeschen der Originalentscheidungen.

Im Betrieb werden pro Feld und Kundengruppe Korrekturrate, fachliche Fehler,
Anteil automatisch ergaenzter Felder, Klaerungsbedarf, Bearbeitungszeit,
Latenz/Kosten und Musterwechsel beobachtet. Hohe automatische Uebernahmequote
allein ist kein Erfolg. Bei schlechter Kalibrierung oder Drift wird wieder
auf menschliche Pruefung gestellt. Kein Online-Training mit Chatinhalten in
einem fremden oder allgemeinen Kundenkontext.

## Umsetzungsreihenfolge und Abnahme

| Slice | Inhalt | Nachweis vor Abschluss |
| --- | --- | --- |
| WHATSAPP-INBOX-TRUST-20261011 | Verifizierte Inbox-Rechte, Kunden-/Artikelreferenzen, Urheber und Eingangs-Replay; Original und Korrektur atomar nachvollziehbar | Zwei echte Mandanten, fremde Referenz/Token/Header, unveraenderte Daten bei Ablehnung, konkurrierender Replay im gemeinsamen Pruefstand |
| WHATSAPP-ORDER-HISTORY-20261011 | Kanonische Silo-/Gebinde-/Einheitenvertraege und begrenzte autorisierte Historie | Verbraucher-/Schemaabgleich, keine Konkurrenzhistorie, unterschiedliche Lieferstellen und Varianten getrennt |
| WHATSAPP-LEARNING-ENGINE-20261011 | Lernende Kandidaten, feldbezogene Unsicherheit, menschliches Feedback und kalibrierte Uebernahme | Zeitlich getrennte Bewertungsdaten; explizite Angaben unveraendert; korrigiertes Muster verbessert Folgefall; Cold Start, konkurrierende Mengen/Silos und Saisonwechsel; kein Lern-Replay/Trainingsleck |
| WHATSAPP-DELIVERY-PLANNING-20261011 | Verfuegbarkeitsanbindung und feste Stueckguttouren, Alternativen und Kundeninformation | Folgetag verfuegbar/nicht verfuegbar; volle Tour, Annahmeschluss, Feiertag, Wochenwechsel, expliziter Wunsch; keine Zusage ohne aktuelle Quelle; keine doppelte Meldung |
| WHATSAPP-EMERGENCY-ALLOCATION-20261012 | Seltene freigegebene Kammerumverteilung, Ersatz-Teilmenge und Restverpflichtungen beider Kunden | Mengenbilanz und richtige Artikel/Chargen; beide Kunden ohne fremde Details informiert; fehlende Ersatz-/Dispositionsfreigabe abgewiesen; konkurrierende Allokation, Replay/Rollback und Ruecknahme; unmoeglicher Folgetermin bleibt offen; Ausnahmen verfälschen keine normalen Lernmuster |
| Bestehender WHATSAPP-WEB-INTEGRATION-20261011 | Konto-/Chatbindung und Browser-Versandnachweis | Autorisierter konkreter Testempfaenger; Abbruch vor/nach Senden und Wiederanlauf ohne Doppelversand |

Die Code-Slices bleiben offen und sind vor Umsetzung separat zu claimen.
INBOX-TRUST hat den abgeschlossenen Teilschnitt INBOX-ACCESS-20261012; dieser
ersetzt nicht die noch offene Replay-/Original-/Korrektur-Abnahme.
Tests nutzen ausschliesslich den bestehenden gemeinsamen Pruefstand, eigene
Datensaetze oder Savepoints; keine neue Testdatenbank und kein neuer Container.

## Referenzen

- [Browser- und Benachrichtigungsvertrag](whatsapp-web-computer-use.md)
- [CRM Domain Pack](../architecture/domains/crm/README.md)
- [Aktives Workboard](../agent-ops/active-workboard.md)
- [Abnahme der Benachrichtigungspersistenz](../quality-assurance/whatsapp-persistence-20261011.md)
