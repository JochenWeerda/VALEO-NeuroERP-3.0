---
title: Adaptive Workspace und Qualitaetsprotokolle - unabhaengige Pruefung
type: reference
owner: Codex
status: reviewbefunde-behoben
last_reviewed: 2026-10-24
---

# Pruefung des angeforderten Root-Arbeitsstands

Geprueft: adaptive-workspace-framework.md, adaptive-workspace-events-mcp.md, test_workspace_agrar_chain.py, test_workspace_sse_mirror.py, live-signals.ts, app/workspace/events.py, quality_protocols.py und quality_protocol_repo.py. Ergaenzend die tatsaechlich aufgerufenen Service-/Outbox-/NATS-Pfade und Schema-Constraints. Massgeblich ist der Root-Arbeitsbaum, nicht die unabhaengige Reparaturansicht. Ergebnis: keine fachliche Gesamtfreigabe.

## Befunde

| ID | Prioritaet | Ort im geprueften Stand | Befund und Folge |
|---|---|---|---|
| AW-R01 | P1 | quality_protocols.py:294,302 | approved_by wird unverifiziert aus dem Body in finale Fassung und Event uebernommen. Der gepruefte Tokenurheber entscheidet hier nicht. Manipulierbare Freigabezuordnung; Urheber serverseitig binden. |
| AW-R02 | P1 | quality_protocols.py:163-165; quality_protocol_repo.py:81-85,100-104 | Anlegen/Import prueft nicht, ob die angegebene harvest_acceptance_id zum verifizierten Mandanten gehoert. Auch die Versionssuche ist nicht tenantgebunden. Echte Probe-Constraints sind nur einzelne FKs auf Annahme und Mandant, RLS ist aus: kein ersetzender DB-Schutz. Fremdverknuepfung und fremde Versionsbeeinflussung werden im Schreibpfad nicht verhindert. |
| AW-R03 | P1 | quality_protocols.py:307-316; outbox.py:43-60 | store_event spiegelt standardmaessig vor commit auf SSE. Reproduziert: Ereignis sichtbar, anschliessender Rollback hinterlaesst null Outboxzeilen. Datenbank und Live-Anzeige widersprechen sich. Erst nach erfolgreichem Commit ueber dauerhaftes Outbox-Verfahren spiegeln. |
| AW-R04 | P1 | events.py:250-255; nats_publisher.py:38-45 | Tatsaechlicher NATS-Serializer liefert aussen event_type=IntegrationEvent, innen den Ist-Typ, ohne tenant_id. Workspace-Handler verwirft genau diesen Umschlag. Reproduziert ohne echten Broker mit unveraendertem Serializer und echtem Handler. Der RecordingPublisher-Test prueft diesen Draht nicht. |
| AW-R05 | P1 | quality_protocol_repo.py:151-163; quality_protocols.py:282-294 | Pruefen und Festschreiben sind nicht durch Rowlock, bedingtes UPDATE oder Versionspruefung verbunden. Zwei Anfragen koennen denselben offenen Stand passieren, zwei Finalisierungen/Events erzeugen und den Freigebenden ueberschreiben. Der vorhandene Test prueft ausschliesslich serielle Wiederholung. Codebefund; kein paralleler PostgreSQL-Reproducer in dieser Pruefung. |
| AW-R06 | P2 | quality_protocols.py:148,184; adaptive-workspace-events-mcp.md | Dokumentiertes GET /api/v1/agrar/quality-protocols fehlt im Root-Router. Reproduziert:405. Die Qualitaets-Worklist besitzt damit keinen behaupteten Lesepfad. Ein GET-Nachtrag liegt bereits im separaten Reparaturbaum, ist im geprueften Root aber noch nicht integriert. |
| AW-R07 | P2 | quality_protocols.py:129-133,167-171,259-263 | Numerische Werte werden per Wahrheitswert statt is not None geprueft. Echte Nullwerte werden beim Schreiben verworfen und beim Lesen als null statt0 ausgegeben; reproduziert fuer Feuchte und Mykotoxin. |
| AW-R08 | P2 | events.py:192-205 | Ereignis-ID wird vor erfolgreichem broadcast als erledigt gespeichert. Nach einem Transportfehler wird der Wiederholungsversuch derselben ID unterdrueckt. Reproduziert: erster Versand fehlschlaegt, zweiter erreicht den Hub nicht. Erfolg erst nach Lieferung vormerken bzw. fehlgeschlagenen Versuch freigeben. |
| AW-R09 | P2 | live-signals.ts:317-329,368-374 | onerror schliesst EventSource dauerhaft; kein Neuaufbau/Tokenwechsel und keine Queue-Nachladung. Kurzer Verbindungsverlust beendet die Live-Aktualisierung fuer die gesamte Mountdauer. Der Test prueft Kalenderanzeige nach Fehler, keine Wiederherstellung. |

## Durchgefuehrte Pruefungen

- 76 Python-Unit-Tests aus beiden angeforderten Testdateien bestanden.
- 3 PostgreSQL-Integrationstests aus test_workspace_agrar_chain.py bestanden, ohne Skip. Ausschliesslich vorhandene valeo_probe, vorheriger Status loading_stop_fk_20261023; eigene synthetische Testzeilen durch vorhandenen Cleanup entfernt. Keine neue Datenbank/Container, kein Reset.
- 4 Frontendtests in live-signals.test.tsx bestanden. Erster Sandboxlauf scheiterte vor Sammlung an einer Windows-Tempdateisperre; derselbe direkte Vitest-Lauf ausserhalb dieser Sperre bestand. Keine Abhaengigkeiten installiert.
- Eigener Reproducer artifacts/workspace-review-20261023.py: GET405, Nullwertverlust, SSE vor Commit trotz Rollback, verlorener Wiederholungsversuch und verworfener echter NATS-Umschlag. HTTP-TestClient/SQLite im Speicher; NATS-Transport simuliert, Serializer und Handler echt. Kein Nachweis eines Live-Brokers behauptet.
- Reale Probe-Schemainspektion: QualityProtocol-FKs nur harvest_acceptance_id zu harvest_acceptances.id und tenant_id zu tenants.id; relrowsecurity=false. Kein mandantenuebergreifender Fachdatensatz angelegt.

Die gruenen Tests widerlegen die Befunde nicht: Es fehlen insbesondere manipulierter Freigebender, fremde Annahme, konkurrierende Finalisierung, Rollback ohne Live-Signal, fehlgeschlagener SSE-Retry, echte NATS-Serialisierung sowie Wiederverbindung mit frisch validierter Sitzung. Die Dokumentation nennt den Spiegel erreicht; dieses Wort muss zwischen lokalem Unit-Draht und produktionsgetreuem NATS-/Commit-Nachweis unterscheiden.

Keine der acht geprueften Produktions-/Testdateien wurde fuer diese Pruefung korrigiert. Befunde sind offen; bereits vorhandene Reparaturarbeit wird vor Umsetzung integriert und nicht doppelt gebaut.


## Reparatur AW-R08

AW-R08 ist im Quellstand korrigiert: Ereignisidentitaet aus Mandant plus Ereignis-ID; erfolgreich erst nach Broadcast merken. Fehlversuche, unbekannte Typen und abgebrochene Versuche verbrauchen die Identitaet nicht. Gleichzeitige Duplikate teilen den laufenden Versuch; ein wartender Aufrufer kann ihn nicht abbrechen. Cache bleibt auf512 erfolgreiche Ereignisse begrenzt und pro Prozess best-effort, kein dauerhafter Nachrichtenzustellnachweis.

Gemeinsame Abnahme:41 Tests bestanden (36 bestehende SSE-Vertraege plus5 neue Fehler-/Mandanten-/Parallel-/Abbruchfaelle), ohne Datenbank oder Container. Acht weitere Reviewbefunde bleiben offen. Die Workspacequelle lag bisher nur im geteilten Arbeitsbaum, nicht in HEAD; dieser eng gepruefte Ereignisspiegel wird erstmals im Reparaturzweig versioniert. Die gesamte fremde Workspaceimplementierung wird dabei nicht mitcommittet. Keine Live-NATS-/Browser- oder Gesamtfreigabe.


## Reparatur AW-R07

Alle15 numerischen Konvertierungen fuer Ausgabe, Anlage und Aenderung unterscheiden jetzt None von0. Feuchte, Besatz, Hektolitergewicht, Protein und Mykotoxin verlieren gemessene Nullwerte nicht mehr.45 neue Vertragsfaelle bestanden: je Feld fehlend,0 und positiver Messwert fuer Ausgabe/Anlage/Aenderung. Die Schreibfaelle pruefen die echte Route bis zur Decimal-Uebergabe an den Fachservice; kein Datenbank-Persistenznachweis und keine Rollenabnahme behauptet. Vorhandene fremde GET-/Outbox-Aenderungen wurden erhalten und nicht mit diesem Commit vermischt. Zusammen mit AW-R08 sind zwei der neun Befunde korrigiert; sieben bleiben offen.


## Abschluss der neun Reviewbefunde am 24.10.2026

Alle neun Befunde sind im Reparaturzweig behoben. AW-R07/08 waren bereits
separat gepusht; dieser Nachlauf schliesst AW-R01/02/03/04/05/06/09.

- AW-R01: allein verifizierter Token-sub als Freigebender; echte RSA/JWKS-HTTP-Gegenproben fuer manipulierte Body-/Headerangaben, ungueltige Signatur und fehlende Fachrolle.
- AW-R02: Pflichtmandant im Repository und allen Aufrufern, tenantgebundene Protokoll-/Parentabfragen auch fuer Importe; exklusiver Parentlock vor Versionsvergabe. Fremde Elternreferenz real auf PostgreSQL abgewiesen.
- AW-R03: store_event erzeugt ausschliesslich Outboxzeilen, niemals vorzeitiges SSE. Explizites mirror_on_store=True wird abgelehnt. Finalisierung und Abschlussereignis liegen im selben Commit; echter gemeinsamer PostgreSQL-Rollback belegt.
- AW-R04: IntegrationEvent traegt Tenantkontext; der echte NATS-Serializer uebertraegt Ist-Typ, unveraenderten Business-Payload, Ereignis-ID und Tenant. Outboxzeile ist fuehrend; widerspruechliche Payloads und direkte Tenantueberschreibungen werden abgewiesen. Transportfehler propagieren; auch nach drei Fehlern bleibt der Datensatz offen statt faelschlich veroeffentlicht. Bestehende domain-Subjects bleiben erhalten.
- AW-R05: Zeilensperre mit populate_existing und Zustandspruefung im Repository verhindert konkurrierende Freigabe bzw. nachtraegliche Aenderung auch bei vorgeladenem ORM-Zustand.
- AW-R06: dokumentierter GET auf die Protokollsammlung existiert, typisiert und auf maximal200 Datensaetze des angemeldeten Mandanten beschraenkt.
- AW-R09: begrenzte Wiederverbindung mit frischem Token, erneutes autoritatives Queue-Lesen bei jedem Oeffnen und nach relevanten Ereignissen, Nullstandbereinigung und Timer-/Socket-Cleanup.

Abnahme:128 Backendtests gemeinsam bestanden,5 neue echte PostgreSQL-Faelle
plus3 bestehende Agrar-/Outbox-HTTP-Faelle ohne Skip und11 Frontendtests.
Fokussierte TypeScript-Pruefung einschliesslich tatsaechlicher Importabhaengigkeiten
und Test-Matcher gruen. Keine neue DB/Container, kein Reset; eigene PG-Zeilen
gezielt entfernt. Sandbox-Asynclaeufe koennen unter Windows haengen; die
aufgefuehrten erfolgreichen Laeufe liefen mit normalem Windows-Prozesszugriff.

OpenAPI wurde aus sauberem HEAD plus genau sieben geprueften Produktionsdateien
erzeugt: weiterhin3246 Pfade, nur drei Quality-Pfade geaendert; QueueOut neu und
unvertrauenswuerdiger FinalizeIn entfernt. Agentenhandbuch und Inventare aus
vollstaendigen versionierten Quellen nachgezogen. Fremde uncommittete API- und
Studioarbeiten bleiben erhalten. Die reine Live-Signal-Importkette ist fuer den
Commit eigenstaendig, ohne den fremden Inbox-/Studio-UI-Baum mitzupublizieren.

Grenze: Dies schliesst diese neun Codebefunde, nicht die gesamte Studio-Migration
oder alle Projekt-CI-Befunde. Der NATS-Transporttest verwendet den echten
Serializer/Handler mit aufgezeichnetem JetStream-Transport; keine Live-Broker-
oder Browserabnahme behauptet. SSE-Deduplizierung bleibt prozesslokal und
begrenzt; verbindlicher Zustand wird ueber authentifizierte Reads nachgeladen.
