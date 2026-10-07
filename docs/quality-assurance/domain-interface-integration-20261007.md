---
title: Schnittstellen-Nachzug nach echten Fachaktionen
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: lokal_geprueft
last_reviewed: 2026-10-07
---

# Schnittstellenintegration der Fachmeilensteine

Quelle ist der isolierte committed Stand `f9981f7e0`, einschliesslich
`5db4b4944`, `71aecf2ae`, `54a659699` und `28e6133ed`.
Die vorherige OpenAPI-Lieferung `d8f9117d4` lag vor diesen Fachaktionen.
Es wurde derselbe kleine Quellsnapshot wiederverwendet; `app`, `scripts`
und `main` wurden explizit auf dessen Herkunft geprueft. Keine Root-WIP uebernommen.

Vier inzwischen wirklich implementierte Action-Pfade sind neu veroeffentlicht:

- Opportunity-Aktivitaet anlegen.
- Einkaufsangebot in eine Bestellung umwandeln.
- Wareneingang aus dem Anlieferavis.
- Lagerbewegung durch Gegenbuchung stornieren.

Keine Pfade entfernt. 14 vorhandene Pfade tragen die inzwischen geaenderten
Opportunity-Mandantenvertraege, Lager-/Warehouse-Vertraege und Storno-Antworten.
Die Spezifikation hat jetzt 3101 Pfade. Das ist ein Artefakt-Nachzug der gelieferten
Fachimplementierungen, kein neuer Fake-Endpunkt oder Erfolgspfad.

## Architektur und Abnahme

Der neue `wareneingang_avis_service` war als einziger Service ohne Domain-Mapping.
Er fuehrt Avis und kanonische Bestellung und delegiert den Lagerzugang;
deshalb exakte Zuordnung zu `procurement`, analog `einkauf_compat_service`.
Kein breiter neuer Prefix, neuer Kontext oder Container. Das vorhandene
Architecture Agent Protocol und Einkauf-Domain-Pack wurden konsultiert;
Minor-Inventarkorrektur ohne neue Architekturentscheidung.

- OpenAPI deterministisch auf derselben realen `main.app` erzeugt und erneut geprueft.
- Drei Code-Inventare erzeugt; `--check` gruen.
- Architektur `--require-complete` und `--check` gruen:
  935 Routen, 275 Services, 454 Endpoints, alle zugeordnet.
- 24 Architekturvertraege bestanden (0,90 s).
- Alle fuenf Handbuchartefakte des aktiven Fachowners mit `--check` aktuell;
  keine fremde Handbuchlieferung ueberschrieben.

Die Anwendung registriert weiterhin 41 doppelte Pfad-/Methodengruppen.
Dieser Befund bleibt offen; keine pauschale Compat-Loeschung ohne
Handler-/DTO-/Verbraucherabgleich. Die verbleibenden echten Action-Luecken
und fachlichen Architekturentscheidungen bleiben bei ihrem aktiven Owner.
Keine neue DB/Container, Reset, Migration oder Schreibzugriffe im Probe;
Generator-Import ist keine Abnahme einer Fachmutation.

Neue GitHub-Drift-Abnahme erforderlich. Die separate lokale Fachintegration
auf `c466af7de` hat 71 Tests ohne Skip bestanden; sie ersetzt nicht den
vollstaendigen CI-Lauf dieses Artefakt-Nachzugs.
