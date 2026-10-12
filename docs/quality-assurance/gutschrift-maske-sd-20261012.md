# Gutschrift-Maske als ScreenDefinition, mit MCP- und CI-Schnittstellen

Stand: 2026-10-12 · Slice `GUTSCHRIFT-MASKE-SD-20261012` · Folge aus
[Steuerschlüssel: eine Quelle](steuerschluessel-einheit-20261012.md)

## Auftrag

„Maske an Steuerschlüssel(-Tabelle) ändern, systemweit vereinheitlichen." und danach, als Korrektur
eines ersten Versuchs: „no handmade masks, maskbuilder und screendefinitions nutzen. mcp und ci
schnittstellen".

## Was verworfen wurde

Ein erster Entwurf baute die Gutschrift-Maske als frei geschriebene React-Seite mit eigener Tabelle,
eigener Steuerberechnung im Browser und eigener Auswahlkomponente. Er wurde **nicht committet**.
Übrig geblieben ist davon nichts.

## Ausgangslage der alten Maske

`pages/sales/credit-note-editor.tsx` war eine Attrappe: Die Positionstabelle wurde als Textfeld
gezeichnet, die Feldnamen passten nicht zur Schnittstelle (jedes Speichern 422), sie lud und
änderte über Wege, die es nicht gibt, und Vorschau, Druck, Freigabe und Versand riefen ebenfalls ins
Leere. Je Position gab es ein Prozentfeld „Steuersatz".

## Lieferung

**ScreenDefinition `sales/gutschrift`** (`app/core/screen_definitions_capture.py`, registriert, nicht
temporär, Readiness bestanden, Beratungswert 1,0, keine Governance-Fehler):

- Kopf: Nummer, Kunde, Rechnungsbezug, Art (Rechnungskorrektur / § 14 UStG), Grund, Notizen.
- Positionserfassung mit **Steuerschlüssel als Auswahl** aus `domain_erp.tax_keys`
  (Datenquelle `steuerschluessel`). Kein Prozentfeld, kein Vorgabewert.
- Tabellen: Positionen, Steuerausweis je Steuerschlüssel, Gutschriften des Mandanten.
- Prozess: Erfassen → Entwurf → Gebucht; Stand, nächster Schritt und Prüfgrund im Prozessbereich.

**Die Maske rechnet nicht.** Netto, Umsatzsteuer und Brutto kommen von
`POST /sales/credit-notes/steuer-vorschau` – dieselbe Stelle (`steuergruppen`) wie die Buchung.

**Kommando-Wege** über `run_delegated_mask_action` (Trockenlauf, Audit, Outbox, Idempotenz):

| Aktion | Weg | Verhalten |
|---|---|---|
| Als Entwurf speichern | `POST /sales/credit-notes/actions/speichern` | Trockenlauf schreibt nichts; doppelte Nummer, fehlende Positionen und ein Widerspruch Schlüssel/Satz werden abgelehnt |
| Buchen | `POST /sales/credit-notes/{id}/actions/buchen` | Trockenlauf nennt den Prüfgrund; gebucht wird einmal; Kontosperre als Satz |

Dazu `GET /sales/credit-notes/{id}` (mit Positionen). Die Buchungslogik ist in `_buchungsplan`
(liest, prüft) und `_buche` (schreibt) getrennt; der bisherige Weg `…/post` benutzt dieselben beiden.

**Rollen:** Die Gutschrift-Wege hatten keine Rollenprüfung. Lesen verlangt jetzt die Belegleserolle,
anlegen, löschen und buchen die Belegbearbeitung (`beleg_read` / `beleg_write`).

**Seite:** `credit-note-editor.tsx` ist eine dünne Hülle um `UniversalMaskRenderer` – die Seite
speichert, der Builder zeichnet (Vorbild `pages/admin/postfaecher.tsx`).

**MCP:**

- Werkzeug `sales.gutschrift.speichern` (`config/mcp_erp_tools.yaml`, Ausführung in
  `mcp_execution_service.py`): legt den Entwurf an; Trockenlauf liefert Netto/Steuer/Brutto oder
  den Prüfgrund; `execute` verlangt einen Idempotenzschlüssel; Mandant nur aus dem Token.
- **Buchen ist für Agenten gesperrt** (`forbiddenForAgents`, `humanApprovalRequired`). Ein Agent legt
  den Entwurf an, gebucht wird durch einen Menschen. In der Aktionskarte steht die Aktion als
  `open_high` ohne Werkzeug.

**CI-Schnittstellen nachgezogen:** Aktionskatalog (`screen_mask_actions.json`), MCP-Aktionskarte
(`mcp_mask_action_map.yaml`), Kommando-Weg-Inventar (0 Lücken), MCP-Werkzeugreferenz, Agent-Handbuch
(5 Dateien), OpenAPI. Vier festgeschriebene Zählwerte der MCP-Ratschen sind um die neuen Einträge
erhöht (Werkzeuge 56 → 57, `mapped` 41 → 42, `local_ui` 13 → 14, `open_high` 1 → 2).

### Auslegungen (einfachste tragfähige – bitte widersprechen, wenn falsch)

- **Buchen bleibt beim Menschen.** Für buchungsrelevante Agentenaktionen gibt es im Haus das Muster
  Vorschlag → Freigabe → Ausführung (`finance.ap_invoice.propose` / `…freigeben`). Für die Gutschrift
  ist das nicht gebaut; bis dahin ist die Buchung für Agenten zu.
- **Kunde als Nummernfeld.** Die Erfassungsmasken des Builders haben kein Nachschlagefeld im Einsatz;
  die Kundensuche fehlt hier.
- **Speichern markiert die Ursprungsrechnung nicht** als „gutgeschrieben" (der alte REST-Weg tut das
  schon beim Anlegen des Entwurfs). Eine Rechnung gilt erst mit der Buchung als korrigiert.

## Nachweis

- `tests/test_gutschrift_umsatzsteuer.py` – 35 bestanden gegen `valeo_probe`: ScreenDefinition
  (bereit, kein Prozentfeld, Steuerschlüssel ohne Vorgabe), Steuer-Vorschau, beide Kommando-Wege
  (Trockenlauf, Ausführung, Wiederholung, Prüfgrund, Kontosperre), Rollen, MCP-Werkzeug
  (Trockenlauf, einmaliges Anlegen, Mandantenangabe und fehlendes Recht abgewiesen), Agentensperre.
- Plattform: `test_mcp_mask_action_map`, `test_mcp_local_action_classification`,
  `test_mcp_tool_registry`, `test_mcp_tenant_isolation_all`, `test_mcp_execution`,
  `test_mcp_reference_staged`, `test_mask_screen_definition`, `test_postfaecher` u. a. – zusammen
  305 bestanden.
- Maske: `src/__tests__/pages/sales/credit-note-editor.test.tsx` – 5 bestanden (Auswahl ohne
  Vorsteuerschlüssel und ohne Vorgabe; Server rechnet; ohne Schlüssel „offen" und Prüfgrund;
  Speichern ohne Steuersatz; Buchen fragt nach und zeigt den Prüfgrund). `tsc` ohne Fehler, ESLint
  sauber.

## Nicht geprüft

- **Die Maske im Browser.** Es gibt weiterhin kein Provider-Konto für die Sichtprüfung; geprüft ist
  die gezeichnete Maske im Vitest, nicht am laufenden System.
- Budget- und Leistungsratschen der Masken (`check_mask_bundle_budget`, `…performance_contract`).
- Ob die Registry die ScreenDefinition im laufenden Dienst ausliefert (die Seite nimmt sonst die
  Kopie aus `capture-screens.ts`).

## Offen

- **Übrige Masken mit Prozent-Freitext** (systemweite Vereinheitlichung): Ausgangsrechnung
  (`finance/invoice-form`), Eingangsrechnung (`finance/ap-invoice-form`,
  `einkauf/rechnung-eingang-erfassung`, `einkauf/rechnungseingang` mit fest verdrahteten `VAT_19`),
  Einkaufsgutschriften, Lieferschein-Erfassung, Bestellung, Zinsabrechnung, Artikelstamm, Kasse,
  Ernteannahme. Jede braucht denselben Weg: Steuerschlüssel als Feld der ScreenDefinition und ein
  Backend, das den Schlüssel statt des Satzes annimmt. Noch **nicht** umgestellt.
- **Maske „Steuerschlüssel"** (`finance/steuerschluessel.tsx`) ist handgebaut und zeigt Erlöskonto
  und § 24 noch nicht – als ScreenDefinition neu zu bauen.
- **Bearbeiten eines Entwurfs:** Es gibt nur Anlegen und Buchen; ein gespeicherter Entwurf lässt sich
  öffnen, aber nicht ändern.
- **Vorschlag/Freigabe-Paar** für das Buchen durch Agenten.
- **Kundensuche** in der Maske.
