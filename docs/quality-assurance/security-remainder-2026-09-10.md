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
Grype-Nachmessung vom 2026-09-10 abgeschlossen (lokales Artefakt
`artifacts/security-remainder-grype.json`, Grype 0.115.0): 243 Meldungen,
davon 10 Critical, 59 High, 78 Medium, 9 Low, 63 Negligible und 24 Unknown.
Keine High/Critical-Meldung hat im damaligen Scan den Fixstatus `fixed`.
Scan-Ziel war `valeo-backend:security-remainder`, Image-ID
`sha256:78c68efa4be9ffaf1624a79ae40c3321c2c0f84ce27152e60740bd2ead5a8c26`.
Das ist historische Evidenz und kein aktueller Scan des lokalen latest-Tags.

Der gespeicherte Trixie-Baseline-Scan umfasst 170 Meldungen (7 Critical,
58 High), ebenfalls keine High/Critical mit Fixstatus `fixed`. Er betrifft
nur das Python-Basisimage, nicht das vollstaendige Backend; die Gesamtzahlen
sind deshalb kein belastbarer Vorher-/Nachher-Vergleich fuer einen Wechsel.

## Weitere Befunde

GitHub-Export vom 2026-09-10: 95 offene Dependabot-Meldungen. Viele betreffen
mehrere Manifeste oder archivierte Lockfiles. Fuer ChromaDB und image-size
meldet die Advisory-API keinen gepatchten Release. Die weiteren Pakete
werden anhand ihrer konkreten Versionsgrenzen in Folgewellen aktualisiert;
dieser Slice ist deshalb noch nicht abgeschlossen.

## Wiederaufnahme 2026-09-13

- Eingecheckter Ausgangsstand: `8e1f84a01`. Uncommittierte Aenderungen des
  Cursor-Slices RESTFEHLER-20260911 wurden nicht in den Build aufgenommen.
- Isolierter Build aus den benoetigten Git-Archivpfaden erfolgreich;
  Tag `valeo-backend-security:resume-20260913`, Manifest-Index
  `sha256:054c342fc329f7938b8e19b898c001e4271d44751dd00d359bd22d5d717d833f`.
- Vier Patch-Pruefsummen gegen `provenance.json` bestaetigt. Negativkontrolle
  mit unveraendertem Python 3.13.15 Bookworm: 17 Teilfehler, Exit 1.
  Nach Backports im Builder und Runtime-Stage jeweils 4/4 Tests bestanden.
- Offline-Import von fastapi, uvicorn, sqlalchemy, alembic, pydantic und
  app.main bestanden; Python 3.13.15, uid 1000, kein importierbares pip.
  `app.main` ist die Test-Kompatibilitaetsschicht; zusaetzliche Abnahme des
  Produktionsmoduls `main` ebenfalls bestanden: 3949 Routen registriert,
  uid 1000, kein pip. Kein Lifespan-/DB-/HTTP-End-to-End-Nachweis.
- Vorhandenes lokales `valeo-neuro-erp-backend:latest` stammt vom
  2026-09-10 04:06:59 UTC, ID `8fc6deae9769`; es enthaelt den Pruefer noch
  nicht. Kein Retagging, Neustart oder Deployment dieses bestehenden Images.

Aktuelle Grype-Nachmessung: Exit 0, Grype 0.115.0, Datenbank vom
2026-09-13 06:31:42 UTC (valid), lokales Vollartefakt
`artifacts/security-resume-grype-20260913.json`. 245 Meldungen:
10 Critical, 59 High, 80 Medium, 9 Low, 63 Negligible und 24 Unknown.
Keine High/Critical-Meldung hat Fixstatus `fixed`; der ungefilterte Scan
ist ausdruecklich kein Nachweis fuer Befundfreiheit. Kein neuer Trivy-Lauf.

Gegenueber dem historischen Grype-Scan hinzugekommen: CVE-2026-89092
je einmal fuer libc-bin und libc6 2.36-9+deb12u14, Medium, laut Scanner
`not-fixed` und ohne Fixversion. Die vier gepatchten CPython-Befunde bleiben
versionsbasiert sichtbar. Keine neuen Ausnahmen oder gelockerten Gates.
Naechster Schritt: offene Dependency-Welle mit Cursor abstimmen und
separaten Trivy-/GitHub-Nachweis erbringen; der Gesamtslice bleibt in Arbeit.


## Fortsetzung 2026-09-14

### Trivy-Abnahme

Scan desselben isolierten Backend-Images `valeo-backend-security:resume-20260913`
abgeschlossen, lokales Artefakt `artifacts/security-resume-trivy-20260914.json`.
Der erste Lauf erreichte beim Analysieren das Standard-Zeitlimit; der zweite
Lauf mit `--timeout 15m` und persistentem Scanner-Cache endete mit Exit 0.
Ungefiltertes Ergebnis: **246 Befunde** (5 Critical, 55 High, 99 Medium,
86 Low, 1 Unknown). Keine High/Critical-Meldung nennt eine Fixversion.
Das ist eine lokale Image-Abnahme, kein neuer GitHub-Workflow-Nachweis.

### CRM Communication: STARTTLS-Patch

`services/crm-communication/requirements.txt`: aiosmtplib **5.1.1 -> 5.1.2**.
Herstellerbezug: [GHSA-vxj7-4xrp-5vr4 / CVE-2026-55558](https://github.com/cole/aiosmtplib/security/advisories/GHSA-vxj7-4xrp-5vr4).
Der Patch verwirft vor dem TLS-Wechsel gepufferte Klartextantworten.

`scripts/verify_aiosmtplib_security.py` prueft zwei Vertraege gegen einen
lokalen SMTP-Server mit echtem TLS, generiertem Testzertifikat und aktiver
Zertifikatspruefung. Keine externen Verbindungen, keine Mailzustellung.
Unter Python 3.11 im Container mit `--network none`:

- 5.1.1: normaler STARTTLS-Wechsel bestanden, Injection-Test fehlgeschlagen
  (`injected-plaintext` statt `authenticated-tls-reply`), Exit 1.
- 5.1.2: beide Tests bestanden, Exit 0.

Reproduktion: gewuenschte aiosmtplib-Version isoliert installieren, dann
`python scripts/verify_aiosmtplib_security.py` ausfuehren; OpenSSL wird fuer
kurzlebige lokale Testzertifikate benoetigt. Die vollstaendige Dienst-
Abhaengigkeitsaufloesung mit Python 3.11 bestanden: 50 Pakete,
aiosmtplib 5.1.2, pip --dry-run --ignore-installed Exit 0. Bericht:
`artifacts/crm-communication-resolve-20260914.json`. Kein neuer Dienst-Build.

Grenze: Der aktuelle `/emails/send`-Endpunkt legt einen DB-Datensatz an,
enthaelt aber noch TODOs fuer Queue, Anhaenge und Templates. Dieser Patch
schliesst die Paketluecke und implementiert keinen produktiven Mailversand.

### Abgleich mit GitHub

Lesender Export am 2026-09-14: weiterhin 51 offene Dependabot-Meldungen,
keine auf Archivpfaden (`artifacts/security-dependabot-20260914.jsonl`).
Der lokale SMTP-Patch ist noch kein geschlossener GitHub-Alert. Andere
Dependency-Fixes bleiben offen; services/ai, cryptography und image-size
bleiben bei Cursor. Keine neuen Ausnahmen oder abgeschwaechten Gates.
