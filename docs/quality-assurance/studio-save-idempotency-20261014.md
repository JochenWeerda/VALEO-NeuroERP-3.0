---
title: Idempotentes Anlegen und Bearbeiten von Studio-Entwuerfen
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-14
---

# Studio-Speicher-Idempotenz

POST /studio/drafts und PUT /studio/drafts/{id} verlangen nun UUID-idempotency_key. PUT verlangt weiter expected_revision. Das vorhandene unveraenderliche Historienereignis speichert das atomare Ergebnis unter dieser UUID. Ein Replay bestaetigt Mandant, Actor, create/update, Entwurfs-ID (bei update), Ausgangsrevision und die vollstaendige JSON-Definition. Vergleich ist kanonisch und typgetreu (Bool/Wert werden nicht gleichgesetzt). Ein anderer Auftrag mit demselben Schluessel ergibt Konflikt ohne Aenderung.

SQL-Speichern verwendet einen transaktionalen PostgreSQL-Advisory-Lock fuer die UUID vor Ergebnislookup und Zeilensperre. Dadurch sind auch zwei CREATE-Auftraege mit gleicher UUID serialisiert, bevor ein Entwurfsdatensatz existiert. Der normale Mandanten-/Versionsschutz und Unique-Screen-Vertrag bleiben aktiv. Der explizite Testspeicher benutzt denselben Replayvertrag unter seinem bestehenden Lock. Interne administrative Aufrufe koennen ohne UUID weiterarbeiten; sie sind keine freigeschalteten Agenten-Commands.

Der Browser hasht den tatsaechlich serialisierten JSON-Inhalt mit SHA-256 und sprachunabhaengiger Schluesselsortierung. Aktion, Ziel, Ausgangsrevision und Inhaltsfingerprint bestimmen den stabilen UUID-Schluessel im bestehenden Sessionstorage/Prozesscache. Inhalte, Tokens, E-Mail oder Benutzerkennung werden darin nicht abgelegt. Aenderungen des Inhalts bekommen einen anderen Schluessel. Historische Replayantworten ersetzen keinen Abruf des aktuellen Entwurfs.

Abnahme: 125 Python-/SQL-Faelle und elf Frontendfaelle bestanden. Nach Ergaenzung des unabhaengigen DB-Lockvertrags elf betroffene Save-/Statusfaelle erneut bestanden; nach finaler Fingerprintnormalisierung drei Transportfaelle erneut gruen. Neue Tests pruefen Create- und Update-Replay ohne Doppelhistorie, geaenderten Inhalt/Actor sowie simulierten verlorenen Rueckgabewert nach SQL-Session.commit. Zwei eigene Datenbankverbindungen belegen blockierte und nach Rollback freigegebene UUID-Sperre, ohne Fachdatensaetze anzulegen. Dies ist keine Lastabnahme zweier gleichzeitig laufender HTTP-Clients. Der vorhandene gemeinsame valeo_probe wird verwendet; SQL-Historienfixtures rollen eigene Datensaetze zurueck.

Keine Migration oder neue Datenbank erforderlich. MCP-Schreibadapter werden nicht freigeschaltet. Offen bleiben getrennte Agenten-/Korrelationsattribute, maskenseitige Historie, vollstaendige Prozessvariantensimulation und echte Browserabnahme. Der bekannte Architekturdrift aus fremden aelteren Quellinventaren bleibt separat offen. Auch die erzeugten API-Artefakte muessen mit den verschärften HTTP-Vertraegen koordiniert synchronisiert werden; fremde alte Arbeitskopien wurden nicht blind ueberschrieben.
