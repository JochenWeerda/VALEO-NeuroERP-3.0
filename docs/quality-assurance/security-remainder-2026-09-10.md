---
title: Verbleibende Security-Befunde
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-10
version: 1.0.0
description: CPython-Backports und weitere Dependency-Befunde mit Abnahmenachweis.
---

# Verbleibende Security-Befunde

## CPython 3.13.15

Vier Verhaltensregressionen reproduzieren im unveraenderten offiziellen
Image alle vier CVEs (17 fehlgeschlagene Teilpruefungen). Kein Netzwerkziel
wird angesprochen; ZIP-Proben sind auf 4 MiB begrenzt.

- CVE-2025-15367: POP3-Steuerzeichen vor dem Schreiben ablehnen.
- CVE-2026-15806: HTTP-Zugangsdaten an das URL-Schema binden.
- CVE-2026-17084: IDNA-2003 mit Unicode-3.2-Zuordnung verarbeiten.
- CVE-2026-15310: BZIP2/LZMA pro ZIP-Lesezugriff begrenzen.

Die Quellkorrekturen liegen unter `config/security/cpython-3.13.15/` samt
PSF-Lizenz und `provenance.json` (Hersteller-Commit, Status und SHA256).
Der ZIP-Backport ist upstream noch offen; die anderen Quellen sind gemerged.
Es werden nur die betroffenen Bibliotheksdateien gepatcht. Der Builder
verlangt exakt 3.13.15 und wendet Patches ohne Fuzz an. Beide Image-Stages
pruefen das Verhalten. Eine Python-Aktualisierung muss die Backports erneut
bewerten und darf diese Pruefung nicht umgehen.

Die letzte Grype-Ausnahme wurde entfernt. Die echte Python-Versionsnummer
bleibt erhalten: versionsbasierte Restmeldungen sind dadurch weiterhin
sichtbar und gelten nicht allein aufgrund eines gruenen Gates als behoben.
Build bestanden, alle vier Tests auch im Runtime-Stage gruen; Imports von
fastapi, uvicorn, sqlalchemy, alembic, pydantic und app.main bestanden.
Trivy vollstaendig: 244 Meldungen (5 Critical, 55 High, 97 Medium, 86 Low,
1 Unknown), keine High/Critical mit verfuegbarem Fix. Dies ist ausdruecklich
kein Null-Befund-Nachweis. Die Critical-Meldungen betreffen Debian sqlite,
perl-base und zlib; ein stabiler Trixie-Vergleich ist in Arbeit.
Grype-Nachmessung laeuft noch.

## Weitere Befunde

GitHub-Export vom 2026-09-10: 95 offene Dependabot-Meldungen. Viele betreffen
mehrere Manifeste oder archivierte Lockfiles. Fuer ChromaDB und image-size
meldet die Advisory-API keinen gepatchten Release. Die weiteren Pakete
werden anhand ihrer konkreten Versionsgrenzen in Folgewellen aktualisiert;
dieser Slice ist deshalb noch nicht abgeschlossen.
