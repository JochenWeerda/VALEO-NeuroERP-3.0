# Maske „Steuerschlüssel" als ScreenDefinition

Stand: 2026-10-13 · Slice `STEUERSCHLUESSEL-MASKE-SD-20261013` ·
Folge aus [Gutschrift: Agent schlägt vor, Mensch gibt frei](gutschrift-agent-freigabe-20261012.md)

## Auftrag

„Maske an Steuerschlüssel(-Tabelle) ändern, systemweit vereinheitlichen" und „no handmade masks,
Mask Builder und ScreenDefinitions nutzen, MCP- und CI-Schnittstellen" (Auftraggeber, 12.10.2026).

`domain_erp.tax_keys` ist die eine Quelle, aus der Belege Satz und Konten nehmen. Die Maske, mit
der die Buchhaltung diese Quelle pflegt, war die letzte handgebaute Stelle davor.

## Was die handgebaute Maske tat

- Sie belegte beim Anlegen den Satz 19, das „Konto Soll" 1400 und das „Konto Haben" 1776 vor. 1400
  ist das Forderungskonto, kein Steuerkonto.
- Sie kannte weder Erlöskonto noch § 24 UStG. Beides gab es seit dem 12.10. nur über die API.
- Sie konnte nichts ändern, nur anlegen.
- Scheiterte das Speichern, blieb der Dialog offen und zeigte nichts.

## Was jetzt gilt

- ScreenDefinition `finance/steuerschluessel` (`build_finance_steuerschluessel_screen_definition`),
  Registry, Agenten-Synonyme, Listenroute, TS-Kopie `financeSteuerschluesselScreen`. Die Seite
  `pages/finance/steuerschluessel.tsx` ist ein dünner Wrapper; der Mask Builder zeichnet.
- Kein Vorgabewert, weder für den Satz noch für ein Konto noch für „Gültig von".
- Felder: Schlüssel, Bezeichnung, Steuersatz, Umsatzsteuerkonto, Erlöskonto, Vorsteuerkonto, § 24 UStG,
  Reverse Charge, innergemeinschaftlich, Ausfuhr, UStVA-Kennzahl und -Text, Gültigkeit, Aktiv, Notizen.
- Die Tabelle zeigt je Schlüssel, **wofür er automatisch bucht** („Verkauf", „Einkauf") oder warum
  nicht („Bucht nicht automatisch: Für Steuerschlüssel 24 ist kein Erlöskonto hinterlegt."). Der Text
  kommt vom Server aus derselben Regel, die die Buchung anwendet (`verkauf_hindernis`).
- Speichern läuft über den Kommando-Weg `POST /api/v1/finance/tax-keys/actions/speichern`
  (`run_delegated_mask_action`: Trockenlauf, Audit, Outbox, Idempotenz), Rolle `finance_write`.
  Der Schlüssel entscheidet: vorhanden = Änderung, sonst Anlage. Die Antwort nennt bei einer
  Änderung jedes geänderte Feld mit altem und neuem Wert; so steht es auch im Audit.
- Vor dem Speichern fragt die Maske nach und sagt, ob angelegt oder geändert wird.

### Was der Server ablehnt

| Eingabe | Meldung |
|---|---|
| Steuersatz fehlt | „Steuersatz angeben; es gibt keinen Vorgabewert." |
| Steuersatz keine Zahl / außerhalb 0–100 | „Steuersatz: keine Zahl." / „… zwischen 0 und 100." |
| Schlüssel nicht ein oder zwei Ziffern | „Schlüssel: ein oder zwei Ziffern." |
| Bezeichnung oder „Gültig von" fehlt | Pflichtmeldung |
| „Gültig bis" vor „Gültig von" | „Gültig bis liegt vor Gültig von." |
| Reverse Charge mit Satz über 0 | „Reverse Charge verlangt den Steuersatz 0." |
| Konto steht nicht im Kontenplan des Mandanten | „Erlöskonto 8999 steht nicht im Kontenplan." |

Ein abgelehnter Wechsel lässt den Bestand unverändert.

## Agenten

Die Aktion `speichern` ist `forbiddenForAgents` und `humanApprovalRequired`; in der MCP-Aktionskarte
steht sie als bewusst gesperrt (`open_high`), ein MCP-Werkzeug gibt es nicht. Das folgt der
Architekturentscheidung vom 12.10.: Ein Agent darf eine Steuerregel vorschlagen, nie in Kraft setzen.
Ein Vorschlagsweg für Steuerschlüssel ist nicht gebaut; er gehört zum geplanten Tax Rules Service.

## Mitbehoben

1. **Die Schlüsselliste wurde nach Änderungen nicht aktualisiert.** `GET /finance/tax-keys` liegt
   eine Stunde im Cache; keiner der schreibenden Wege leerte ihn (`invalidate_tenant_prefix` war
   importiert, nie aufgerufen). Mit Redis sah die Auswahl in der Gutschrift einen neuen oder
   geänderten Schlüssel bis zu einer Stunde nicht. Jetzt leeren Anlegen, Ändern, Deaktivieren und
   der Kommando-Weg den Cache.
2. **Ein Ladefehler galt als leerer Bestand.** Die Liste fing jeden Fehler und gab `[]` zurück —
   und diese leere Liste lag dann eine Stunde im Cache. Jetzt: Rollback und 500.
3. **Fehlende UStVA-Kennzahl kam als Text „None" zurück.** Die Antwort wandelte `NULL` mit `str()`.
4. **Der Bauplan-Cache des Mask Builders übersah Schreibschutz und Untertitel.**
   `schemaVolatility` (`render-plan/schema-compiler.ts`) nahm nur Summen, Auswahlwerte, gesperrte
   Aktionen und Dichte in den Cache-Schlüssel. Setzte eine Seite zur Laufzeit ein Feld auf
   `readOnly`, zeichnete der Builder weiter den alten Plan — außer es änderte sich zufällig
   gleichzeitig etwas anderes (so bei der Gutschrift). Beim Bearbeiten eines Steuerschlüssels wäre
   das Feld „Schlüssel" änderbar geblieben. Betrifft jede Maske, die Felder zur Laufzeit sperrt.

Fünf wortgleiche Antwortblöcke in `tax_keys.py` sind eine Funktion (`_antwort`).

## Auslegungen (meine, nicht entschieden)

- **Ändern statt Versionieren.** Je Mandant gibt es einen Schlüssel einmal (`uq_tax_keys_tenant_code`).
  Ein Satzwechsel ändert die Zeile; gebuchte Belege tragen ihre Beträge selbst und bleiben
  unberührt. Schlüssel mit mehreren Gültigkeitszeiträumen gehören zum geplanten Tax Rules Service.
- **Kein Pflichtgrund bei Änderung.** Das Audit hält fest, wer wann was von welchem auf welchen
  Wert geändert hat; eine Begründung verlangt die Maske nicht.
- **Deaktivieren über „Aktiv".** Wie bisher über `PUT` genügt dafür `finance_write`; das Löschen
  über `DELETE` bleibt `finance_admin`.
- **Land nicht in der Maske.** Der Server setzt wie bisher `DE`.

## Nachweis

- `tests/test_steuerschluessel_maske.py`: 24 bestanden gegen `valeo_probe` — Anlage mit Erlöskonto
  und § 24, Liste sofort aktuell, Änderung mit Alt/Neu, Zurücknehmen des Erlöskontos und Inaktiv,
  Trockenlauf schreibt nichts, zwölf abgelehnte Eingaben ohne Schreibzugriff, Verwendungstext,
  Lesen reicht nicht zum Speichern, Ladefehler ist 500, ScreenDefinition (Governance, UX-Lint,
  `generatorReady`, Score 1,0), Agentensperre in Aktionskarte und Werkzeugliste.
- Mit Gutschrift- und Bestandstests der Steuerschlüssel: 74 bestanden.
- Nachbarn (Steuer, Masken-Plattform, MCP, Inventare; 79 Dateien): 1034 bestanden, 2 rot, beide ohne
  Bezug zu diesem Slice und ohne von ihm berührte Datei —
  `test_generate_architecture_index::test_build_index_mapping_complete` (`tenant_lifecycle_service`
  ohne Domain-Zuordnung) und `test_inventory_auxiliary::test_route_is_registered` (401).
  `test_mcp_client_lifecycle.py` (19 Fälle) lief auf diesem Windows-Rechner nicht durch
  (`UnicodeDecodeError` beim Lesen des Kindprozesses) und ist ausgenommen.
- Rollenvertrag `test_zahlung_stammdaten_rollen_vertrag.py`: 1828 bestanden; der neue Weg ist als
  `write` eingetragen.
- Vitest: Maske 6, Bauplan-Cache 2 (beide Cache-Tests waren vor der Korrektur rot), Mask-Builder-
  Verzeichnis und Gutschrift zusammen 228 bestanden. `tsc --noEmit` und ESLint ohne Befund.
- Gewachsene Datenbank `valeo_neuro_erp`: Liste des Testmandanten (vier SKR03-Schlüssel) mit
  Verwendungstext, Trockenlauf mit unveränderten Bestandswerten ohne Befund.
- Nachgezogen: Aktionskatalog (97 Aktionen, 49 Masken), MCP-Aktionskarte (`open_high` 4,
  `local_ui` 15), Agenten-Handbuch, OpenAPI (3142 Pfade), Zählwerte der MCP-Ratschen.
  `check_pagination`, `check_dead_transactions`, `check_baseline_integrity`, `check_initial_data`,
  Kommando-Weg-Inventar (0 Lücken): in Ordnung.

**Nicht geprüft:** die Maske im Browser. Seit der Identitätsgrenze vom 12.10. gibt es lokal keine
Anmeldung ohne Anbieterkonto.

## Offen

- Rund zehn Masken fragen weiter einen Prozentsatz ab statt eines Steuerschlüssels
  (Ausgangsrechnung, Eingangsrechnung, Rechnungseingang, Einkaufsgutschrift, Lieferschein,
  Bestellung, Zinsabrechnung, Artikelstamm, Kasse, Ernteannahme).
- Die alten Wege `POST`/`PUT`/`DELETE /finance/tax-keys` bestehen weiter (ohne Audit, ohne
  Kontenprüfung). Die Maske nutzt sie nicht mehr.
- Vorschlagsweg für Agenten und Schlüssel mit Gültigkeitszeiträumen: Tax Rules Service (geplant).

## Nachtrag: Konten aus dem Kontenplan (`STEUERSCHLUESSEL-KONTENVORSCHLAG-20261013`)

Auftrag vom 13.10.2026: „Kontonummern aus Kontenplan vorschlagen (fachliche kontextuelle Zuordnung)."

- Umsatzsteuer-, Erlös- und Vorsteuerkonto sind in der Maske eine **Auswahl aus dem Kontenplan** des
  Mandanten, kein Freitext mehr. Quelle: `GET /api/v1/finance/tax-keys/kontenvorschlaege?steuersatz=…`
  (`kontenvorschlaege` in `app/finance/steuerschluessel.py`).
- **Zuordnung nach Kontenart:** Umsatzsteuerkonto = Verbindlichkeitskonto, Vorsteuerkonto = Aktivkonto,
  Erlöskonto = Erlöskonto. Je Feld erscheinen nur Konten dieser Art, die bebuchbar sind (aktiv, nicht
  gesperrt, kein Summenkonto). Ein eigenes Konto des Mandanten geht dem gemeinsamen Rahmen vor.
- **Reihenfolge:** zuerst Konten, deren Bezeichnung zur Rolle **und** zum eingegebenen Satz passt
  („1776 – Umsatzsteuer 19 % (Vorschlag: passt zum Satz 19 %)"), dann Konten, die nur zur Rolle passen
  (Bezeichnung oder Kategorie „tax"), dann die übrigen der Art. „7 %" trifft „17 %" nicht.
- **Vorgeschlagen, nicht gewählt.** Die Felder bleiben leer, bis jemand wählt. Bei Satz 0 wird kein
  Steuerkonto als zum Satz passend gereiht.
- **Der Server prüft dieselbe Regel beim Speichern** (`konto_hindernis`): Ein Konto der falschen Art
  wird abgelehnt — „Umsatzsteuerkonto 1400 (Forderungen aus Lieferungen und Leistungen) ist kein
  Verbindlichkeitskonto." 1400 war die Vorgabe der alten Maske. Gesperrte Konten werden weder
  vorgeschlagen noch angenommen.
- Ein hinterlegtes Konto, das der Kontenplan nicht mehr anbietet, bleibt beim Bearbeiten sichtbar
  („nicht im Kontenplan, gesperrt oder falsche Kontenart").

**Auslegung (meine):** „fachlich kontextuell" heißt hier Kontenart plus Bezeichnung und Satz. Der
Kontenplan trägt kein eigenes Merkmal „Steuerkonto für Satz X"; die Kategorie `tax` ist nur bei den
am 12.10. angelegten Konten gesetzt, die gemeinsamen Konten 1576/1776 stehen unter
`current_assets`/`current_liabilities`. Die Reihung nach Bezeichnung ist deshalb eine Hilfe und
keine Zusicherung.

**Mask Builder, zweiter Cache-Fehler:** `schemaVolatility` nahm von Auswahlfeldern nur die Werte,
nicht die Beschriftung, in den Cache-Schlüssel. Bei gleichen Werten und neuer Beschriftung zeichnete
der Builder die alte Auswahl. Korrigiert, Test in `render-plan-cache.test.ts`.

**Nachweis:** `tests/test_steuerschluessel_maske.py` 31 bestanden gegen `valeo_probe` (neu: Reihung
nach Satz, 7 gegen 17, ohne Satz und bei 0, gesperrte Konten, drei Konten falscher Art). Gegen
`valeo_neuro_erp` von Hand: 19 % → 1776/1576/8400, 7 % → 1771/1571/8300. Vitest: Maske 8,
Bauplan-Cache 3, zusammen mit Mask-Builder-Verzeichnis und Gutschrift 231. `tsc`, ESLint ohne Befund.
Rollenvertrag: neuer Leseweg eingetragen. Nicht im Browser geprüft.
