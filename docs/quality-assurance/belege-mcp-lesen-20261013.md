# BELEG-013: Lesende MCP-Werkzeuge für Belege, Verzeichnis der Belegkommandos

Stand: 2026-10-13 · Slice `BELEG-013` · aus dem
[Masterplan Belegmaske mit Varianten](../design/belegmaske-varianten-masterplan.md), Abschnitt C1 ·
Folge aus [Lesender Belegweg](belege-lesen-20261013.md) · gebunden an den Standard
[MCP-WRITE](../architecture/mcp-write-standard.md)

## Auftrag

Entscheidung des Auftraggebers vom 13.10.2026: eine Fachaktion, mehrere Zugänge; MCP-Werkzeuge für
Belege zuerst nur lesend.

## Geliefert

### Drei lesende Werkzeuge (Scope `belege:read`)

| Werkzeug | Zweck |
|---|---|
| `beleg.arten` | Belegarten des Belegvertrags und das Verzeichnis der Belegkommandos |
| `beleg.suchen` | Belege nach Belegart, Status, Teil der Belegnummer, Partnernummer; höchstens 50 |
| `beleg.lesen` | Ein Beleg in der Form des Belegvertrags |

- **Derselbe Beleg wie die Maske:** `beleg.lesen` und `GET /api/v1/belege/{belegart}/{beleg_id}`
  benutzen denselben Adapter; ein Test vergleicht beide Antworten für alle 17 Referenzbelege.
- **Mandant und Akteur aus der geprüften Anmeldung** (`execute_mcp_tool`); ein Mandant in den
  Parametern wird abgelehnt.
- **Sie schreiben nichts**, in keinem Modus; `propose` wird abgelehnt.
- **Ohne Preise in der Variante kein Betrag** — auch nicht in der Trefferliste der Suche.

### Verzeichnis der Belegkommandos (`app/core/belegkommandos.py`)

Zehn Einträge: Name, Adresse, Risikoklasse R0–R4 nach MCP-WRITE, Idempotenz. Freigabe ist ab R3 nötig.

| Kommando | Klasse | Freigabe |
|---|---|---|
| `beleg.lesen` | R0 | — |
| `docflow.create`, `.update`, `.delete_draft` | R1 | — |
| `docflow.convert`, `.record_print`, `.record_export` | R2 | — |
| `docflow.release`, `docflow.post` | R3 | ja |
| `docflow.reverse` | R4 | ja |

- Die Aktionen des Belegvertrags nehmen Kommando und Freigabepflicht aus dem Verzeichnis.
- **Kein schreibendes Belegkommando hat ein MCP-Werkzeug** (MCP-WRITE-014); ein Test hält das fest.
- Das Verzeichnis ist keine zweite Capability-Registry, sondern die Zuarbeit der Belege für Stufe 2 des
  Standards („Bestehende Register vereinheitlichen").

## Nachweis

- `tests/test_mcp_beleg_tools.py`: 16 bestanden gegen `valeo_probe` — jedes Kommando hat seinen Weg;
  **jeder schreibende DocFlow-Weg steht im Verzeichnis** (ein neuer ohne Eintrag macht den Test rot);
  Risikoklassen und Freigabe; Werkzeuge nur lesend registriert; Agent und Maske lesen denselben Beleg;
  Suche mit Filtern; ohne Scope 403, fremder Mandant leer bzw. 404, falsche Belegart 404; sieben
  ungültige Eingaben 422; kein Schreibzugriff.
- Vorhandene MCP-Tests (Ausführung, Mandantentrennung, Referenz, Aktionskarte): 198 bestanden.
- `tests/test_belege_lesen.py` 10, `tests/test_belegvertrag.py` 27, `tests/test_mcp_tool_registry.py`
  (jetzt 62 Werkzeuge) bestanden.
- MCP-Referenz, Aktionskarte, Agenten-Handbuch, Architektur-Index (Endpunkt `belege` zugeordnet)
  nachgezogen.

## Auslegungen (meine, nicht entschieden)

- **Eigener Scope `belege:read`** statt je eines Scopes für Verkauf und Einkauf: Die Registry kennt
  einen Scope je Werkzeug, und Belege beider Richtungen mit Preisen zu lesen soll eine ausdrückliche
  Erlaubnis sein. **Noch trägt kein Token diesen Scope** — die Werkzeuge sind bis zur Vergabe durch die
  Identität (Codex) für niemanden aufrufbar.
- **Risikoklassen:** Freigeben R3 (vergibt die endgültige Belegnummer, der Beleg ist ausgestellt),
  Buchen R3, Stornieren R4, Umwandeln R2 (der Folgebeleg entsteht offen, nicht ausgestellt). Die
  Einstufung ist an Codex zur Prüfung in Stufe 2 gemeldet.

## Grenzen

- **Kein Recht am einzelnen Beleg:** Wer den Scope hat, liest alle Belege des Mandanten mit Preisen
  (BELEG-012).
- Recht, Schemaversion und Freischaltzustand je Kommando fehlen im Verzeichnis (Stufen 1 und 2 von
  MCP-WRITE).
- Die Freigabepflicht ist eine Angabe; durchgesetzt wird sie noch nicht — über REST lassen sich Belege
  weiterhin ohne Freigabe buchen und stornieren.
- Kein Kommandozeilenzugang.
- Nicht über den MCP-Transport selbst geprüft, sondern an `execute_mcp_tool`.
