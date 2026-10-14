---
title: Idempotente Studio-Statusauftraege
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-14
---

# Studio-Status-Idempotenz

submit-review, publish und retire verlangen neben expected_revision einen UUID-idempotency_key. Die UUID wird als ID des atomar geschriebenen Historieneintrags verwendet; kein zweites Ergebnisregister oder eine neue Tabelle entsteht. Das gespeicherte Ergebnis ist dessen unveraenderlicher Snapshot. Eine Wiederholung muss Mandant, Actor, Entwurf, Zielaktion und Ausgangsrevision exakt bestaetigen. Anderer Inhalt/Kontext mit demselben Schluessel ergibt 409.

Die HTTP-Anmeldung und (bei Publikation/Retirement) menschliche Adminrolle werden vor jedem Replay geprueft. Publikationsreplay durchlaeuft weiterhin den aktuellen Metadatenkatalog. Ein Replay aendert weder aktuellen Entwurf noch Historie; es liefert den historischen Ausgang des urspruenglichen Auftrags, auch wenn der Entwurf spaeter weitergegangen ist. Es ersetzt keinen aktuellen Einzelabruf.

Der SQL-Statusweg sperrt den Entwurf, prueft ein bereits gespeichertes Ergebnis vor dem Snapshotvergleich und schreibt neuen Status und Historienergebnis gemeinsam. Eine globale UUID-Kollision beim Insert wird mit Rollback als 409 behandelt. Der Browser verwendet je Aktion/Entwurf/Revision denselben Schluessel aus Sessionstorage, mit Prozesscache bei nicht verfuegbarem Browserstorage; ohne Browserstorage bleibt Reload-Wiederholung begrenzt. Es werden keine Kennungen, E-Mails, Tokens oder Entwurfsinhalte in diesem Schluesselspeicher abgelegt (nur Aktionsname, opaque Entwurfs-ID, Revisionshash und UUID).

Abnahme: 119 Python-/SQL-Faelle und zehn Vitest-Faelle bestanden; nach Ergaenzung des Kollisions-Rollbackvertrags neun betroffene Replay-/Historienfaelle erneut bestanden. Neue Tests pruefen drei Statusreplays ohne Doppelhistorie, geaenderten Actor/Aktion/Revision, entzogene Publikationsrolle und einen simulierten verlorenen Rueckgabewert nach Session.commit. SQL-Kollision wird bei erzwungenem Cache-Miss geprueft und darf den Status nicht veraendern. Dies ist keine Netzunterbrechungs-/Lastabnahme zweier gleichzeitig laufender PostgreSQL-Clients. Der gemeinsame valeo_probe und dessen rollbackisolierte Historienfixtures werden wiederverwendet.

Offen: Create-/Update-Idempotenz, getrennte Agenten-/Korrelationsattribute, Historienanzeige, Produktivfreigabe und Prozessvariantensimulation. Bei einem Anmeldewechsel im selben Browser bleibt ein Schluessel an die urspruengliche serverseitige Identitaet gebunden; eine andere Person bekommt Konflikt statt deren Antwort. Schreibende MCP-Funktionen bleiben deaktiviert. Kein DB-/Container-Neubau oder Migrationsschritt in diesem Slice. Der bekannte Architekturdrift aus aelteren fremden Quellinventaren ist unveraendert separat offen.
