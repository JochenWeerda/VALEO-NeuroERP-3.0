---
title: Eingrenzbare Datenrechte fuer den Pruefstand
status: aktiv
last_reviewed: 2026-11-14
owner: Codex
---

# Datenrechte ohne Rollenprovisionierung

`provision_db_roles.py --data-only --schemas <schema...> --data-roles <rolle...>`
zeigt standardmaessig einen Plan. `--anwenden` fuehrt diesen aus; zusammen mit
`--rollback` wird er innerhalb derselben Transaktion zurueckgenommen. Die
Auswahl ist explizit und nur `valeo_app`, `valeo_agent`, `valeo_system` sind
zulaessig. Reservierte und fehlende Schemas, fehlende Rollen, leere und doppelte
Auswahlen werden abgelehnt. Schema- und Rollenexistenz werden im PostgreSQL-
Katalog geprueft. `--eigentum` und `--waage-only` sind nicht kombinierbar.

Die vier Regeln fuer Schema-USAGE, DML auf bestehenden Tabellen, Sequenzen und
Funktionsausfuehrung kommen aus derselben Funktion wie bei der bisherigen
Vollprovisionierung. Der begrenzte Weg aendert keine Rollen, Kennwoerter,
Mitgliedschaften, Eigentuemer oder Default Privileges und vergibt kein CREATE
oder GRANT OPTION. Der Aufruf benoetigt die jeweiligen vorhandenen PostgreSQL-
Berechtigungen; PostgreSQL entscheidet ueber die moegliche Rechtevergabe. Nach Grants prueft der Modus im aktuellen Katalog jedes einzelne benoetigte
Recht fuer jede ausgewaehlte Rolle und jedes bestehende Objekt; bei fehlendem
Recht wird die Transaktion hart abgebrochen und zurueckgerollt. Nach der Rechtevergabe wird der Katalog innerhalb derselben Transaktion
erneut gelesen; alle Einzelrechte werden vor Commit geprueft. Dies
sperrt keine parallel danach angelegten Objekte. Der Modus aendert keine bestehende Rechtepolitik und stellt keine
RLS-Abnahme dar. Neue Objekte erhalten durch diesen Modus keine automatischen
Default-Rechte.

Gezielt ohne PostgreSQL geprueft: 30 bestehende und neue Rollenplan-/CLI-Tests
bestanden (4,47 s), inklusive Dry-run, Commit, Rollback, verbotene Kombinationen,
reservierte/fehlende Schema- und Rollenangaben und Vollplanparitaet. Eine
pyreadline-Aufraeumwarnung trat nach erfolgreichem Lauf auf. Keine Verbindung
zu einer Datenbank, keine Container, keine echte PostgreSQL-/RLS-Abnahme.

Nachtrag: 33 Unit-/CLI-Tests bestanden (2,35 s), darunter fehlendes Einzelrecht
mit Rollback und ohne Commit sowie erfolgreiche Pruefung im Rollbackmodus.
Im begrenzten Modus wird PGAPPNAME respektiert. Keine echte Datenbankpruefung.


## Reale Rollback-Abnahme 15.11.2026

Lead hat auf dem vorhandenen valeo_probe sowohl den reinen Plan als auch
`--anwenden --rollback` fuer domain_docflow/domain_shared und ausschliesslich
valeo_agent ausgefuehrt. Beide endeten erfolgreich; der reale Katalog-
Nachbedingungscheck wurde dabei ausgefuehrt. Vorher/nachher verglichene
Tabellen- und Schema-ACLs, Eigentum, RLS und Rollenflags waren identisch.
Keine neue Datenbank und keine bleibende Rechtevergabe. Die dauerhaft
geplante Vergabe war zuvor von der automatischen Freigabepruefung abgelehnt
worden und wurde nicht ausgefuehrt.

Die wiederverwendbare Grant-Factory prueft DATA_ROLES auch bei direktem
Aufruf. Der finale gemeinsame Lead-Lauf der Consumer-, Rechte- und
Improvement-Vertraege bestand mit 82 Faellen (ueberlappend zu Agentenlaeufen).
