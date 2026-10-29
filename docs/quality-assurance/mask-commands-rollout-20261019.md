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

## Schritt 5: Frontend-Kommandos der Erfassungsmasken (40 ohne MCP/CLI -> 0)

Die Capture-Masken verdrahten ihre Aktionen in der Seite (`command`). 40 davon waren fuer MCP unklassifiziert und
ohne CLI. Jetzt, in Backend-SD und Frontend-Kopie `capture-screens.ts` gleich:

- **18 Mutationen** mit `inputFlow` auf den Sendeweg, den die Seite tatsaechlich ruft (`forbiddenForAgents`):
  Postfach entfernen, Fuhrpark-Dokument/-Rechnung/-Terminart loeschen, Drucker einrichten, Unfallanzeige,
  Tour stornieren, Versandprofil/Lieferavis anlegen und Profil loeschen, Einwilligung erteilen/widerrufen,
  Bewerbung/Onboarding/Qualifikation/Schulung loeschen.
- **22 Oberflaechenaktionen** mit `localEffect`: Navigation, Formular laden/Position (`edit_mode`), Druck,
  Fracht-Probe, Lieferschein aufloesen, Hinweise, Gutschrift laden/pruefen (`view`), Fahrerliste exportieren.

Inventar: `aktionen_nicht_deklariert`, `aktionen_ohne_mcp_klassifikation`, `aktionen_ohne_cli` alle 0;
CLI-Register 220 Aktionen. 137 betroffene Suiten 2232 gruen; Vitest 23 Dateien und Spiegeltest der Postfaecher
gruen; `tsc` ohne Fehler.

## Schritt 6: Studio-Katalog vollstaendig bedienbar (3 -> 0)

- `stornieren` versprach `/sales/orders/{id}/actions/stornieren`, den Weg gab es nicht. Jetzt derselbe
  Zustandswechsel wie `/cancel` mit Verkaufsrolle, Begruendung, Trockenlauf, Wiederholungsschutz (Agenten gesperrt).
- Das Inventar wertet eine Katalogaktion ohne eigene MCP-Zuordnung nach derselben Regel wie
  `mask.action.execute` (generisch ausfuehrbar oder bewusst menschlich).

### Sicherheitsbefund und Korrektur

**Mahnen war fuer Agenten offen.** Die MCP-Karte entschied "Mahnlauf-Write bewusst nicht" (nur Status lesen),
die Maskenaktion `finance/ar-open-item:mahnen` sperrte Agenten aber nicht; das generische `mask.action.execute`
haette Mahnungen erzeugt. Jetzt `forbiddenForAgents` an Maske und Studio-Katalog; der Studio-Vorschlag traegt die
Sperre in den Agentenvertrag. Neuer Vertrag `test_kartenentscheidung_ohne_agenten_write_gilt_auch_generisch`:
Jede Kartenentscheidung ohne Agenten-Write muss die Maske sperren.

### Nachweis

`tests/test_sales_order_storno_command.py` (2) gegen `valeo_probe`; Auftrags-, Studio-, MCP-, Offene-Posten-,
Katalog- und SD-Suiten 882 gruen; Vitest Mahnlauf/Katalog 52 gruen. Ratsche: alle Aktions- und Kataloglisten 0.

## Schritt 7: keine Identitaet aus Client-Kopfzeilen (systemweit)

Nach den Masken des Rollouts lasen noch 21 Stellen `X-User-ID`, `X-User-Email` oder Rollen aus Kopfzeilen:
Urheber-Helfer in elf Routern (Chargen-Freigabe, DSGVO, Tagespreise, FiBu-Konnektoren, Auskunftsersuchen,
Berichtskatalog, Kalender, Qualitaetsprotokolle, Abfrage-Center, Lieferschein, Sanktionspruefung, Gutschrift,
Tourenanlage, Mailkonto) sowie die zentralen `get_user_id_from_request`/`get_user_email_from_request`,
`fibu_audit._user_from_request` (Kopf vor Token!) und die Audit-Middleware. Bei den UX-Overlays waehlte der Kopf,
wessen Ansichtseinstellungen gelesen und ueberschrieben wurden.

- `app/core/akteur.py`: `akteur_aus_request` / `gepruefter_akteur_aus_request` lesen die Claims, die
  `require_bearer_token` geprueft ablegt; `bekannter_nutzer` fuer Spalten mit Fremdschluessel auf
  `domain_shared.users` im frischen Schema (Attestierung des Lieferschein-Nachdrucks): gepruefte Kennung, wenn
  bekannt, sonst `system` wie bisher.
- FiBu- und DSGVO-Audit schreiben die gepruefte Kennung (im frischen Schema ohne Fremdschluessel; die
  Entwicklungsdatenbank hat dort Drift).
- Vertrag `tests/test_keine_client_identitaet.py`: Kein Code unter `app/` liest diese Kopfzeilen.
- Testgrenze `testgrenze.setze_identitaet` fuer Mini-Apps statt `X-User-ID`; betroffene Tests pruefen jetzt,
  dass ein gefaelschter Kopf nichts bewirkt.

Nachweis: 98 + 43 Suiten der beruehrten Wege, FiBu und Audit 2076 gruen gegen `valeo_probe`.

### Offen (eigene Slices)

- **STAMMDATEN-BEARBEITEN:** elf native Objektmasken ohne Aenderungsbefehl (Schritt 4).
- **Rollen der Auftragswege:** `sales_orders` (anlegen, bestaetigen, abschliessen, `/cancel`) prueft keine Rolle;
  der neue Storno-Kommandoweg schon. Ein Rollen-Inventar aller Schreibwege ohne Rollenpruefung steht aus.
