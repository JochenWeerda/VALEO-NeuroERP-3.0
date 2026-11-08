---
title: Integration offener Studio- und Workspace-Aenderungen
type: verification
owner: Codex
status: in-arbeit
last_reviewed: 2026-10-26
---

# Integrationsabnahme

Die Nutzerfreigabe umfasst auch die Uebernahme bisher fremder Aenderungen. Die Lieferung erfolgt aus der geprueften Ansicht `artifacts/migration-repair-source`; der gemeinsame Baum enthaelt auch aeltere Fassungen bereits veroeffentlichter Reparaturen. Fehlende Dateien der partiellen Ansicht und entpackte LFS-Bilder sind keine neuen Loeschungen oder Bildaenderungen.

## Nachgewiesen

- 59 gemeinsame Studio-Vertraege bestanden: Entity-Projektion, kanonische Stammbindungen, Detail-Lesevertraege, OpenAPI-Methodenabgleich und Runtime-Gates. Transporttests mit MockTransport pruefen Kanalparitaet, keine PostgreSQL-Persistenz.
- 75 reine Workspace-/Inbox-/Fachaktions-/Dispositionsvalidierungsvertraege bestanden. Die lesenden MCP-Katalogwerkzeuge sind ueber den bestehenden Dispatcher angebunden; bestehende schreibende Finanzadapter wurden nicht aus aelteren Rootkopien uebernommen.
- 48 weitere Inbox-/Agrar-Vertraege bestanden; die Inbox-HTTP-Persistenzfaelle verwenden den vorhandenen PostgreSQL-Pruefstand valeo_probe, eigene Datensaetze und Cleanup. Status vorher: Revision loading_stop_fk_20261023. Keine neue Datenbank, Container oder Ruecksetzung.
- Die separate API-Tranche bestand15 Tests, darunter3 PostgreSQL-Faelle. Abschlusschecklisten verarbeiten JSONB korrekt und verwenden verifizierten Mandantenkontext; der Negativfall fremde Rolle bleibt403. Die Zusatzpruefung aller noch offenen API-WIP-Dateien laeuft.
- Audit-Parser korrigiert und veroeffentlicht:19 Regressionen,11Advisories/12Versionsbefunde korrekt gezaehlt. Neue ungepruefte Paketbefunde bleiben blockiert. Paket-/Lockreparaturen sind als separater Auftrag fuer Claude abgegrenzt.

## Noch keine Freigabe

Die neue Dispositions-Schreibanbindung ist nicht abgenommen und wird nicht als produktive Mutation gemountet. Die Tafel bleibt bis zur serverautoritativen Fach-/Rechte-/Versions-/Freigabepruefung lesend beziehungsweise Vorschau. Schema-Deklarationen sind keine Benutzerrechte. Der bestehende Tourenweg bleibt erhalten.

DMS-Webhook und beide vorhandenen Inboxadapter erhalten gemeinsame Tenant-/Rollenpruefungen und ehrliche Createantworten. Ein blosses processed ohne Domainbeleg ist kein Erfolg. Gleiche externe Dokumentnummern duerfen keine fremde Zeile ueberschreiben. Die Sicherheits-/PostgreSQL-Abnahme ist mit vier echten Tenantfaellen bestanden; der Parser-/Transportnachlauf mit50Faellen und die Queue-/Routervertraege mit29Faellen ebenfalls. Siehe inbox-integration-followup-20261026.md.

Portal-Zertifikatsdetails, Anlage-Neuerfassung, weitere fachlich ausgeduennte Masken und die verbleibenden Erreichbarkeitsbefunde sind durch diese Lieferung nicht pauschal geschlossen. Browser-/Gesamt-CI-Abnahme bleibt getrennt; keine Gateabsenkung oder Testloeschung.

## Integrationsnachlauf: Inbox und Abhaengigkeiten

Sicherheitsmerge11d47f9f6 und Abhaengigkeitsvertrag8aaaacbcf sind im bestehenden Integrationszweig gepusht. Frontend-Typpruefung und21 Tests der vier fokussierten Suiten bestanden. Der frische strikte Produktionsaudit blockiert keine ungeprueften Befunde; die bestehende node-forge-Frist bleibt unveraendert. Siehe workspace-dependency-contract-20261025.md.

Neue Inbox-Handlerabnahme:6 Tests bestanden mit synthetischem, durch den echten Python-Queuebuilder erzeugtem Serververtrag. Positiv: frischer prepare und Maskenoeffnung ohne Buchung/processed/Scheinerfolg. Negativ: fremde ID, booking_allowed, fehlende Oeffnungsfreigabe, unbekannte Dokumentart; Loeschen nur nach Bestaetigung. Diese noch uncommittete UI-/API-Tranche muss zusammen mit ihren Quellen und generierten Vertragsartefakten geliefert werden, nicht als isolierter gruener Testcommit.

Abschlusschecklisten-Nachlauf ist inzwischen mit9b4308339 geliefert: verifizierte Urheber und vier registrierte, mandantengebundene Pruefungen; gespeicherte SQL-Texte werden nicht ausgefuehrt.20kombinierteVertraege bestanden. NachUebernahme der neuen Claude-Datenbank-Governance zusaetzlich neun kritische Inbox-/Checklistenfaelle ohneSkip gruen, auf bestehender valeo_probe ohneDDL/Reset. Siehe closing-validation-security-20261025.md.

## Stand nach Claude-Handshakes 2026-10-26

Bereits gemergte PR45-51 auf9e7d33a03 sind mit3d0cde657 konfliktfrei in die private Arbeitsansicht uebernommen und gepusht. Acht Drizzleketten sind geliefert, getrennte DB-Rollen und Migrationsverbindung bleiben erhalten; keine Ruecknahme der entfernten Laufzeit-DDL. Offene PR52/53 sind nur gelesen und nicht als integriert behauptet.

Aktuelle API-Nachabnahme77/77 ohneSkip; Lieferumfang und vier PostgreSQL-Faelle im studio-api-contracts-closure-20261025.md.3261OpenAPI-Pfade und149Aktionsrechte aus produktiver main:app neu erzeugt, Zusammenfuehrung der Artefakte laeuft. Ein fehlender JS-YAML-Testimport ist im Frontendmanifest/Lockfile gebunden und frozen offline ohneDownloads/Scripts installiert; keine Versionsaenderung bestehenderPakete. Backportfristen unveraendert.

Frontend: zusaetzlich147Batch11/12-Inventar-/Mountfaelle und Fixtureparitaet bestanden.142Inventarzeilen sind statischeNachweise, nicht142neueBedienabnahmen. Zwei echte gerouteteMounts pruefen gemeinsameRuntime/Renderer. WeitereUIX-Suiten werden auf realeBedienvertraege migriert. LokalerVollrun ohneEndbericht beendet, keineGesamtabnahme.272Erreichbarkeitsbefunde bleiben sichtbar;71fachlicheLegacydateien werden ohneFunktionsabnahme nichtgeloescht.
