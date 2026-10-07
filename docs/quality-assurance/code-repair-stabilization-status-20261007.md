---
title: Code-Reparatur und Stabilisierung - Gesamtzielstand 2026-10-07
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-07
---

# Code-Reparatur und Stabilisierung: verbleibende Arbeit

Abgleich des laufenden Chats mit Workboard, Handshakes, Open Gaps, Code und
GitHub auf `00de664df`. Diese Liste ist ein priorisierter Reparaturstand,
keine Vollstaendigkeits- oder Betriebsfreigabe. Lieferstand bleibt
[Process Kernel STATUS](../architecture/process-kernel/STATUS.md) mit den
Wave-Statusdateien. Aktiver Dateibesitz steht im
[Workboard](../agent-ops/active-workboard.md).

## Aktuelle Abnahme statt historischer Testzahlen

[Schnittstellenintegration](domain-interface-integration-20261007.md): vier echte
Fachaktionspfade nachgezogen, keine Pfade entfernt; OpenAPI 3101 Pfade, drei
Inventare und kompletter Architekturindex (935/275/454) aktuell. 24
Architekturvertraege und fuenf fremde Handbuchartefakte lesend geprueft.
Die 41 doppelten API-Pfad-/Methodengruppen sind dabei erneut bestaetigt.

[NPM-Herstellerfixes](npm-security-releases-20261007.md): zwoelf Paketpins,
frozen Lockfile auf 36 committed Workspaces und sechs reale Offline-Vertraege
gruen. Production-Audit jetzt 2 High, 0 Moderate/Low/Critical; die beiden High
haben weiterhin keinen Herstellerfix. Behavior-Vertraege laufen fortan vor
dem unveraenderten CI-Audit. Frischer Workspace-Build bleibt erforderlich.

Fachliche Integrations-Teilabnahme auf `c466af7de`: 71 Tests ohne Skip gruen
(66,35 s), einschliesslich SPEC-P1-04-Inventur, echten Maskenwirkungen,
Lager-Gegenbuchung und Opportunity-Mandantenvertraegen. Gemeinsamer Probe
vorher lesend vorhanden auf `mandant_finanz_crm_20261007`; kein Reset/neue DB.
Isolierte committed Pakete fuer `app` und `scripts`; keine Arbeitsbaum-Mischung.
Die bekannten echten Action-Luecken bleiben aktiv beim fremden Fachclaim.

Der [KIM-Navigations-Smoke](kim-navigation-smoke-20261007.md) ist lokal repariert:
gueltige isolierte Kunden-Lesefixture statt nicht existierendem PERF-K1;
native Identitaetsanzeige/Registerwahl und fehlender Kunde separat geprueft,
zwei Chromium-Vertraege gruen. Kein Produkt- oder Persistenz-Scheinerfolg;
frischer GitHub-Lauf bleibt erforderlich.

Weitere Teilabnahme: [CPython-Herstellerfix](cpython-upstream-security-20261007.md)
hebt das Backend-Image auf echtes 3.13.16, entfernt drei ueberholte Backports und
erhaelt den nachweislich notwendigen POP3-Schutz. Fuenf Runtime-Sicherheitstests
bestanden; neuer Tarfile-Vertrag auf 3.13.15 bewusst rot. Linux-/Grype-Abnahme
und Node-Audit bleiben offen.

Teilabnahme dieser Abarbeitung: [Native Vertragsreparaturen](native-mask-contract-repairs-20261007.md)
schliessen sechs der elf Backend-Fehler auf `3e7142c48` und beide Frontendbefunde
lokal: 813 Pythonvertraege, 23 Architekturvertraege, 38 Frontendtests und TypeScript
gruen. OpenAPI/Inventare/Handbuch folgen den bereits committeten sieben ehrlichen
Action-Loeschungen; Praesente neu typisiert. Neue Actions-Abnahme bleibt erforderlich.
SPEC-P1-04 und KIM sind inzwischen lokal nachgeprueft; neue CI-Gesamtabnahme,
verbleibende Security-Befunde und weitere fachliche Integrationen bleiben offen.
Die historische Liste unten dokumentiert ihren Ausgangspunkt.

Auf `00de664df` erfolgreich: PostgreSQL `require_db` (37610643657), OpenAPI
(37610643398), Docs Build/Governance, Service Security, Full Security Agent,
E2E Smoke (37610643388), kritische E2E (37610643487), Erntepeak.
Dies schliesst andere rote Gates nicht automatisch.

| Prioritaet | Offen / naechster Nachweis | Evidenz / Besitz |
|---|---|---|
| P0 | Security Scan: Production-Audit und Backend-Grype | [Run 37610643700](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/37610643700): node-forge/braces weiter high, Grype `--only-fixed --fail-on high` rot. Kein Ignore oder abgesenkter Schwellwert. |
| P0 | Verbleibende echte Fachaktionswege und globale Belegnummernkanonisierung | Die vier Mandanten-/Mutationsbefunde sind laut Workboard geliefert; Opportunities einschliesslich Pipeline/Forecast tenantgebunden. Lokale Teilintegration 71 Tests gruen. `MANDANT-FINANZ-CRM-EINKAUF-20261007` bleibt bei Claude fuer Lead-Qualifizierung und echte Ernte-PDF-Ablage offen; nicht doppelt bearbeiten. Globale `documents.doc_number`-Eindeutigkeit bleibt ausserhalb dieses Fachclaims offen. |
| P1 | Frische Backend-Vollsuite abnehmen | Die historischen elf Fehler sind lokal durch 813 plus 71 gezielte Vertraege abgedeckt. [PostgreSQL-Lauf auf c466af7de](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/37644389765) gruen; dies ersetzt die weiterhin ausstehende komplette Pipeline-Abnahme nicht. |
| P1 | Frisches Frontend-Quality Gate abnehmen | Schulungen-Delegation und Titelduplikate lokal mit 38 Tests plus TypeScript geschlossen. [Quality auf c466af7de](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/37644390353) wegen Folgepush abgebrochen; kein neuer erfolgreicher Vollnachweis. Fremde Renderer-WIP erhalten. |
| P1 | Frisches CI-Schema und physischer Tabellenkatalog harmonisieren | Lokal 659 Tabellen geprueft; kein Ersatz fuer frische CI-Abnahme. Generator, Test und Quality-Workflow sind fremde WIP. Kein Reset oder neue Testdatenbank. |
| P1 | 41 doppelte API-Pfad-/Methodenregistrierungen beseitigen | Letzter main.app-/OpenAPI-Abgleich im Personal-Rollenschutz: ausgefuehrten Handler, DTO und Verbraucher gemeinsam kanonisieren, keine pauschale Compat-Loeschung. |
| P1 | Finanzbuchungen durchgehend zentral und atomar | [Open Gaps](../project-context/open-gaps-and-known-issues.md): echter Kassenabschluss, Consumer der commit-freien Journaltransaktion, weitere Rohschreiber/Periodensperren, Anlage-/Schema-/Bewertungskanonisierung und Hauptbuch-/Bankintegrationsnachweise. `L3-JOURNAL-SOURCE-20260910` hat fremden aktiven Besitz. |
| P1 | Futter-Schreibwege und Modelle harmonisieren | Listen-/Loeschschutz geschlossen; weitere Anlage-/Aenderungs-/Rezepturwege, ArticleModel-Projektion gegen FutterStamm/Einzel-/Mischfutter und Frontend-DTO-Verbraucher bleiben getrennte Arbeit. |
| P1 | Bewerbungsprozess vollstaendig und nachvollziehbar | 16 Rollenwege geschlossen; Selbstwiderruf fuer Bewerber, UI-Rollensteuerung und authentifizierter Akteur statt frei gelieferter `durchgefuehrt_durch`/`erfasst_durch` offen. |
| P2 | Wiegemodell technisch bereinigen | ADR-077 entscheidet `domain_inventory.weighing_tickets`; alte Mobile-/Operations-Verbraucher noch nicht vollstaendig rueckgebaut. |
| P2 | CRM-Persistenz und kanonisches Lead-Schema | `INTERESSENT-IST-LEAD`-Handshake: Umzug `public.crm_leads` mit Verbrauchern, Begriffsentscheidung `domain_crm.leads`, fluechtiger Portal-Interessentenspeicher. Nicht mit diesem Headerfix geschlossen. |
| P2 | Laufzeit-, Abdeckungs- und Betriebsnachweise erneuern | Alte GET-5xx-Liste, Nightly/UAT und Abdeckungszahlen sind keine aktuelle Vollabnahme. Kritische Kernpfade vor Flaechenabdeckung; Performance und Importkosten messen. Externe Go-live-Gates bleiben Betriebsverantwortung. |

Historische Fehler des Ausgangs-Backendlaufs, inzwischen lokal nachgeprueft:

- `fuhrpark/fahrzeug-stamm/loeschen`: ungueltiges `dangerLevel=destructive`
  in zwei Governance-/Safetytests; Schema und native Definition gemeinsam pruefen.
- Zwei Tabellenquellen ohne deklarierte Zeilenform:
  `crm/customer-360/praesente` und `personal/bewerbung-einwilligung/vorgaenge`.
- Spaltennavigation `fuhrpark/terminarten`: widerspruechlicher Vertrag `single`.
- Native Command-Inventur: ein verbliebenes `stubReason`.
- Bewerbungs-Pipeline-Test setzt Loeschen als erste Zeilenaktion voraus,
  obwohl Einwilligungsnavigation hinzugekommen ist.
- Bewerbungs-Loeschroutentest liest das alte `personal.router` statt des
  kanonischen `personal_bewerbungen.router` nach der Zerlegung.

Offene GitHub-Code-Scanning-Alerts enthalten ausserdem urllib3-, Python- und
ChromaDB-Befunde. Ein offener Alert allein belegt nicht den aktuellen Commit
oder das aktuelle Image: Analysezeitpunkt, Branch, Paketpfad und Herstellerfix
muessen vor einer Reparatur einzeln abgeglichen werden. Insbesondere bedeutet
`0 critical` im Node-Audit nicht `0 critical` im gesamten Repository.

## Bereits geschlossen: keine Doppelarbeit

Die vier im Chat genannten Handshake-Punkte sind im
[Open-Gaps-Nachweis](../project-context/open-gaps-and-known-issues.md#handshake-gap-closure--vier-benannte-befunde-2026-10-05)
geschlossen: Ledger-Options-Paginierung, Bank-Fixture, mandantenbezogene
Journalnummer und Entscheidung zum fuehrenden Wiegemodell. Der technische
Waage-Rueckbau bleibt oben aufgefuehrt. `logistics_tours.py` liegt beim letzten
Groessengate bei 1031 Zeilen; die historische 1059-Zeilen-Verletzung ist damit
kein unveraendert aktueller Befund.

`af2b90fac` behebt die erfundenen Erfolgsmeldungen der Mask-Aktionen. Die dabei
sichtbar gewordenen vier Fach-/Mandantenbefunde sind aktiv geclaimt, aber noch
nicht abgenommen. Personal-Rollenschutz `00de664df`: 161 neue plus 163 bestehende
Vertraege bestanden; kein Ersatz fuer die rote Gesamt-CI.

## Reparatur in dieser Fortsetzung: Interessenten-Fehlerantwort

Der zentrale `X-Migration-Hint` enthielt einen Gedankenstrich, den Starlette
beim Header-Encoding nicht verarbeiten konnte. Bei Datenbankfehlern stuerzten
sowohl die vorgesehene 503-Leseantwort als auch die 409-Anlageantwort ab. Der
Hinweis verwendet jetzt einen ASCII-Bindestrich; Inhalt, Statuscodes und
Rollback-Verantwortung bleiben erhalten.

Der alte Anlagetest mockte einen entfernten `COUNT`-Weg. Er prueft jetzt das
kanonische Register: Jahres-/Maximalnummer-Abfrage, exakte naechste Nummer,
`INSERT INTO public.crm_leads`, Tenantparameter, gespeicherte Antwort und genau
einen Commit. Keine alternative Nummernlogik eingefuehrt.

Red: zwei echte FastAPI-HTTP-Fehlerantworttests reproduzierten vor dem Fix
`UnicodeEncodeError`. Green: alle 18 Vertraege in
`test_sammelabrechnung_interessent_waagen_vorlage.py` bestanden, null Skip,
Exit 0 (1,87 s). GET/POST liefern 503/409 inklusive Migrationsheader und JSON;
Rollback genau einmal, kein Commit im Fehlerfall. Ein vorhandener
Starlette/httpx-Deprecation-Hinweis bleibt. Keine DB-Verbindung oder Migration.

## Fortlaufender Betrieb und Effizienz

Reihenfolge: bestaetigte Sicherheits-/Mandantenfehler, rote ausfuehrbare
Vertraege, kanonische API-/Journalintegration, dann erneut Vollsuite und
Laufzeitabnahme. Claims, Commits und Actions-Evidenz verhindern Doppelarbeit;
geschlossene Teiltests werden nur nach relevanter Aenderung erneut ausgefuehrt.
Keine Gate-Abschwaechung und keine historischen Zahlen als Freigabe.

Alle Agenten verwenden den gemeinsamen Probe beziehungsweise die konfigurierte
`TEST_DATABASE_URL`. Vor DB-Tests `pruefstand_db.py --status`, Isolation durch
Transaktionen/eigene Datensaetze, keine neue DB/Container pro Test/Slice/Agent,
kein Reset oder Docker-Prune. Dieser Slice prueft ohne DB-Verbindung. Fremde
laufende Aenderungen und deren Ressourcen bleiben geschuetzt.
