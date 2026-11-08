---
title: qs Sicherheitskorrektur 2026-10-27
type: reference
audience: [entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Exakte Upstreamkorrektur und Verhaltenstest fuer qs Komma-Serialisierung.
---

# qs Sicherheitskorrektur

Quality Gate 40560803213 meldete GHSA-6pq8-jhm2-2vcw fuer qs6.16.0.
[Upstream](https://github.com/ljharb/qs/security/advisories/GHSA-6pq8-jhm2-2vcw)
behebt den Fehler ab6.16.1. Das vorhandene globale Override wird auf exakt
6.16.1 gesetzt. Die gepinnte pnpm9.12.0 erzeugt den Lockfile ohne Installation
in bestehende Modulverzeichnisse. Nur qs Override, Aufloesung, Integritaet
und die elf Verbraucherreferenzen aendern sich; keine fremden Paketupdates.
Ein erster Entwurf mit pnpm10 wurde verworfen, nicht geliefert.

## Nachweis

Vier Verhaltenstests aus dem Upstreamfix pruefen nicht aufrufbares toString,
Null-Prototypen, verschachtelte Komma-Arrays, encodeValuesOnly und normale
Serialisierung samt expliziter Benutzerfehler. Gegen6.16.0: drei rot, einer
gruen. Gegen6.16.1: vier gruen, keine Skips. Das getrennt bezogene Paketarchiv
stimmt mit der SHA512-Integritaet im Lockfile ueberein.

Der permanente Test scripts/verify_qs_security_release.cjs laeuft im
bestehenden Backport-Audit-Gate mit. Der Gate entfernt einen etwaigen
SECURITY_QS_RUNTIME-Override vor seiner Pruefung der installierten Version.
Lokale Gegenproben nutzen explizite Paketpfade, keine Installation anderer
Worktrees wird veraendert.

pnpm9 audit des neuen Lockfiles: kein qs-Befund; genau ein bekannter hoher
node-forge-Befund. Audit Exit1 wird deshalb nicht als Gesamtgruen dargestellt.
Patchbytes der vorhandenen Backports sind gegen HEAD und ihre bisherigen
Hashes geprueft; nur Manifest-/Lockbindungen werden erneuert. Pruefdaten und
Frist28.10.2026 bleiben unveraendert. Frischer CI-Gesamtlauf steht aus.
Keine Datenbank, Container, Live-Aktivierung oder Browserabnahme.
