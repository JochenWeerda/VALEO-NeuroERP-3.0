# EUDR-Chargenkennzeichnung und EU-Anbindung (Slice EUDR-CHARGENKENNZEICHNUNG-20261001)

Stand: 2026-10-05 · Vorgänger: [EUDR-Sorgfaltserklärung](eudr-sorgfaltserklaerung-20261001.md)

## Die Lücke

Der Vorgängerslice hat das Register nach Verordnung (EU) 2023/1115 modelliert:
Erklärung, Geolokation, Risikobewertung, Einreichung. Was fehlte, war die
Verbindung zur Ware. Art. 4 Abs. 1 verbietet das Inverkehrbringen eines
relevanten Erzeugnisses, **bevor** eine Sorgfaltserklärung abgegeben ist. Ohne
eine Verbindung zwischen Charge und Erklärung kann niemand sagen, welche Ware
verkehrsfähig ist — das Register war ein Aktenschrank ohne Bezug zum Lager.

Zweite Lücke: Das Register kannte nur den eigenen Haushalt. Nach Art. 4 Abs. 9
darf sich ein Marktteilnehmer auf eine vorgelagerte Erklärung berufen, muss sie
aber **prüfen**. Nach Art. 33 läuft Einreichung und Abruf über das
EU-Informationssystem. Ein Register, das nur schreibt, macht das Haus zum ersten
Inverkehrbringer jeder Lieferung — auch dort, wo ein Vorlieferant die Sorgfalt
schon getragen hat.

## Was jetzt gilt

### Chargenkennzeichnung (Migration `eudr_chargenkennzeichnung_20261001`)

* `domain_inventory.inventory_lots.eudr_relevant BOOLEAN NOT NULL DEFAULT FALSE` —
  die Kennzeichnung sitzt auf der kanonischen Chargentabelle, nicht auf einer
  Nebentabelle. Standard `FALSE`: Relevanz nach Anhang I ist eine Aussage, die
  ein Haus trifft, keine, die eine Migration unterstellt.
* `domain_inventory.lot_eudr_erklaerungen (id, tenant_id, lot_id → inventory_lots
  ON DELETE CASCADE, erklaerung_id → eudr_due_diligence ON DELETE RESTRICT,
  menge_kg CHECK > 0, verknuepft_am, verknuepft_durch)` + `ux_lot_eudr_paar`
  auf `(tenant_id, lot_id, erklaerung_id)`.

**Warum eine Verbindung mit Menge und keine Spalte.** Im Landhandel wird
verschnitten. Eine Silocharge aus drei Anlieferungen trägt drei Erklärungen. Eine
Spalte `erklaerung_id` auf der Charge hätte erzwungen, dass genau eine davon die
Wahrheit ist — der Rest wäre verloren, und zwar genau der Teil, den eine Behörde
nach Art. 10 Abs. 4 fünf Jahre lang sehen will.

**Warum `ON DELETE RESTRICT` auf die Erklärung.** Die Erklärung ist der Nachweis.
Eine Charge darf verschwinden (verbraucht, verkauft, zusammengeführt); der
Nachweis, der sie gedeckt hat, darf das nicht, solange eine Bindung ihn
referenziert. Umgekehrt `CASCADE`: Verschwindet die Charge, verschwindet die
Bindung — die Erklärung bleibt.

**Der Nachweisstand ist abgeleitet, nicht gespeichert.** `NICHT_RELEVANT` /
`NACHGEWIESEN` / `OFFEN` fällt aus dem Vergleich von `current_qty` gegen die Summe
der gebundenen Mengen (`eudr_register_service.KENNZEICHNUNG`). Eine gespeicherte
Kennzeichnung wäre eine zweite Wahrheit, die von der ersten abweichen kann — und
abweichen *würde*, sobald jemand eine Bindung löscht oder eine Chargenmenge
korrigiert. Der Preis ist ein Join pro Abfrage; der Gegenwert ist, dass die
Anzeige nicht lügen kann.

### Übermittlung in beide Richtungen (Migration `eudr_uebermittlung_20261001`)

Ausgehend auf `eudr_due_diligence`: `uebermittlung_status`, `eu_system_id`,
`uebermittelt_am`, `uebermittlung_versuche`, `uebermittlung_fehler`,
`uebermittlung_dienst`, `uebermittlung_umgebung`.

Eingehend auf `eudr_vorgelagerte_erklaerungen`: `pruefung_status`, `geprueft_am`,
`pruefung_quelle`, `pruefung_hinweis`.

Prüfbedingungen:

| Bedingung | Was sie verhindert |
| --- | --- |
| `ck_eudr_uebermittelt_belegt` | Ein Status `UEBERMITTELT` ohne `eu_system_id` und ohne Zeitpunkt — eine Übermittlung, die niemand nachweisen kann. |
| `ck_eudr_abgewiesen_begruendet` | Ein `ABGEWIESEN` ohne Fehlertext; der Grund ist der einzige Weg zurück. |
| `ck_eudr_uebermittlung_umgebung_pflicht` | Eine Übermittlung ohne Angabe der Umgebung. |
| `ck_eudr_vorgelagert_bestaetigung` | Ein `BESTAETIGT` aus dem `EU_INFORMATIONSSYSTEM` ohne Verifizierungsnummer — eine Bestätigung ohne das Einzige, womit sie überprüfbar wäre. |

**Warum `uebermittlung_umgebung` (`PRODUKTION` / `ANNAHMETEST`) eine eigene Spalte
ist und kein Konfigurationswert.** Das EU-System hat eine Akzeptanzumgebung. Eine
dort eingereichte Erklärung erhält eine echte Referenz- und Verifizierungsnummer
und sieht in jeder Spalte wie eine produktive aus. Wenn die Umgebung nur in der
Anwendungskonfiguration steht, dann zählt nach dem nächsten Umschalten jede
Testeinreichung als Compliance — und genau das würde niemandem auffallen, weil
die Zeile vollständig aussieht. Die Umgebung gehört zum Nachweis, nicht zum
Betrieb.

## Zur Frage der Bidirektionalität

Der Einwand war richtig. `EUDRDueDiligenceStatementServiceV3` führt Einreichung
und Abruf in **einem** Dienst zusammen; V3 ist gegenüber V2 brechend genau darin,
dass der Abruf dazugekommen ist. Zwei Abrufwege sind fachlich verschieden:

* **nach interner Referenz** — „was habe ich eingereicht?" Das ist die Rückmeldung
  auf den eigenen Schreibweg und füllt `eu_system_id` / `uebermittelt_am`.
* **nach Referenz- *und* Verifizierungsnummer** — „stimmt, was mein Vorlieferant
  mir genannt hat?" Das ist der Prüfweg nach Art. 4 Abs. 9 und füllt
  `pruefung_status` / `geprueft_am` / `pruefung_quelle`.

Nur der zweite Weg macht aus dem Haus einen nachgelagerten Marktteilnehmer statt
eines ersten Inverkehrbringers. Deshalb ist er modelliert, und deshalb verlangt
`ck_eudr_vorgelagert_bestaetigung` die Verifizierungsnummer: Ohne sie ist der
Abruf nicht möglich, und eine Bestätigung ohne möglichen Abruf ist eine
Behauptung.

Das Datenmodell ist **transportneutral**. Es hält fest, *was* das EU-System
gemeldet hat, nicht *wie* es befragt wurde. SOAP, WS-Security und WSDL kommen in
keiner Spalte vor.

## Adapter-Recherche (kostenlose Importschnittstellen)

| Client | Sprache | Lizenz | Stand |
| --- | --- | --- | --- |
| `mfrntic/eudr-api-client` | Node.js / `node-soap` | **AGPL-3.0** | V3-Clients funktionsfähig, V1/V2 im Repo als nicht funktionsfähig markiert |
| `gschurgast/eudr-api-client` | PHP | MIT (**von mir nicht verifiziert**) | submit/amend/retract + Abruf mit typisierten DTOs |
| `zeep` gegen das offizielle WSDL | Python | eigener Code, keine Fremdlizenz | kein Client, sondern ein SOAP-Stack |

Zwei Korrekturen zur Ausgangsrecherche:

1. **V3 ist der funktionsfähige Teil** von `mfrntic/eudr-api-client`, nicht ein
   Nachzügler. V1/V2 sind dort ausdrücklich als nicht funktionsfähig geführt. Der
   Plan „V2-Reste entfernen" ist damit kleiner als gedacht.
2. **Die Lizenz ist AGPL-3.0**, nicht MIT. Das ist die eigentliche Entscheidung:
   AGPL-3.0 greift auch über Netzwerknutzung. Ein kommerzielles ERP, das diesen
   Client in einem Dienst betreibt, den Kunden über das Netz erreichen, steht vor
   einer Copyleft-Frage, die kein technisches Argument auflöst. Ein eigener
   Prozess mit eigener Schnittstelle *kann* die Grenze sein — das ist aber eine
   Rechts-, keine Architekturfrage und gehört vor den ersten produktiven Einsatz
   geklärt.

Deshalb bleibt der naheliegende Weg der eigene: Der Adapter läuft serverseitig,
wo der Stack Python ist. `zeep` gegen das offizielle V3-WSDL ist derselbe Aufwand
wie das Validieren eines fremden Clients, ohne Lizenzfrage und ohne einen zweiten
Laufzeitstack im Betrieb. Der Node-Client bleibt wertvoll als
**Referenzimplementierung**: Was in ihm `eudr-repository` und `eudr-test` heißen,
ist die Trennung, die hier zu `uebermittlung_umgebung` geworden ist, und seine
Abrufoperationen (Abruf nach Identifikatoren, Verifikation) sind die Operationen
hinter `vorgelagerte/.../pruefung`.

Was ich **nicht** geprüft habe: die MIT-Lizenz des PHP-Clients und die offizielle
V3-Dokumentationsseite. Beides steht hier als Angabe aus der Recherche, nicht als
Befund.

## Die Grenze `EudrProvider`

Nach der Vorgabe wird kein fremder Client in Finance, Inventory oder Sales
importiert. Der Zuschnitt dieses Slices zieht die Naht vor:

```
Fachmodule ─▶ eudr_register_service (kanonisches Modell, Ableitung)
                      ▲
          ┌───────────┴───────────┐
   eudr_register   eudr_chargen   eudr_anbindung  ← drei dünne Router
                                        │
                                   EudrProvider   ← noch nicht gebaut
                                   {TracesV3, LiveEO, Mock}
```

`eudr_anbindung.py` ist heute der einzige Ort, der von Übermittlung und Prüfung
weiß, und er schreibt ausschließlich in die kanonischen Spalten. Ein Adapter
tritt dort hinzu, ohne eine Zeile in den Fachmodulen zu ändern. Der erste E2E-Weg
bleibt der vorgeschlagene: Erklärung nach Referenz- und Verifizierungsnummer
einlesen → validieren → Charge zuordnen — er trifft genau
`pruefung_status`/`pruefung_quelle` und dann `lot_eudr_erklaerungen`.

## Zerlegung statt Godfile

`eudr_register.py` war nach dem Ausbau 1107 Zeilen und damit ein neuer Godfile.
Zerlegt entlang derselben Naht, die der Adapter braucht:

| Datei | Zeilen | Aufgabe |
| --- | --- | --- |
| `app/services/eudr_register_service.py` | 200 | Tabellennamen, abgeleitete Kennzeichnung, gemeinsame Helfer |
| `app/api/v1/endpoints/eudr_register.py` | 538 | Erklärung, Geolokation, Risiko, Einreichung |
| `app/api/v1/endpoints/eudr_chargen.py` | 189 | Bindung Ware ↔ Nachweis, offene Chargen |
| `app/api/v1/endpoints/eudr_anbindung.py` | 281 | Übermittlung aus, Prüfung ein |

Alle drei Router tragen `prefix="/eudr/sorgfaltserklaerungen"` und werden in
`api.py` in der Reihenfolge chargen → anbindung → register eingehängt, damit die
wörtlichen Pfade vor `/{erklaerung_id}` stehen. Umgekehrt hätte `/chargen/offen`
als Erklärungs-ID gegolten und 404 geliefert — die Reihenfolge ist hier
Fachlogik, keine Formsache.

## Maske

`/compliance/eudr` liefert jetzt `lots_relevant`, `lots_covered`, `lots_open`,
`open_quantity_kg` aus dem Register. `deforestation_risk` ist `UNBEKANNT`, solange
etwas unbewertet ist **oder** das Register leer ist. Die Maske
(`pages/nachhaltigkeit/eudr-compliance.tsx`) zeigt offene Chargen als roten
Hinweis mit Menge und dem Verbot aus Art. 4.

Vorher stand dort eine Compliance-Rate von 0,0 % **neben** dem Status „KONFORM",
weil der Endpunkt einen Lesefehler auf einer nie angelegten Tabelle abfing und
`NIEDRIG` meldete. Das ist das Muster dieser Welle: **Ein Fehler darf nie wie ein
leerer, konformer Zustand aussehen.**

## Nachweis

```
DATABASE_URL=…/valeo_probe python -m pytest \
  tests/test_eudr_chargenkennzeichnung_vertrag.py \
  tests/test_eudr_sorgfaltserklaerung_vertrag.py \
  tests/test_gap_fixes_batch1.py -q
→ 87 passed
```

Beide Migrationen gegen die frische `valeo_probe` **und** die gewachsene
`valeo_neuro_erp` hochgezogen. Gates: Tabellenverweise 12 an lebenden Wegen
(Schwelle 12), Baseline-Integrität OK, keine neue tote Transaktion, Paginierung
unverändert.

## Revisionsbaum

Zwei Agenten haben am 01.10. je eine Migration an
`eudr_sorgfaltserklaerung_20261001` gehängt. `zusammenfuehrung_20261005` führt
`bank_gl_binding_20261001` und `eudr_uebermittlung_20261001` ohne eigenes DDL
zusammen und stellt den Einzelkopf her, den jede Neuinstallation braucht.

## Offener Punkt (Handshake)

`app/api/v1/endpoints/logistics_tours.py` ist im geteilten Arbeitsbaum von 1033
auf 1059 Zeilen gewachsen und verletzt damit die Godfile-Ratsche. Die Änderung
ist nicht aus diesem Slice — sie gehört dem Agenten, der an der Tourenplanung
arbeitet, und bleibt unangetastet.
