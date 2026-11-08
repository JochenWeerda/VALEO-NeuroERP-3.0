---
title: Controller-Rechteprojektion in Belegmasken
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-13
---

# Controller-Rechteprojektion in Belegmasken

Der vom Auftraggeber gemeldete fehlende UI-Vertrag wurde ausgefuehrt und ergaenzt: screen-permissions.test.ts, 14 Faelle bestanden. Beide vorhandenen Rollen controller und CONTROLLING erhalten an der Eingangsrechnungsmaske die deklarierten Rechte belege.freigeben und belege.freigeben_erhoeht. Weder Bearbeiten, Ausstellen, Buchen noch Stornieren entsteht daraus. Transportscopes belege:write/admin:all erweitern diese Domainrechte nicht.

Zusammen mit der vorhandenen Rolle FINANCE_LESEN kommen Lesen und Preise hinzu, weiterhin ohne Buchungsrecht. Die Projektion bleibt aus beleg_roles.py erzeugt; es wird keine zweite Rollenlogik eingefuehrt. Der Test verwendet den tatsaechlichen Frontend-Permissionsresolver und die vorhandene kanonische JSON-Projektion.

Diese Abnahme prueft die UI-Rechteentscheidung, nicht eine reale Controller-Anmeldung oder den Kontrollkorb im Browser. Der bestehenden realen Testkennung wurden keine weiteren Rollen zugeteilt. Fremde generierte Arbeitskopien von Tabellen-/Migrations-/Endpoint-Inventaren und OpenAPI wurden nicht beruehrt.
