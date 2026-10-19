# Maskenaktionen als Kommando-Weg (MASK-COMMANDS-ROLLOUT-20261019)

Ziel: jede Maskenfunktion per Maske, CLI und MCP ueber denselben Fachweg. Maskenweise, ein Commit je Schritt.

## Schritt 1: Belegkontrolle (4 Masken)

`auswertungen/beleg-kontrolle` und die gespeicherten L3-Sichten `auswertungen/auftrags-kontrolle`,
`auswertungen/lieferschein-kontrolle`, `abrechnung/eb-lieferschein-kontrolle` (gleiche Zeilenaktionen).

- Neuer Kommando-Endpunkt `POST /api/v1/document-control/exceptions/{entity_id}/actions/{assign_me|start_work|resolve|waive}`
  ueber `run_delegated_mask_action`: Begruendung Pflicht, Trockenlauf prueft Fall, Mandant und Statusuebergang
  gegen die Datenbank, Wiederholung mit demselben Schluessel wirkt einmal. Delegiert an
  `DocumentControlService.assign`/`transition`.
- ScreenDefinition: die vier Aktionen tragen `commandEndpoint`; `waive` zusaetzlich `humanApprovalRequired`
  (Agenten bleiben gesperrt); `open_source` ist `localEffect: navigation`.
- Seite `DocumentControlScopePage` ruft nur noch den Kommando-Weg, wertet `success=false` als Fehler und
  sperrt Doppelausfuehrung je Fall und Aktion. `beleg-kontrolle.tsx` nutzt dieselbe Seite statt einer Kopie.

### Sicherheitsbefund und Korrektur

Die bestehenden Wege `/exceptions`, `/project`, `/assign`, `/transition` nahmen den Audit-Urheber aus dem
Client-Header `X-User-ID` (sonst `document-control-operator`); die Seite setzte als Zustaendigen die Zeichenkette
`current-user`. Jeder Schreibberechtigte konnte so Audit-Eintraege unter fremdem Namen erzeugen. Urheber und
Zustaendiger kommen jetzt aus dem geprueften Token; ohne `sub` antwortet der Weg 403.

## Nachweis

- `tests/test_document_control_mask_commands.py` (8, gegen `valeo_probe`): Bearbeiter aus Token trotz
  gefaelschtem Kopf, Trockenlauf schreibt nichts, Wiederholung wirkt einmal, abgeschlossener Fall kein Erfolg,
  Begruendung Pflicht, fremder Mandant findet den Fall nicht, unbekannte Aktion 422, alle vier Masken zeigen
  auf den Kommando-Weg.
- Zusammen mit Projektion und Rollenvertrag 711 gruen; angrenzende MCP-/CLI-/Katalog-/Inventarsuiten 185 gruen.
- Vitest `beleg-kontrolle.test.tsx` 3 gruen (Kommando-Weg, Ablehnung kein Erfolg, keine Doppelausfuehrung);
  ESLint und volle `tsc` ohne Befund in den Dateien.
- Neu erzeugt: OpenAPI, Architekturindex, CLI-Register (153 Aktionen, vorher 137), Inventar und Ratsche
  (`aktionen_nicht_deklariert` 119 -> 99). Gates Kommando-Inventar, MCP-REST-Bindungen, Architektur-Drift gruen.

## Schritt 2: Rechnungsstapel, Produktionsleitstand, Fremdware, Inventur-Nebenlaeufe

Kommando-Endpunkte (alle ueber `app/services/mask_commands.statusaktion` bzw. `run_delegated_mask_action`):

- `POST /billing-batches/{id}/actions/{validate|release|execute}`, `POST /billing-batches/lines/{id}/actions/retry`
- `POST /production-control/operations/{id}/actions/{release|start|complete|mark_rework}`
- `POST /foreign-goods/{id}/actions/{transfer|complete}` (Ziellager bzw. Restmenge im Auftrag)
- `POST /inventory/auxiliary/batches/{id}/actions/{review|approve|apply}`,
  `POST /inventory/auxiliary/actions/{create_count_sheet|create_control|create_valuation}` (Inventur im Auftrag)

Freigeben/Ausfuehren eines Rechnungsstapels und Freigeben/Anwenden eines Inventur-Nebenlaufs sind
`humanApprovalRequired` (MCP sperrt Agenten). Reine Oberflaechenaktionen tragen `localEffect` (`navigation`,
`print`); der Typ kennt jetzt zusaetzlich `download`, `edit_mode`, `refresh`, `view`.

Gemeinsame Bausteine: `app/core/akteur.py` (Urheber aus dem Token, Rolle je Aktion),
`app/auth/betrieb_roles.py` (Lager/Produktion), `useMaskRowCommands` (Seite: Umschlag, `success=false` ist
Fehler, Schutz je Zeile und Aktion), `tests/maskenkommando_pruefstand.py` (Pruefstand mit umschaltbarer
Identitaet). Der MCP-Kartengenerator kennt `mask.action.execute` (`mapped_generic`).

### Sicherheitsbefunde und Korrektur

1. **Vier-Augen-Prinzip umgehbar.** Rechnungsstapel (Freigeber != Ersteller) und Inventurfreigabe
   (Pruefer != Ersteller) verglichen Werte aus `X-User-ID`. Mit zwei Kopfzeilen gab man den eigenen Stapel
   bzw. die eigene Bewertung selbst frei. Jetzt Kennungen aus dem Token (Test mit zwei Personen).
2. **Schreibwege ohne Rolle.** Produktionsleitstand (registrieren, synchronisieren, weiterschalten), Fremdware
   (umlagern, abschliessen) und Inventur-Nebenlaeufe (anlegen, weiterschalten) prueften keine Rolle; jede
   angemeldete Person des Mandanten konnte schreiben. Jetzt Bearbeitungsrolle des Bereichs, Freigeben/Anwenden
   der Inventur Lagerleitung.

### Nachweis

- Gegen `valeo_probe`: `test_billing_batch_mask_commands` (6), `test_production_control_mask_commands` (3),
  `test_lager_mask_commands` (4); mit Bestands-, MCP-, CLI-, Katalog-, Inventar- und Rollenvertragssuiten
  zusammen 1997 gruen.
- Vitest der fuenf Seiten 15 gruen; volle `tsc` und ESLint ohne Befund in den Dateien.
- Inventar: `aktionen_nicht_deklariert` 99 -> 75, CLI-Register 169 Aktionen.

## Schritt 3: Tankanlagen-Eingang, Altsystem-Adapter, MDE-Inbox, Dokumentenruecklauf, Pruefkorb

- `POST /tank-adapter/intake/{id}/actions/{validate|process|retry}` (retry optional `corrected_payload`)
- `POST /legacy-interface-adapters/batches/{id}/actions/{stage|reconcile|approve}` (approve menschlich)
- `POST /mobile/sync-queue/{id}/actions/retry_event`
- `POST /document-returns/{id}/actions/{mark_sent|mark_received|verify_return}` — bewusst nicht unter
  `/docflow`, dort gelten die versionierten Beleg-Adapter (MCP und CLI sperren `/docflow`-Wege ohne Adapter)
- `POST /kontrolle/befunde/{id}/actions/pruefen` (`note` = Bewertung und Begruendung; menschlich)

Vorschau des Ruecklaufnachweises ist `localEffect: view` (lesend).

### Sicherheitsbefunde und Korrektur

Tankanlagen-Eingang (pruefen, verarbeiten, wiederholen), MDE (wiederholen, Queue verarbeiten) und
Dokumentenruecklauf (anlegen, Statuswechsel) hatten keine Rollenpruefung. Jetzt: Tankanlage Lager oder Verkauf
(`tank_write`), MDE Lager, Ruecklauf Belegbearbeitung (`beleg_write`). Alle fuenf Router nahmen den Urheber aus
`X-User-ID`; die Annahme der Tankdaten nimmt jetzt die Kennung des angemeldeten (technischen) Zugangs.

### Nachweis

- `tests/test_inbox_mask_commands.py` (5, `valeo_probe`): Rolle, Urheber, Zustand, Trockenlauf, fremder
  Mandant, Funktionstrennung im Pruefkorb. Mit Bestands-, MCP-, CLI-, Inventar- und Rollensuiten 2751 gruen.
- Vitest der Seiten (finance, schnittstelle, tankstelle, docflow) gruen; `tsc` und ESLint ohne Befund.
- Inventar: `aktionen_nicht_deklariert` 75 -> 60; CLI-Register 180 Aktionen.

## Schritt 4: alle uebrigen Maskenaktionen deklariert (`aktionen_nicht_deklariert` 60 -> 0)

- **Reine Oberflaechenwirkung** (`localEffect`): Navigation, Druck, lesender Export (`download`), Ansicht/Vorschau
  und Lesepruefung (`view`: Berichtslauf, Drilldown, Hash-Kettenpruefung, Versionsvergleich), Neu laden.
- **Eingabefluesse** (`inputFlow` mit echtem Sendeweg, `forbiddenForAgents`): Futter-/Rationsformulare (Betrieb,
  Vorlage anlegen/anwenden, Tiergruppe anlegen/bearbeiten, Tageswerte, Analyse erfassen), Abfrage anlegen,
  Bonus-Korrektur, Chargenkennzeichen, Mailentwurf/-zuordnung, Strecke anlegen/loeschen, Frachttarif stornieren,
  Frachttabelle loeschen, letzte Dokumente entfernen. Vorlage anwenden hat dafuer einen Sendeweg ohne fremden
  Pfadparameter (`/ration-templates/actions/apply_template`, derselbe Fachweg).
- **Kommandos**: Futteranalyse plausibilisieren (`.../actions/validate`), Mail senden (`.../actions/queue`,
  menschlich) und Anhang uebernehmen (`.../attachments/{id}/actions/transfer`).
- **Bearbeiten**: Duenger, Saatgut, Lieferant, Bestellung und Lagerartikel fuehren zur bestehenden Pflegemaske mit
  derselben Kennung; Einzelfuttermittel bearbeitet in der Seite (`edit_mode`). In elf nativen Objektmasken
  (Auftrag, Kontrakt, Chance, Lead, Anfrage, AB, Bankkonto, Debitor, Kreditor, Mischfuttermittel, Reklamation) tat
  der Knopf nichts: kein Aenderungsbefehl, keine eindeutige Pflegemaske (teils doppelt vergebene Routen). Er ist
  entfernt; ein echter Bearbeitungsweg ist Folge-Slice (siehe Workboard).

### CLI: Eingabefluesse

Die CLI fuehrt einen Eingabefluss mit Sendeweg fuer Menschen aus: Formularfelder ohne Aktionsumschlag (`--grund`
wird `reason`), nur `execute`, fuer Agenten gesperrt. Die Paritaetsregel zu MCP bleibt (MCP sperrt Eingabefluesse).
CLI-Register 204 Aktionen; Grund `eingabe_in_maske` kommt nur noch ohne Sendeweg vor. MCP-Karte fuehrt
Eingabefluesse als `blocked_human_only`.

### Sicherheitsbefund und Korrektur

**Mail-Arbeitsplatz:** Welche Rollenpostfaecher jemand las, beschrieb und versandte, entschied der Client-Header
`X-Roles`. Wer ihn setzte, hatte jedes Rollenpostfach des Mandanten. Jetzt Rollen aus dem Token (Test:
`X-Roles: FINANCE_ADMIN` oeffnet nichts), Urheber aus dem Token.

### Nachweis

- `tests/test_mail_workspace_mask_commands.py` (3) gegen `valeo_probe`; CLI-Vertrag fuer Eingabefluesse.
- 152 betroffene Suiten (ScreenDefinitions, Masken, MCP, CLI, Futter, Studio, Katalog, Registry): 1792 gruen,
  ohne `test_mcp_client_lifecycle` (bekannter Windows-Fall).
- Vitest 93 + 61 Dateien gruen (u. a. Sync der Frontend-Kopie `capture-screens.ts`); volle `tsc` ohne Fehler.
- Gates: Ratsche (nicht deklariert 0), Kommando-Inventar (0 bekannte Luecken), Architektur-Drift gruen.
