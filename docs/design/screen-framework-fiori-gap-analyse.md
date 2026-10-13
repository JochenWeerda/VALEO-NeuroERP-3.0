# VALEO Screen Framework — Bestandsprüfung gegen SAP Fiori elements, DocFlow und Sichtprüfung

Stand: 2026-10-13 · Auftrag des Auftraggebers vom 13.10.2026 („VALEO Screen Framework –
SAP-Fiori-Gap-Analyse"; „Der nächste technische Schritt ist die Bestandsprüfung von DocFlow und der
vorhandenen Authentifizierungs- und Staging-Infrastruktur, nicht der sofortige Neubau weiterer Masken") ·
Gehört zu `belegmaske-varianten-masterplan.md`.

Geprüft am Code und an den Schemata beider Datenbanken, nur lesend. Nichts wurde geändert.
SAP Fiori dient als Architektur- und Designreferenz; SAPUI5 wird nicht übernommen.

Legende: **vorhanden** · **teilweise** · **fehlt** · **redundant** (mehrfach vorhanden).

## 1. Screen Framework gegen die Fiori-Konzepte

Bestand in Zahlen: 104 ScreenDefinitions in der Registry (`app/core/screen_definitions*.py`), alle
`adapter.type = native`, `schemaVersion: 1`. Der Mask Builder (`components/mask-builder`) hat 36
Renderer, 18 Laufzeitbausteine, einen Plan-Compiler mit Cache und eine Governance-Schicht.
Von 698 Seitendateien nutzen 52 die ScreenDefinition-Laufzeit (`UniversalNativeDetailPage` 27,
`UniversalMaskRenderer` 25), 101 die ältere Konfigurationsschicht (`ObjectPage` 37, `Wizard` 29,
`ListReport` 23, `Worklist` 12), eine den `FormBuilder`; 516 Dateien nutzen keines davon (darunter
Unterseiten und Hüllen, nicht nur Masken).

| Fiori-Konzept | Prio | Stand | Beleg | Lücke |
|---|---|---|---|---|
| Annotation-driven UI (Fachmetadaten) | P0 | **teilweise** | ScreenDefinition beschreibt Felder, Tabellen, Aktionen, Rechte, Agentenvertrag deklarativ; Server liefert sie aus (`/masks/{id}/screen-definition`) | Metadaten hängen an der Maske, nicht am Fachobjekt: dasselbe Feld heißt je Maske anders (`order_number`, `invoice_number`, `beleg_nr`). Es gibt kein Feldwörterbuch je Belegart |
| Floorplans | P0 | **vorhanden** | `floorplans.ts`: Arbeitsliste, Objektseite, Transaktion, Cockpit, Assistent, Analytische Liste; je Zweck Regeln (Spalten, Sprungmarken). In Benutzung: 57 Arbeitslisten, 15 Objektseiten, 8 Cockpits, 1 Transaktion | 23 Definitionen ohne Floorplan-Angabe (18 Detail, 5 Cockpit); „Analytische Liste" definiert, von keiner Definition benutzt |
| Building Blocks | P0 | **vorhanden** | Renderer für Feld, Formular, Tabelle, Reiter, Abschnittsseite, Summen, Aktionsleiste, Prozessband, Belegkette, Meldungen, Zeilendetail, Kacheln, Kalender, Quellvorschlag | Kein Positionsbaustein mit Erfassung in der Zeile: Die Gutschrift erfasst Positionen über Kopf-Felder plus „Position übernehmen" |
| Draft Management | P0 | **fehlt** | Nur `UnsavedChangesGuard` (Warnung beim Verlassen). `studio_draft_store` meint Entwürfe von *Masken*definitionen, nicht von Belegen | Kein serverseitiger Belegentwurf, keine Wiederaufnahme nach Sitzungsablauf, kein „in Bearbeitung durch", keine Konflikterkennung außer `expected_version` in DocFlow |
| Edit Flow / Actions | P0 | **vorhanden** | Kommando-Wege mit Trockenlauf, Idempotenz, Audit, Outbox (`run_delegated_mask_action`); Aktionskatalog; Gefahrstufen, Bestätigung, Agentensperre; `ActionRuntime` | Statusübergänge stehen je Maske in der Seite, nicht in der Definition (`workflow.phases` beschreibt nur die Anzeige) |
| Value Help | P1 | **teilweise / redundant** | `LookupField` mit Suche, Mindestlänge, Cache, Bindung über Datenquelle | Keine einzige ScreenDefinition benutzt den Typ `lookup`. Kunden- und Artikelsuche sind je Maske eigen gebaut (`CustomerCombobox`, Suchfelder im Handbau, `FormBuilder`-Lookup). Kein einheitlicher Suchweg mit `{value, label}` |
| Side Effects | P1 | **fehlt** | Einzelfall: Die Gutschrift fragt eine Steuer-Vorschau am Server ab — in der Seite, nicht im Framework | Keine deklarative Angabe „bei Änderung von A berechne B neu am Server" |
| Message Handling | P1 | **teilweise** | `MessagePanelRenderer` (Fehler, Warnung, Hinweis, Sprung zum Feld), Feldfehler im Formularzustand, `validationErrors` der Kommando-Wege | Serverfehler eines Kommando-Wegs landen in den Seiten als Toast; keine einheitliche Abbildung Serverfehler → Feld |
| Variant Management (Nutzeransichten) | P1 | **vorhanden** | Nutzer-Overlays serverseitig (`lib/api/ux-overlays`, `render-plan/overlay.ts`): sichtbare Spalten, Breiten, gespeicherte Tabellenvarianten; harte Liste dessen, was ein Overlay nie ändern darf (Aktionen, Rechte, Felder) | — |
| Belegvarianten (administrativ) | P1 | **fehlt** | — | Die ScreenDefinition kennt keine Variante; jede Belegart ist eine ausgeschriebene Definition |
| Flexible Column Layout | P2 | **vorhanden** | `columnNavigation`: `single`, `listDetail`, `listDetailDetail`; `ColumnLayoutRenderer` | — |
| Analytical List Page | P2 | **teilweise** | Floorplan definiert, Cockpit-Seiten mit Kennzahlen vorhanden | Keine Definition nutzt ihn; Diagramm plus Tabelle als Baustein fehlt |
| Extension Points | P1 | **teilweise** | Adaptertyp `specialized`; Sonderbausteine (Quellvorschlag, Zwilling, Kalender) | Sonderbausteine sind im Kern eingebaut. Es gibt keine dokumentierte Stelle, an der eine Maske einen Fachbaustein einhängt, ohne den Renderer zu ändern |

### Konkurrierende Schemas und Renderlogik (Abnahmekriterium „keine konkurrierenden Maskenschemas")

| # | Was | Wo | Bewertung |
|---|---|---|---|
| K1 | ScreenDefinition (Python-Registry, vom Server ausgeliefert) | `app/core/screen_definitions*.py` | **kanonisch** |
| K2 | Handkopie von 31 ScreenDefinitions in TypeScript | `masks/capture-screens.ts` | **redundant**: dieselbe Definition zweimal, von Hand bzw. Skript abgeglichen; Seiten mit `UniversalMaskRenderer` lesen die Kopie, Detailseiten holen vom Server |
| K3 | `MaskConfig` der älteren Schicht | `ObjectPage`, `ListReport`, `Wizard`, `Worklist`; 101 Seiten | **zweites Schema**; ein Adapter nach ScreenDefinition existiert (`adapters/mask-config-adapter.ts`) |
| K4 | JSON-Schema des `FormBuilder` | `domain-schemas/sales_invoice.schema.json`, eine Seite | **drittes Schema**, entfällt mit der Rechnungsvariante |
| K5 | Weitere Adaptertypen im Schema | `crmMaskJson`, `formSchema`, `l3-mask-adapter.ts` | von keiner Registry-Definition benutzt |

Zwei Fehler im Plan-Cache des Compilers wurden am 13.10.2026 behoben (zur Laufzeit gesetzter
Schreibschutz und neu beschriftete Auswahlen wurden nicht neu gezeichnet) — ein Hinweis, dass
zur Laufzeit veränderte Definitionen bisher kaum vorkamen.

### Serverseitige Durchsetzung (Abnahmekriterium „keine Umgehung von Berechtigungen")

| Punkt | Stand |
|---|---|
| Rollen an den Kommando-Wegen | vorhanden, je Weg als Abhängigkeit; Vertragstests je Modul |
| `permission` einer Aktion in der Definition | wirkt nur in der Oberfläche (Aktion sichtbar oder nicht); maßgeblich ist die Rolle am Weg |
| Feldrechte (z. B. Preise) | **fehlt**: kein Leseweg filtert Felder nach Berechtigung |
| Mandant | aus der Anmeldung — **außer in DocFlow**, das ihn aus einem Anfrageparameter nimmt (siehe 2) |
| Steuerregeln in Definitionen | keine; Steuer kommt aus `tax_keys`, gerechnet wird am Server |

## 2. DocFlow gegen die Bedingungen des Auftraggebers

Bedingung: „Vor der Ablösung muss nachgewiesen sein, dass DocFlow Mengen, Preise, Steuerpositionen,
Teilrechnungen, Gutschriften, Belegreferenzen und revisionssichere Statuswechsel korrekt unterstützt."

| Bedingung | Stand | Beleg |
|---|---|---|
| Mengen, Preise, Rabatt | **vorhanden** | `document_items`; Prüfbedingungen gegen negative Werte und Rabatt außerhalb 0–100 |
| Steuerpositionen | **vorhanden seit 13.10.2026** | `tax_code` je Position, Satz als Abbild, Buchung je Steuerschlüssel; Position ohne Schlüssel wird gespeichert, nicht gebucht |
| Belegreferenzen | **vorhanden** | `document_header_links` (Beleg → Beleg), `document_links` (Position → Position mit `quantity_linked`) |
| **Teilrechnungen, Teillieferungen** | **fehlt** | `convert` gibt je Quelle und Folgeart den schon vorhandenen Folgebeleg zurück (`uq_docflow_header_link_source_relation`): Ein zweiter Teillieferschein aus demselben Auftrag entsteht nicht. Teilmengen werden nur gegen die volle Quellmenge geprüft, nicht gegen das schon Umgewandelte — eine Restmengenrechnung gibt es nicht |
| **Gutschriften** | **teilweise** | Übergang `sales_invoice → sales_credit_memo` und Nummernkreis vorhanden; `post_document` bucht nur `sales_invoice`. Die buchende Gutschrift lebt daneben in `/sales/credit-notes` (eigene Tabellen) |
| **Revisionssichere Statuswechsel** | **fehlt** | Der Status wird im Kopf überschrieben; eine Statushistorie gibt es nicht. Das Protokoll heißt `best_effort_audit`, schreibt ohne Benutzerkennung und verschluckt Fehler |
| Versionierung | teilweise | `version` zählt hoch und dient der Konflikterkennung (`expected_version`); frühere Fassungen werden nicht aufbewahrt |
| Idempotenz, Outbox | vorhanden | je Kommando ein Schlüssel; `create_request_idempotency`, `command_idempotency_keys` |
| Buchungsnachweis | vorhanden | `document_postings` mit Journalbezug, Buchung und Stornobuchung |
| Storno | teilweise | Rechnung: Gegenbuchung über Finance. Die Stornobuchung schreibt sich vor dem Belegstatus fest (kein gemeinsamer Commit) |
| Dokumente, E-Rechnung | vorhanden | `document_artifacts` (Hash, Version, Freigabe), `invoice_xml_store`, GoBD-Export |
| **Einkaufsbelegarten** | **fehlt** | Belegarten und Übergänge nur für Verkauf und Kasse; der Kopf hat `supplier_id` |
| **Mandant** | **Lücke** | Die Wege nehmen `tenant_id` aus der Anfrage, sonst den Vorgabemandanten |
| Führender Speicher | uneinheitlich | Für Auftrag und Lieferschein zieht DocFlow Kopien aus den alten Tabellen nach (`_bootstrap_sales_order`, `_bootstrap_sales_delivery`) |

**Ergebnis:** DocFlow trägt die Struktur (eigener Beleg je Schritt, Bezug je Position, Buchungsnachweis),
erfüllt die Bedingungen aber in vier Punkten noch nicht: Teilmengen über mehrere Folgebelege,
revisionssichere Statushistorie, Gutschrift mit Buchung, Mandant aus der Anmeldung. Dazu fehlen die
Einkaufsbelegarten. Das ist die Arbeit von Phase 0, vor jeder Maske.

Bestehende Einkaufsbelege als Migrationsquelle: `einkauf_rechnungseingaenge` ist in der frischen
Datenbank leer und ohne Mandanten-Spalte, in der gewachsenen nicht vorhanden; der Dokumentspeicher
`documents` der gewachsenen Datenbank enthält eine Eingangsrechnung und eine Bestellung. Ein
Datenverlust durch die Ablösung ist danach nicht zu erwarten; vor Ort zu prüfen bleibt jede
Installation mit echten Daten.

## 3. Anmeldung, Staging und Browserprüfung

Bedingung: echte Sicht- und Interaktionsprüfung über den tatsächlichen OIDC-/PKCE-Ablauf, mit
dediziertem Testbenutzer, isolierter Umgebung, Referenzbelegen, Playwright mit Bildschirmfotos und
manueller Sichtabnahme.

| Baustein | Stand | Beleg |
|---|---|---|
| Identity Provider | **vorhanden** | Keycloak im Compose-Stack, lokal in Betrieb; Realm `valeo-neuro-erp` mit Frontend-Client und PKCE S256 (`config/keycloak/realm-export.json`) |
| Echte Anmeldung im Browser | **vorhanden, am 13.10.2026 nachgewiesen** (Codex) | `docs/quality-assurance/login-variants-20261013.md`: Callback, Sitzungserneuerung, Abmelden repariert und real durchlaufen |
| Staging-Umgebung | **vorhanden als Konfiguration** | `docker-compose.staging.yml`, `docker-compose.staging-infra.yml`, Realm `valeo-staging` (`realm-staging.json`), Workflow `deploy-staging.yml`. Ob sie läuft, ist nicht geprüft |
| Dedizierter Testbenutzer | **fehlt** | Beide Realm-Dateien enthalten keine Benutzer; Benutzer leben nur im laufenden Keycloak |
| Testmandant | teilweise | Lokaler Testmandant mit SKR03, vier Steuerschlüsseln, eigenen Konten, 22 Artikeln mit Steuerschlüssel (68 ohne) |
| Referenzbelege | **fehlt** | In DocFlow der gewachsenen Datenbank liegen drei Belege |
| Playwright | **vorhanden** | Konfigurationen und Hilfen in `playwright-tests/`; SSO-Modus über `VALEO_PLAYWRIGHT_USE_SSO=1` mit Zugangsdaten aus der Umgebung |
| Anmeldung in den Browsertests | **nicht ausreichend für die Abnahme** | Standard ist ein in den Browser gesetztes Token (`playwright-smoke-auth.md`) — genau die Umgehung, die für die Sicherheitsabnahme nicht zählt |
| Visuelle Baselines | **fehlt** | Keine Bildschirmfoto-Vergleiche für Masken |

**Korrektur einer früheren Aussage:** In den Berichten vom 12. und 13.10.2026 steht, eine
Sichtprüfung sei lokal nicht möglich. Das war seit der Identitätsumstellung nur für den alten
Token-Weg richtig. Mit dem laufenden Keycloak ist die echte Anmeldung möglich; es fehlt ein
Testbenutzer, kein Anbieterkonto.

Zugangsdaten gehören nicht ins Repository: Testbenutzer werden im Keycloak angelegt, die Tests lesen
Kennung und Kennwort aus der Umgebung.

## 4. Was daraus für die Reihenfolge folgt

Priorität des Auftraggebers: **Framework-Konsolidierung vor Feature-Erweiterung.** Nur nachweislich
Fehlendes wird gebaut; Altes wird erst nach nachgewiesener Funktionsgleichheit entfernt.

**Phase 0 — vor jeder Maske**

| # | Arbeit | Fertig, wenn | Zuständig |
|---|---|---|---|
| 0.1 | DocFlow: Mandant aus der Anmeldung | kein Weg nimmt den Mandanten aus der Anfrage | Identität (Codex) |
| 0.2 | DocFlow: Teilmengen über mehrere Folgebelege mit Restmengenrechnung | ein Auftrag → drei Teillieferscheine → zwei Rechnungen; Überlieferung wird abgelehnt | Claude Code |
| 0.3 | DocFlow: Statushistorie und Protokoll, die nicht ausfallen dürfen (wer, wann, von, nach, Grund) | kein Statuswechsel ohne Eintrag; Fehler bricht den Wechsel ab | Claude Code |
| 0.4 | DocFlow: Einkaufsbelegarten mit Übergängen; Eingangsrechnung bucht über Finance | Bestellung → Wareneingang → Eingangsrechnung mit Bezug je Position; Buchungsstatus prüfbar | Claude Code |
| 0.5 | DocFlow: Gutschrift bucht über Finance; Storno in einem Commit | eine Gutschriftstruktur | Claude Code |
| 0.6 | Testbenutzer im Keycloak (lokal und Staging), Zugangsdaten nur in der Umgebung | Playwright meldet sich über OIDC/PKCE an | Identität (Codex) mit Auftraggeber |
| 0.7 | Referenzbelege im Testmandanten (Positionen, Steuerarten, Status, Rechte) als wiederholbares Skript | Belege entstehen reproduzierbar | Claude Code |
| 0.8 | Bildschirmfoto-Baselines mit Playwright; manuelle Sichtabnahme als Schritt | reproduzierbarer Lauf mit Fotos | Claude Code |
| 0.9 | Kanonisches Schema festschreiben: ScreenDefinition ist die eine Quelle; TS-Kopie (K2) wird erzeugt oder entfällt; Variante als Begriff | keine von Hand gepflegte Zweitdefinition | Claude Code |

**Phase 1 — Referenzimplementierung:** universelle Eingangsbelegmaske auf DocFlow, mit den dafür
fehlenden Framework-Teilen in dieser Reihenfolge: Variante (0.9), Positionsbaustein, Value Help für
Lieferant und Artikel, Neuberechnung am Server (Side Effects), Meldungsabbildung, Belegentwurf.
Abnahme fachlich und visuell. Keine destruktive Änderung an bestehenden Einkaufs- oder
Buchhaltungstabellen.

**Phase 2 — weitere Einkaufs- und Verkaufsbelege**, je Maske mit Funktionsinventur; danach Abbau der
Altstrukturen mit dokumentiertem Rückfallkonzept.

Nicht geplant: ein zweites UI-Framework, Fiori-Konzepte ohne nachgewiesenen Bedarf (Analytische Liste,
weitere Floorplans), steuerliche Regeln in Definitionen.
