# Gutschrift: Agent schlägt vor, Mensch prüft und gibt frei, Agent bucht · `vat_codes` gelöscht

Stand: 2026-10-12 · Slices `GUTSCHRIFT-AGENT-FREIGABE-20261012` und `VAT-CODES-ENTFERNEN-20261012` ·
Folge aus [Gutschrift-Maske als ScreenDefinition](gutschrift-maske-sd-20261012.md)

## Entscheidungen des Auftraggebers (12.10.2026)

1. „vat_codes löschen."
2. „Für Agent Gutschriften buchen nach Muster human in the loop – prüft und gibt frei."

## Teil 1: `vat_codes` gelöscht

- Migration `vat_codes_entfernt_20261012` (ein Head): `vat_codes`, `vat_codes_audit` und der Typ
  `vatcodecategory` entfallen. Der Rückweg legt die leeren Tabellen wieder an, nicht ihren Inhalt.
- Entfernt: Wege `/finance/vat-codes` (7), Modul und Schemas, die Modelle `VatCode`,
  `VatCodeAudit` samt Vorgabeliste, der Eintrag im Rollenvertrag, zwei Zeilen der
  Pagination-Baseline.
- Verloren: zehn Vorgabezeilen (`DE_19` …) im Prüfstand; die Entwicklungsdatenbank hatte keine.
- Steuerschlüssel kommen damit ausschließlich aus `domain_erp.tax_keys`.

Beide Datenbanken sind migriert.

## Teil 2: Buchen durch Agenten nur nach menschlicher Freigabe

Ablauf:

| Schritt | Wer | Womit | Wirkung |
|---|---|---|---|
| 1 | Agent | `sales.gutschrift.speichern` | Entwurf |
| 2 | Agent | `sales.gutschrift.propose` | Buchungsvorschlag „wartet auf Prüfung"; **bucht nicht** |
| 3 | Mensch | Maske `sales/gutschrift`: Vorschlag „Prüfen" öffnet die Gutschrift, dann „Vorschlag freigeben" oder „Vorschlag ablehnen" | Freigabe oder Ablehnung; **bucht nicht** |
| 4 | Agent | `sales.gutschrift.buchen` mit der Vorschlagsnummer | Buchung, genau einmal |

Regeln, jeweils getestet:

- **Kein Vorschlag für Unbuchbares:** Lässt sich die Gutschrift nicht buchen (fehlender
  Steuerschlüssel, Widerspruch, fehlendes Konto), bekommt der Agent den Prüfgrund statt eines
  Vorschlags.
- **Ohne Freigabe keine Buchung:** `sales.gutschrift.buchen` verlangt `approval_status = approved`.
- **Vier Augen:** Wer vorgeschlagen hat, gibt nicht frei.
- **Wer freigibt, steht in der geprüften Anmeldung** – nicht in einem Kopf und nicht in einem Feld der
  Anfrage. Verlangt wird das Recht, selbst zu buchen (`beleg_write`).
- **Gebucht wird, was freigegeben wurde:** Hat sich der Bruttobetrag seit dem Vorschlag geändert,
  wird nicht freigegeben bzw. nicht gebucht; es braucht einen neuen Vorschlag.
- **Ablehnung braucht einen Grund** und sperrt die Buchung aus diesem Vorschlag.
- **Genau einmal:** Wiederholung desselben Auftrags liefert dieselbe Antwort; ein zweiter Auftrag
  zum selben Vorschlag wird abgelehnt.
- **Ein offener Vorschlag je Gutschrift.**
- Vorschlag, Freigabe, Ablehnung und Buchung schreiben je einen Audit-Eintrag; die Buchung nennt,
  wer freigegeben hat.

Die Maskenaktionen „Buchen", „Vorschlag freigeben" und „Vorschlag ablehnen" sind
`forbiddenForAgents`. Für Freigabe und Ablehnung gibt es **kein** MCP-Werkzeug.

Lieferung im Einzelnen: Wege `GET /sales/credit-notes/buchungsvorschlaege`,
`POST …/buchungsvorschlaege/{id}/actions/freigeben` und `…/ablehnen` (über
`run_delegated_mask_action`); MCP-Werkzeuge `sales.gutschrift.propose` und `sales.gutschrift.buchen`;
ScreenDefinition um die Tabelle „Buchungsvorschläge von Agenten" und zwei Aktionen ergänzt; Seite
(Hülle um den Mask Builder) mit Prüfen, Freigeben (Rückfrage mit den Beträgen) und Ablehnen
(Grund-Dialog). Nachgezogen: Aktionskatalog, MCP-Aktionskarte, Werkzeugreferenz, Agent-Handbuch,
OpenAPI, Architektur-Index; Zählwerte der MCP-Ratschen (Werkzeuge 57 → 59, `mapped` 42 → 43,
`open_high` 2 → 3).

### Auslegungen (einfachste tragfähige – bitte widersprechen, wenn falsch)

- **Freigeben darf, wer selbst buchen darf.** Eine eigene Freigaberolle gibt es nicht.
- **Nach der Freigabe bucht der Agent**, nicht die Freigabe selbst – so ist das Muster bei der
  Eingangsrechnung, und so bleibt sichtbar, wer was getan hat.
- **Verglichen wird der Bruttobetrag**, nicht jede einzelne Position.

## Befund am vorhandenen Freigabe-Muster (nicht behoben, an Codex)

Die allgemeine Freigabe-Stelle `POST /operator-agent/proposals/{id}/approve`
(`app/api/v1/endpoints/operator_agent.py`, `operator_agent_service.py`,
`agent_proposal_repository.py`) trägt die MCP-Vorschläge nicht:

1. **Die Rollen kommen aus dem Kopf `X-VALEO-Roles` der Anfrage** und der Name des Freigebenden
   aus dem Rumpf. Wer den Weg erreicht, kann sich das Recht `agent:approve` selbst zuschreiben.
2. **Die Vorschlagsart `ap_invoice_freigabe` kennt die Stelle nicht** (`AgentActionType`): Ein
   solcher Vorschlag lässt sich dort nicht laden; die Liste bricht ab, sobald einer existiert.
3. **Beim Freigeben wird der Schnappschuss neu geschrieben** und verliert `invoice_id`. Danach
   fände `finance.ap_invoice.freigeben` die Rechnung nicht mehr.

Folge: Für `finance.ap_invoice.propose` und `sales.invoice.propose` gibt es heute keinen
funktionierenden, vertrauenswürdigen Weg, auf dem ein Mensch freigibt; die Tests dieser Werkzeuge
setzen den Status `approved` direkt in die Tabelle. Die Gutschrift benutzt diese Stelle deshalb
**nicht**, sondern eigene, an der geprüften Anmeldung hängende Wege. Die drei Punkte habe ich am
Code gelesen, nicht durch einen Aufruf nachgestellt.

## Von mir verursacht, von Codex behoben

- **Die Pagination-Ratsche ist rot** (`scripts/check_pagination.py`, Exit 1) seit
  `KONTO-SPERRE-20261012` vom Morgen: Die Vorprüfung der Kontosperre in `journal_entries.py` liest
  mit `.all()`. Codex hat das unter `JOURNAL-BLOCK-SUMMARY-20261012` behoben; die Ratsche ist wieder grün.

## Nachweis

- `tests/test_gutschrift_umsatzsteuer.py` – 43 bestanden gegen `valeo_probe`, darunter acht Fälle
  zur Kette Vorschlag → Freigabe → Buchung.
- Mit Plattform- und Finanznachbarn zusammen 2163 bestanden (nach dem Abgleich mit Codex' Identitäts-Commits).
- Maske: `credit-note-editor.test.tsx` – 7 bestanden; `tsc` ohne Fehler, ESLint sauber.
- `check_baseline_integrity.py` und Kommando-Weg-Inventar (0 Lücken): und `check_pagination.py`: in Ordnung.

## Nicht geprüft

- Die Maske im Browser (kein Provider-Konto).
- Die Kette mit einem echten Agenten über den MCP-Server; getestet ist der Werkzeugaufruf an der
  HTTP-Grenze mit eingesetzter Agentenidentität.

## Offen

- Eine **Benachrichtigung** an die Buchhaltung, dass ein Vorschlag wartet, gibt es nicht; er steht in
  der Tabelle der Maske.
- Vorschläge **verfallen nicht** (kein Ablaufdatum).
- Die übrigen Masken mit Prozent-Freitext und die Maske „Steuerschlüssel" (siehe Vorgänger).
