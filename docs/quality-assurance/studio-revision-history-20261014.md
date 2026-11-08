---
title: Atomare unveraenderliche Studio-Revisionshistorie
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-14
---

# Studio-Revisionshistorie

Speichern und Statuswechsel fuegen in derselben SQL-Transaktion einen Eintrag in domain_shared.screen_definition_history ein. Er enthaelt die Aktion, den geprueften Subject des HTTP-Aufrufers (interne Verwaltungswege uebergeben ihren eigenen Actor), Mandant, Entwurfs-ID, vorherige/neue Revision und den vollstaendigen gespeicherten Stand. Ein fehlgeschlagener Historieneintrag rollt die Zustandsaenderung zurueck. Der explizite Testspeicher bildet denselben Ereignisvertrag ab.

PostgreSQL-Trigger verweigern UPDATE, DELETE und TRUNCATE der Historientabelle. Fremdschluessel mit Loeschkaskaden zum veraenderlichen Entwurf/Mandanten fehlen bewusst: Die Aufzeichnung bleibt beim spaeteren Entfernen von Entwicklungsentwuerfen erhalten. Das ist keine Unveraenderlichkeitsgarantie gegen einen privilegierten Datenbankadministrator, der Tabellen oder Trigger entfernen darf.

GET /api/v1/studio/drafts/{id}/history prueft Anmeldung und aktuellen Mandanten. Fremde Entwuerfe ergeben 404; der Speicher filtert Historie nach Mandant und Entwurf. Pagination verwendet skip und limit (1 bis 500), has_more und next_skip. Der Index tenant_id/draft_id/recorded_at/id unterstuetzt diesen Zugriff.

Migration studio_history_20261014 nach control_findings_20261013 auf dem vorhandenen valeo_probe und valeo_neuro_erp angewandt; ein Alembic-Head. Additive Tabelle, Index und Trigger, keine Datenbank/Container angelegt, kein Reset. Vorherige Ereignisse werden nicht erfunden oder rueckwirkend als gepruefte Freigaben dargestellt; die Historie beginnt mit den neuen Schreibvorgaengen.

Abnahme: 115 Studio-/Pilotfaelle bestanden; nach abschliessender Pagination sechs betroffene API-/SQL-Faelle erneut geprueft. Neue Vertrage belegen Inhalts-/Urheber-/Revisionskette, Fremdmandant ohne Historie, SQL-Sperre von UPDATE/DELETE/TRUNCATE, Rollback bei Auditfehler und Erhalt vorheriger Definitionen. SQL-Fixtures verwenden aeussere Transaktionen mit Session-Savepoints und rollen eigene Ereignisse zurueck, statt unveraenderliche Historienzeilen zu loeschen.

Architektur: C4- und Containerchecks bestanden (direkte package.json-Skripte, nachdem pnpm im Sandbox-Runtimecache EPERM meldete). Architekturindex-/Strict-Driftcheck bleibt lokal rot: Aeltere fremde erzeugte Quellinventare wuerden zahlreiche bereits committete Services/Endpunkte aus dem Index entfernen. Keine blinde Regeneration oder Ueberschreibung. Die Source-Mappings sind vollstaendig; eine saubere Inventar-Synchronisierung bleibt offen.

Offen bleiben Idempotenz samt Wiederholung nach unklarem Commit-Ergebnis, getrennte Agenten-/Korrelationsidentitaet und Historienanzeige in der Maske. Keine Freischaltung schreibender MCP-Tools. Produktionsfreigabe, Prozessvariantensimulation und reale Browserabnahme bleiben Teil des Gesamtziels.
