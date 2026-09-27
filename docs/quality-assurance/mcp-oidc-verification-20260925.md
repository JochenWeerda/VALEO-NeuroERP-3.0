---
title: Kryptografische OIDC-Pruefung am MCP-Endpunkt
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-27
description: Signierte Token im realen Authentifizierungspfad und verbleibende Provider-Abnahme.
---

# Tokenpruefung

Der gemeinsame OIDC-Verifier verlangt jetzt konfigurierte Issuer und Audience
sowie die Token-Claims `exp`, `iss`, `aud` und `sub`. Ein leerer Subject wird
abgewiesen. Bisher konnte insbesondere ein Token ohne Ablaufdatum akzeptiert
werden. Signatur-, Issuer-, Audience- und Ablaufpruefung bleiben beim bestehenden
JWT-Verifier; es gibt keinen neuen Authentifizierungsweg.

## Nachweis

`python -m pytest tests/test_mcp_oidc_verification.py tests/test_mcp_execution.py --noconftest -q --override-ini addopts=''`

**31 Tests bestanden.** Der neue Test erzeugt kurzlebige RSA-Schluessel im
Speicher und signiert echte JWTs. Der MCP-HTTP-Endpunkt verwendet unveraendert
seine OIDC-Dependency. Nur Provider-Konfiguration und oeffentlicher JWKS-Cache
werden gestellt; die Datenbank ist ein Testdouble.

Geprueft: gueltiger Token erreicht dryRun; falscher Signaturschluessel,
fehlende Pflichtclaims, abgelaufener Token, falscher Issuer/Empfaenger,
zukuenftiges nbf, leerer Subject und unvollstaendige Verifier-Konfiguration
werden abgewiesen. Auch ein korrekt signierter Token erhaelt ohne Scope oder
bei abweichendem Mandanten keinen Datenbankzugriff.

## Grenzen

Dies ist keine Abnahme eines echten Identity-Provider-Logins. Discovery,
JWKS-Abruf/Rotation und die produktive Client-/Realm-Konfiguration sind separat
zu pruefen. Die Tests bestaetigen keine Kontaktpersistenz; deren PostgreSQL-
Nachweis liegt im [Adapterbericht](mcp-execution-crm-20260921.md).
Weitere Schreibadapter, vollstaendiger MCP-Transport und UIX-Gesamtabnahme
bleiben offen. Anbieter muessen die jetzt verpflichtenden Standardclaims liefern.

Architektur-Impact: bestehende Tokenvalidierung gehaertet, keine neue Route,
kein Schema und kein neuer Authentifizierungsmechanismus.
