---
title: Claude-Handshakes und Integrationsabgleich 2026-10-26
type: qa
audience: [entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-26
---

# Abgleich vor Studio-Lieferung

Neueste gemergte Quelle9e7d33a03ee9f14e5d688bfb9938c01c24607ea9 gegen gemeinsameBasis880d4f967.99Pfade auf Inhaltsabweichungen geprueft: keine Konflikte mit laufender Studio-/Inbox-Arbeit. Workboard: neuere Claude-Fassung plus unveraenderter eigener Anhang seit gemeinsamer Basis; dessen Einfuegungen und unsere Claims bleiben erhalten. Beide Eltern im Merge nachvollziehbar, kein Forcepush und keine blinde Rootkopie.

Gelesen: Drizzle-Ketten acht Pakete, Apply-Waechter, Datenbank-Governance, Rollentrennung, Laufzeit-DDL, Dienstrollen. Acht Ketten bereits upstream geliefert, hier nicht neu erzeugt. Rechte-/DDL-Aenderungen PR45-51 bleiben fuehrend. Neue Quellen enthalten keine requestseitigen Schemaaenderungen als Migrationsersatz.

Auch offene Handshakes PR52/53 gelesen: eigene Dienst-Versionstabellen und Inventory-Tabellenfuehrung durch den Dienst. Diese ungemergten PRs sind nicht Teil dieser Synchronisierung. Der gemeinsame Pruefstand wird nicht migriert oder zurueckgesetzt. Neuer Backend-Migrationshead runtime_ddl_to_migrations_20261026; bestehender valeo_probe bleibt fuer laufende isolierte Tests unveraendert. Keine lokalen Images aus veralteter Rootkopie bauen.

Nachgelagerte Studio-/Inbox-Tranche und generierte Artefakte bleiben getrennt. Keine eigene neue Gesamt-CI-Abnahme behauptet; Synchronisierung bewahrt bereits upstream abgenommene Quellen und verhindert deren Ruecknahme durch aeltere Arbeitskopien.
