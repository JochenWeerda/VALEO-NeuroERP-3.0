---
title: Kanonische Belegrechte im Maskenruntime
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-13
version: 1.0.0
description: Generierte Belegrechte fuer den zentralen Frontend-Permission-Resolver.
---

# Belegrechte im zentralen Maskenruntime

## Lieferung

Voraussetzung fuer BELEG-020 Teil 2. Der gemeinsame getScreenPermissions-Resolver
kennt jetzt belege.lesen/preise/bearbeiten/ausstellen/buchen/stornieren je Belegart.
Die Rollen stammen ausschliesslich aus app/auth/beleg_roles.py (rollen_fuer), nicht
aus einer von Hand gepflegten TypeScript-Matrix. scripts/generate_beleg_permission_projection.py
schreibt runtime/beleg-permissions.generated.json; --check und der neue Pytest-
Driftvertrag machen veraltete Projektionen sichtbar.

Die Projektion bezieht sich auf die kanonischen Screen-IDs beleg/<belegart> mit
Bindestrichen. Unbekannte Belegarten und Rechte werden abgewiesen. Transport-Scopes
belege:read/write oder admin:all allein gewaehrleisten keine Beleg-Fachaktion; Rollen
werden nach demselben Belegarten-/Aktionsvertrag wie im Backend projiziert. Der
Server bleibt fuer Datensatz, Mandant, Zustand, Freigaben und Ausfuehrung autoritativ.
Andere Screen-Permission-Vertraege bleiben erhalten.

## Nachweise

Zehn Vitest-Faelle bestanden, einschliesslich vorhandener Plattform-/CRM-/Logistik-
Vertraege und vier neuer Belegfaelle: Einkauf vs. Verkauf, Lagerleser ohne Preise,
Finanzstorno vs. Einkauf/Manager, keine Rechte aus Schema/Transport-Scopes und kein
unbekannter Beleg trotz Adminrolle. Generator-Driftcheck gruen; neuer CI-Driftvertrag
gegen die vollstaendige kanonische Projektion. Keine Fachtests auf einer Datenbank,
keine neue DB oder Dockerinstanz und keine weitere Identitaets-Rollenvergabe.

## Weiter offen

Die neun Belegvarianten sind weiterhin nicht in der zentralen Registry aktiviert.
BELEG-020 Teil 2 erfordert Registry/Route/Inventare, vollstaendige Meridian-Metadaten,
Zustands-/Aktionsbindung, Command-Eingaben und echte Maskensichtpruefung. Dieser Slice
belegt die Permission-Projektion, keine Belegmasken-/Schreibabnahme. Die vorhandene
Einkaufs-Testkennung und ihre genehmigte Referenzmandantenbindung bleiben erhalten.
