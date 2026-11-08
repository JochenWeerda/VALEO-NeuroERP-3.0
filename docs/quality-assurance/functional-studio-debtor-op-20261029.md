---
title: Studio Debitoren OP-Liste — QA-Begleitnotiz
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-29
version: 1.0.0
description: Abgenommene Fach-, Waehrungs- und Kanalvertraege der Studio-Debitoren-OP-Liste.
---

# Studio Debitoren OP-Liste

Diese Notiz dokumentiert die gezielte Abnahme der Debitoren-OP-Liste und ihrer
gemeinsamen Lesewege. Sie ersetzt keine Gesamtfreigabe aller ERP-Masken.

## Screen und Fachquelle

Die Route `/fibu/debitoren` bindet `NativeListPage` an die kanonische
ScreenDefinition `fibu/debitoren-liste`. Die Datenquelle fordert
`/api/v1/finance/open-items?konto_typ=debitoren&only_open=true` an. Der
Open-Items-Endpunkt zählt den Bestand mit denselben Mandanten- und
Debitoren-/Offenbedingungen vor der Seitenauswahl; die Zeilenabfrage verwendet
`limit` und `offset`. `only_open` schließt Posten ohne offenen Betrag und
geschlossene Status aus. `ueberfaellig` kommt als fachliches Boolean aus dem
Open-Item-DTO (`offen > 0` und Fälligkeit vor heute), nicht aus einer
seiteneigenen Datumsableitung.

Die Tabelle zeigt die kanonischen Rechnungs-, Kunden-, Konto-, Datums-,
Betrags-, Mahnstufen- und Fälligkeitsinformationen einschließlich `waehrung`.
Der Zeilenweg ist `/finance/ar-open-item/{id}`. Eine OP-Kennung wird damit als
Open Item geöffnet und nicht als Verkaufsrechnungskennung interpretiert.

## Kennzahlen und Währung

Die Listenmetadaten deklarieren Zähler für alle offenen Treffer, überfällige
Treffer und Mahnstufen ungleich null sowie eine Summe des offenen Betrags.
Die Summeneinheit ist an das Datenfeld `waehrung` gebunden. Betragsspalten
formatieren ebenfalls anhand dieses Feldes; ein festes EUR-Format ist kein
fachlicher Ersatz für die tatsächliche Einheit.

Für gemischte, ungültige oder nicht sicher summierbare Währungen bleiben die
Open-Item-Zeilen lesbar. Die Kennzahl wird ausgelassen und eine
Kennzahlenwarnung angezeigt; es wird keine währungsübergreifende Summe und
keine ersatzweise EUR-Summe ausgewiesen.

Backend und Kanäle verwenden denselben deklarativen Listenvertrag. Die
gemeinsame Tabellenprojektion wendet Suche und Filter auf den vollständigen
begrenzten Bestand an, berechnet Zähler/Summen vor dem Seitenschnitt und
antwortet mit `aggregates` plus `aggregate_currencies` oder mit
`aggregate_error`. Die Filterung der OP-Fachquelle und ihre `COUNT`-/`OFFSET`-
Seitenauswahl bleiben Teil des kanonischen REST-Vertrags.

Damit sind die Kennzahlen über Backend-Projektion, REST, MCP und CLI an dieselbe
ScreenDefinition gebunden: offene Gesamtzahl, Summe des offenen Betrags je
sicherer Währungseinheit, überfällige Anzahl und Anzahl der Posten mit
Mahnstufe größer null. Es gelten dieselben aktuellen Such- und Filterbedingungen
für Kennzahlen und Zeilen; der Seitenschnitt begrenzt nur die angezeigten Zeilen.
Bei gemischten Währungen liefert die Projektion einen Kennzahlenfehler statt
einer zusammengezogenen Summe. Die Liste bleibt dabei mit den einzelnen
Währungsbeträgen nutzbar.

Der REST-Pfad `/api/v1/masks/{screen}/data/{source}` ruft die gemeinsame
MaskData-Leseprojektion mit verifiziertem Mandanten- und Aufruferkontext auf.
MCP `mask.data.read` und CLI `daten` verwenden dieselbe Projektion und damit
dieselben Such-, Filter-, Paging- und Kennzahlenregeln. Ein direkter
Fachendpunkt für offene Posten bleibt davon getrennt; die Listenkennzahlen
werden über den registrierten MaskData-Tabellenvertrag transportiert.

## Bedien- und Exportvertrag

Die Suche beschränkt sich auf Rechnungsnummer, Kundenname und Kontonummer; die
gemeinsame Runtime lädt paginierte Quellseiten vollständig und wendet die Suche
über den geladenen Bestand an. Der CSV-Export verwendet ausschließlich die
deklarierten kanonischen Listenspalten einschließlich Währung und der aktuellen
gefilterten Sicht. Er ist ein CSV-Download und kein DATEV-Export. Die
Rücknavigation zur
OP-Verwaltung ist als lokale Navigation deklariert, ohne eine Neuanlage oder
zusätzliche Berechtigung vorzutäuschen.

Lade- und Kennzahlenfehler müssen sichtbar bleiben. Ein Kennzahlenfehler darf
die Open-Item-Zeilen nicht in einen leeren Erfolg oder einen Fehlerzustand der
gesamten Liste umdeuten.

## Verifikationsstatus und Grenzen

Der finale Stand besteht mit 81 gezielten Tests: 30 isolierte Backendvertraege,
fuenf CRM-Proxyvertraege, 45 Frontend-/Compilerfaelle und einem signierten
PostgreSQL-Szenario. Letzteres prueft REST/MCP/CLI-Paritaet, COUNT/OFFSET,
exakte Cent-Summe, Rollen-/Mandantenabweisung, kanonische Detailzusammenfassung
und zwei getrennte Zahlungshistorien anhand ihrer strukturierten Auditverknuepfung.
Der urspruenglich falsche OP-ID-Sprung auf eine Verkaufsrechnung ist beseitigt.
Die gemeinsame OP-Verwaltung liest ebenfalls offene Posten statt Anlagen.

Vollstaendige Typpruefung ist gruen. Der Produktionsbuild ist nach der finalen UTF-8-Textkorrektur ebenfalls gruen.
Zwoelf synthetische Ansichten der echten NativeListPage sind abgenommen: EUR/Mixed,
jeweils 1366/1440/1920 Pixel und Hell/Dunkel, ohne horizontalen Ueberlauf,
JavaScriptfehler oder axe WCAG2A/AA-Befunde. Im Auswahlpanel sind EUR und USD
explizit formatiert; gemischte Summen bleiben gesperrt.
[Bilder und Messergebnisse](screenshots/studio-debtor-20261029/results.json). Die reine Runtime-Zaehlung ist E804/851 (47 verbleibend),
Gate A/B/C jeweils851.
Die obsolete zweite Kennung fibu/debitoren wurde nach Verbraucherpruefung
entfernt; das ist keine zusaetzliche funktional migrierte Maske.

Die Testdaten sind synthetisch. Für diesen Slice wird keine neue Testdatenbank
und kein neuer Docker-Container angelegt. Eine angemeldete Browserabnahme und
reale Mandanten-/Fachdatensatzprüfung sind von diesem Quell- und
Runtime-Vertrag getrennte Nachweise.

Bestehende Grenzen: Der vorhandene Settlement-Schreibweg ist nicht Gegenstand
dieser Lesemigration. Insbesondere ersetzt die Anzeige der real gespeicherten
Journalwaehrung keine finanzielle Fremdwaehrungs-Buchungsabnahme. Der vollstaendige
Listenabruf bleibt auf 5.000 Zeilen begrenzt; unvollstaendige Quellantworten werden
abgewiesen. Die Aktivitaetenmaske bleibt ein eigener offener Slice mit Datum-/
Verantwortlichenfiltern und korrektem Paging. Keine Gesamtfreigabe aller Masken.

## Portal-Nebenbefund

Die verwaiste Detaildefinition portal/zertifikat samt Registry/Routenalias und
unbelegtem Editrecht ist entfernt. Die sichere bestehende Liste portal/zertifikate
bleibt unveraendert. Ihre Quelle besitzt noch keine kundenautorisierte Zertifikats-
zuordnung; deswegen wird kein Detail-/Downloadendpoint erfunden. Ein gezielter
Regressionstest besteht. Diese Bereinigung ist keine neue Fachfunktion und keine
Abnahme eines Zertifikats-Downloads. Der vorherige Gate-C-Verweis war ein
Artefaktwiderspruch, der dadurch beseitigt wird.
