---
title: Lernende Ergaenzung verkuerzter WhatsApp-Bestellungen
type: explanation
audience: [product, entwickler, agent, disposition, qa]
owner: Codex
status: geplant
last_reviewed: 2026-10-11
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
| `_enrich` im selben Service | Kunden-/Artikelmatch; keine Historienergaenzung und kein Lernen aus Korrekturen. Kundenmatch nimmt einen Fuzzy-Treffer aus kunden_lookup ohne Mandantenpraedikat. |
| `bestaetigen` im selben Service | Bestaetigung kann parsed ersetzen; erzeugt Kundenkontakt und Beleg-Vorbelegung. Kein unveraenderlicher Vorschlags-/Korrekturvergleich und keine echte Auftragsanlage. |
| `app/api/v1/endpoints/whatsapp_intake.py` | Separater Header-Mandantenvertrag, nicht die verifizierten Guards der reparierten Benachrichtigungsendpunkte; Eingangs-Replay-/Urheberabnahme offen. |
| `app/api/v1/endpoints/sales_orders.py::SalesOrderItemInput` | Artikel, Menge und Preis vorhanden; Einheit, Silo und Gebindegroesse fehlen in diesem Eingabevertrag. Historische Inbox-Bestaetigung ist daher kein Nachweis eines ausgefuehrten Auftrags. |
| Benachrichtigung | Persistente replaygeschuetzte Vorbereitung vorhanden; Browseranbindung und sichtbarer Versandnachweis offen. |

Dies ist ein **Fach- und Integrationsvertrag**, keine Behauptung einer bereits
implementierten lernenden Bestellverarbeitung. Die bisherigen festen
Extraktionswerte duerfen nicht als Freigabesicherheit weiterverwendet werden.

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
| Bestehender WHATSAPP-WEB-INTEGRATION-20261011 | Konto-/Chatbindung und Browser-Versandnachweis | Autorisierter konkreter Testempfaenger; Abbruch vor/nach Senden und Wiederanlauf ohne Doppelversand |

Die Code-Slices sind offen, unreserviert und vor Umsetzung separat zu claimen.
Tests nutzen ausschliesslich den bestehenden gemeinsamen Pruefstand, eigene
Datensaetze oder Savepoints; keine neue Testdatenbank und kein neuer Container.

## Referenzen

- [Browser- und Benachrichtigungsvertrag](whatsapp-web-computer-use.md)
- [CRM Domain Pack](../architecture/domains/crm/README.md)
- [Aktives Workboard](../agent-ops/active-workboard.md)
- [Abnahme der Benachrichtigungspersistenz](../quality-assurance/whatsapp-persistence-20261011.md)
