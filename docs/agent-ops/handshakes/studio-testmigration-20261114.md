# Studio-Testmigration und Vertragsreparaturen — 14.11.2026

Fortsetzung auf `codex/sonar-coverage-20261113`, PR #133. Im isolierten
Arbeitsbaum gearbeitet; keine Datenbank, kein Container, keine Migration.
Alle Teilthemen vor Umsetzung im Workboard reserviert. Der Lead integrierte
die nach dem Nutzungslimit hinterlassenen Aenderungen und pruefte sie.

## Gepruefter Meilenstein

- Runtime46 von 181 auf **131 Faelle in 38 Dateien** gesenkt, neun Smoke-Ausnahmen
  unveraendert. Keine neue Ausnahme und keine Abschwaechung der Ratsche.
- 31 reine Quellen-/Stiltests durch echte Klassen-/Touch-/Kontrastvertraege
  ersetzt (94 Tests); die einzelnen entfernten Faelle sind im Klassen-QA gelistet.
- Zwoelf alte Workflowfaelle durch 13 Prozessraumtests und drei Bestellvorschlag-
  Faelle durch zwoelf Tests der versionierten Familie ersetzt. Builder-Fixtures
  sind direkt gegen die oeffentlichen Backendgeneratoren abgesichert.
- Drei Betriebslisten und Sortendetail verhaltensgeprueft; Zertifikatsroute auf
  das vorhandene Register korrigiert. Neue Sortenobjektdefinition benutzt
  denselben GET/PUT, echte Bereichsrollen und die enge Ressourcen-Allowlist.
- Sorten-GET ohne Read-Time-Seed: Gegenprobe zeigte fuenf Inserts beim Lesen
  eines leeren Mandanten. Nach Rueckbau 26 DTO-/Rollen-/Routertests gruen.
  Alte globale Devtoken-/Seedtests durch isolierte Vertraege ersetzt.
- Gemeinsame Dialogbeschreibungen mit eindeutigen Radix-IDs; 26 betroffene
  Tests gruen. Nachweis vor Fix: ID-Kollision bei zwei Instanzen.
- CLI `resource.v1` konnte einen Trockenlauf als echten PUT versenden.
  Execute-only, Identitaetsbindung, deklarierte Eingaben und Antwortpruefung
  sind jetzt explizit. Die acht versionierten Segment-/DSGVO-Wege behalten
  Version, Idempotenz und Auditgrund, gegen echte Servermodelle geprueft.
  75 gezielte CLI-/Lesevertraege plus finaler Register-/Kanalnachlauf mit
  29 Faellen gruen; diese Laeufe ueberschneiden sich.
- Herstellerfixes fuer sechs Node-Advisories, selektiver OTel-Patch ohne
  Hochziehen unbetroffener alter Versionslinien. Gefrorene Installation,
  57 Security-Vertraege und Produktionsaudit mit null Befunden nachgewiesen.
  HTTP-Span-Vertrag bestaetigt die Schwaerzung von Signaturwerten.

Vollstaendige finale Frontend-Typpruefung Exit 0, 11 Registry-/Fixture-/
Godfiletests, drei Ratschenfaelle, Doku-Drift **0**, Docs-Governance gruen.
Sorten-/Listen-/Rollenprojektionsnachlauf 20 Frontendfaelle gruen. Rechte,
Studio-Katalog, MCP-/CLI-Register und Agent-Handbuch nachgezogen. Neue Sorten-
Definition A/B/C/E und draft-clean; das ist keine Live-Veroeffentlichung.

## Verbleibende fachliche Arbeit

131 alte Erwartungen sind noch nicht vollstaendig ersetzt. Die verbleibenden
69 Faelle in `service-annahme-feldservice-uix.test.ts` mischen technische
Altannahmen mit fachlichen Erwartungen; pauschales Loeschen waere unredlich.
Leistungsnachweise und Wareneingangsabgleich verwenden aktuell generische
Anfragequellen und besitzen die erwarteten Fachaktionen nicht. Fuer
Biostimulanzien/Sachkunde ist ein passender Detail-/Editweg nicht belegt.
Diese Funktionen vor Testabbau gegen kanonische Modelle/Wegvertraege reparieren.

Keine Gesamtmigration oder SQL-/RLS-/OIDC-/Browser-/Sonar-Abnahme behauptet.
Die neuen Unit-/Transporttests simulieren externe Daten-/Identitaetsgrenzen.
Letzter separat gepruefter Main-Sonarwert 70,9 Prozent, Ziel 80; frischer
GitHub-Nachlauf bleibt Pflicht. Historische Teilergebnisse nicht summieren
oder als Gesamtfreigabe umdeuten. Details in den datierten QA-Dateien.


## Fortsetzung: Action-Matrix, CI und Teilmengen

PR134 enthaelt die ehrliche Action-Matrix-Einordnung (38 Aktionen,
32 deklarierte Gaps; keine Laufverknuepfung fuer die sechs anderen).
Sicherheitsgate e733d8828 ist gruen; Nachlauf repariert MCP-Katalogdrift,
geraeteabhaengigen Kundenauswahltest und Scanner-Pythonruntime. Scannerbuild
und Gesamtnachlauf muessen auf dem finalen Commit bestaetigt werden.

Studio-Belegfamilie 1.9.0 ergaenzt echte explizite Teilmengen: preisfreier
Optionsabruf mit Version und Zielart, gemeinsame Tabelle, Vorschau und
Ausfuehrung ueber bestehenden Domain-Command. CLI bildet dieselben Werte ab;
Agentenwrites bleiben gesperrt. Bisherige Versionsinhalte wurden semantisch
gegen Git bestaetigt. Keine Matrix-Statusanhebung ohne realen Laufnachweis.
SQL-/OIDC-/Browsernachweis fehlt weiterhin; Statusskript hatte keine
Datenbank-URL. Details: docflow-teilmengen-eingabe-20261114.md und
 docflow-konvertierung-dialog-20261114.md unter quality-assurance.
