---
title: Handlebars-Herstellerkorrektur fuer drei neue Sicherheitsbefunde
type: qa
audience: [entwickler, qa, security, agent]
owner: Codex-01a0f3fc
status: active
last_reviewed: 2026-10-08
version: 1.0.0
---

# Handlebars-Herstellerkorrektur

## Befunde und Herstellerrelease

GitHub meldet am 08.10. drei weitere Befunde gegen Handlebars4.7.9:

- [GHSA-8r5x-fm3f-whwj](https://github.com/advisories/GHSA-8r5x-fm3f-whwj):
  kritisch, ungepruefte AST-Werte koennen generierten JavaScript-Code injizieren.
- [GHSA-p8wg-vrv2-v86f](https://github.com/advisories/GHSA-p8wg-vrv2-v86f):
  kritisch, Zugriff auf Function ueber eigene Constructor-Eigenschaften von Prototypen.
- [GHSA-xw65-4hp5-5hc7](https://github.com/advisories/GHSA-xw65-4hp5-5hc7):
  mittel, vorcompilierter Text kann ein eingebettetes Script-Element schliessen.

Der Hersteller nennt fuer alle drei [Release4.7.10](https://github.com/handlebars-lang/handlebars.js/releases/tag/v4.7.10).
Das offizielle npm-Paket ist verfuegbar; seine SHA512-Integritaet entspricht
exakt dem neuen Lockfile-Eintrag. Globaler Override auf exakt4.7.10;
kein lokaler Handlebars-Patch und keine Scanner-Ausnahme.

## Echte Abnahme

Die sechs neuen Runtime-Vertraege verwenden die wirklich installierte
Bibliothek. Drei normale Faelle pruefen HTML-Escaping, Blockparameter mit
AST/Precompile und sichere Eigenschaftslesung. Drei Sicherheitsfaelle
pruefen AST-Codeausfuehrung, Constructor-Zugriff und Script-Abschluss.
Nur ein harmloser lokaler Marker, kein Prozessstart oder Netzwerkzugriff.

Original4.7.9: drei Normalfaelle bestanden, alle drei Sicherheitsfaelle
gescheitert. Der AST-Fall setzt tatsaechlich den Marker; der Constructor-Fall
gibt Function zurueck; Precompile enthaelt einen rohen Script-Abschluss.
Release4.7.10: alle sechs bestanden; Vorlageninhalt und normales Rendering
bleiben korrekt.

Der bestehende CI-Einstieg laedt diese sechs Vertraege automatisch.
Zusammen mit den bisherigen 45 Vertraegen: **51 bestanden, null Fehler,
null Skips**, 34,11 Sekunden. Gefrorene Lock-Abnahme aller 36 Workspaces
bestanden; minimaler Lockdelta betrifft ausschliesslich Handlebars.
Normale Offline-Installation aus dem vorhandenen Cache, kein Force-Reinstall.

Reales Production-Audit: kein Handlebars-Befund mehr. Die zwei vorhandenen
High-Befunde bleiben im Rohbericht sichtbar; beide exakt source_backported,
null blockiert, zusaetzliche 12 echte Runtime-Vertraege im Audit-Gate bestanden.
Keine neue Severity-/Erreichbarkeitsausnahme und keine unterdrueckte Meldung.

## Bestehende Backports und weiterer Betrieb

Der komplette Manifest-/Lockdelta wurde vor der Neubindung geprueft.
Alle Patchdateien und installierten Reparaturquellen von node-forge/braces
stimmen weiterhin mit den bisherigen SHA256-Nachweisen ueberein.
Nur Manifest-/Lockhashes in `npm-backport-reviews.json` angepasst;
Reviewdatum08.10. und exklusiver Ablauf15.10. unveraendert. Keine automatische
Verlaengerung oder Neubewertung unbekannter Befunde.

Die GitHub-Versionsmeldungen koennen erst nach dessen erneutem Graph-Scan
als erledigt erscheinen. Der lokale Auditnachweis erklaert keinen kuenftigen
GitHub-Lauf vorzeitig fuer gruen. Bestehende Chroma-/weitere Upstream-Befunde
und die frische Tabellenkatalog-Abnahme bleiben eigene Nachweise.

Nachverifikation auf 3f3927045: GitHub Security Scan37825541453 vollstaendig
erfolgreich. Die offenen Dependabot-Meldungen681/682/683 fuer Handlebars
sind nach dem Graph-Neuscan geschlossen.
