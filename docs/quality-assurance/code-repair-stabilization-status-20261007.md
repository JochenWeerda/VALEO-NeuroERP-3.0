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

Auf `00de664df` erfolgreich: PostgreSQL `require_db` (37610643657), OpenAPI
(37610643398), Docs Build/Governance, Service Security, Full Security Agent,
E2E Smoke (37610643388), kritische E2E (37610643487), Erntepeak.
Dies schliesst andere rote Gates nicht automatisch.

| Prioritaet | Offen / naechster Nachweis | Evidenz / Besitz |
|---|---|---|
| P0 | Security Scan: Production-Audit und Backend-Grype | [Run 37610643700](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/37610643700): node-forge/braces weiter high, Grype `--only-fixed --fail-on high` rot. Kein Ignore oder abgesenkter Schwellwert. |
| P0 | Mandanten-, Rollen-, Vier-Augen- und atomare Mutationsfehler in Zahlungslaeufen, Eingangsrechnungen, Opportunities und Angebotsumwandlung | `MANDANT-FINANZ-CRM-EINKAUF-20261007`, Claude Code, in Arbeit; acht Zahlungswege betroffen. Nicht doppelt bearbeiten. Globale `documents.doc_number`-Eindeutigkeit und Opportunity-Pipeline/Forecast ausserhalb seines Claims weiter offen. |
| P1 | Backend-Vollsuite wieder gruen | [Run 37610643394](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/37610643394): acht Fehler, 16025 bestanden, 324 Skip, ein xfail. Interessenten-Anlagevertrag in diesem Slice korrigiert; die sieben anderen Fehler unten. Neue Actions-Abnahme erforderlich. |
| P1 | Frontend-Quality Gate wieder gruen | [Run 37610643941](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/37610643941): zwei Fehler, 969 bestanden; Schulungen-Test erwartet alte lokale Filtervariablen, Worklist-Titeltest findet drei H1. Ursache am committed Code pruefen; Renderer-WIP nicht blind uebernehmen. |
| P1 | Frisches CI-Schema und physischer Tabellenkatalog harmonisieren | Lokal 659 Tabellen geprueft; kein Ersatz fuer frische CI-Abnahme. Generator, Test und Quality-Workflow sind fremde WIP. Kein Reset oder neue Testdatenbank. |
| P1 | 41 doppelte API-Pfad-/Methodenregistrierungen beseitigen | Letzter main.app-/OpenAPI-Abgleich im Personal-Rollenschutz: ausgefuehrten Handler, DTO und Verbraucher gemeinsam kanonisieren, keine pauschale Compat-Loeschung. |
| P1 | Finanzbuchungen durchgehend zentral und atomar | [Open Gaps](../project-context/open-gaps-and-known-issues.md): echter Kassenabschluss, Consumer der commit-freien Journaltransaktion, weitere Rohschreiber/Periodensperren, Anlage-/Schema-/Bewertungskanonisierung und Hauptbuch-/Bankintegrationsnachweise. `L3-JOURNAL-SOURCE-20260910` hat fremden aktiven Besitz. |
| P1 | Futter-Schreibwege und Modelle harmonisieren | Listen-/Loeschschutz geschlossen; weitere Anlage-/Aenderungs-/Rezepturwege, ArticleModel-Projektion gegen FutterStamm/Einzel-/Mischfutter und Frontend-DTO-Verbraucher bleiben getrennte Arbeit. |
| P1 | Bewerbungsprozess vollstaendig und nachvollziehbar | 16 Rollenwege geschlossen; Selbstwiderruf fuer Bewerber, UI-Rollensteuerung und authentifizierter Akteur statt frei gelieferter `durchgefuehrt_durch`/`erfasst_durch` offen. |
| P2 | Wiegemodell technisch bereinigen | ADR-077 entscheidet `domain_inventory.weighing_tickets`; alte Mobile-/Operations-Verbraucher noch nicht vollstaendig rueckgebaut. |
| P2 | CRM-Persistenz und kanonisches Lead-Schema | `INTERESSENT-IST-LEAD`-Handshake: Umzug `public.crm_leads` mit Verbrauchern, Begriffsentscheidung `domain_crm.leads`, fluechtiger Portal-Interessentenspeicher. Nicht mit diesem Headerfix geschlossen. |
| P2 | Laufzeit-, Abdeckungs- und Betriebsnachweise erneuern | Alte GET-5xx-Liste, Nightly/UAT und Abdeckungszahlen sind keine aktuelle Vollabnahme. Kritische Kernpfade vor Flaechenabdeckung; Performance und Importkosten messen. Externe Go-live-Gates bleiben Betriebsverantwortung. |

Die sieben weiteren Fehler des genannten Backendlaufs:

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
