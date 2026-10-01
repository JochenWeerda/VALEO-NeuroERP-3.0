---
title: Sicherheitsupdate und gepruefte Abhaengigkeiten
type: reference
audience: [agent, entwickler, qa, betrieb]
owner: Codex
status: aktiv
last_reviewed: 2026-10-01
---

# Sicherheitsupdate 2026-10-01

Claims: fc1502e67 und c1b3d765f. Acht offene GitHub-Alerts betrafen
fuenf Pakete. Root, AI und CRM-Marketing verwenden jetzt PyJWT 2.15.0;
die pnpm-Aufloesung verwendet grpc-js 1.14.5, fastify 5.12.5,
fast-uri 3.1.8 und moment 2.31.0. Der Lockfilevergleich zeigt nur diese
vier JavaScript-Paketwechsel und die zugehoerigen Snapshot-Verweise.

Primaere Advisories:
- [PyJWT](https://github.com/jpadilla/pyjwt/security/advisories/GHSA-42vr-xj54-vc7v)
- [grpc-js](https://github.com/grpc/grpc-node/security/advisories/GHSA-m9gg-hp2v-232j)
- [Fastify](https://github.com/fastify/fastify/security/advisories/GHSA-4mh8-r7rc-xpvc)
- [fast-uri](https://github.com/fastify/fast-uri/security/advisories/GHSA-hrr3-gc8f-f4qj)
- [Moment](https://github.com/moment/moment/security/advisories/GHSA-4p3w-j4w9-5jqw)

## Abnahme

- Neuer JWT-Vertrag reproduziert auf 2.14.0 den ungefangenen RecursionError.
  Mit 2.15.0 wird ein tief verschachtelter Payload als DecodeError abgewiesen.
  Zusammen mit echten OIDC/RSA-Vertraegen: 17 Tests gruen, ohne Auth-Override.
- Python-Test nutzt die isolierte Installation unter
  artifacts/security-pyjwt-215; die globale Python-Installation bleibt
  unveraendert. CI/Deployment muessen die neuen Manifestpins installieren.
- Sicherheitsgate: 18 Tests plus 14 Subtests gruen.
- Frozen pnpm-Installation erfolgreich; pnpm audit --prod: null Befunde.
- Root pip-audit: 154 Pakete, null Befunde. CRM-Marketing: 36 Pakete,
  null Befunde. Beide Aufloesungen enthalten PyJWT 2.15.0.
- AI-Service: Rohscanner meldet drei bestehende Chroma-Befunde;
  bestehendes Gate bewertet sie fuer den geprueften Embedded-Betrieb
  als not_affected und erlaubt die Freigabe. Kein Rohscan mit null Befunden.
- Drei Kalender-Frontendtests gruen (maximal zwei Worker).
  Echter Moment/ical-generator-Konsument erzeugt korrekte UTC-Start-/Endzeiten.
  Fastify-HTTP-Injection liefert 200; kein vollstaendiger Service-/Plugin-Bootnachweis.
- Ruff fuer den neuen Fehlervertrag gruen. Keine Datenbank-/Dockeranlage.

Lokale Belege: artifacts/security-npm-audit.json, security-root-audit.json,
security-crm-marketing-audit.json, security-ai-service/ai/{status,pip-audit,
dependency-decision}.json sowie security-frozen-install.log und
security-calendar-tests.log.

## Bestehende Chroma-Entscheidung

Die Evidenz war nach bb552b998 (MCP-Fehlervertraege) und adb38dda4
(voriger PyJWT-Pin) veraltet. Die Diffs wurden erneut geprueft:
kein Chroma-HTTP-Adapter hinzugefuegt; PersistentClient bleibt eingebettet.
Nur die Hashes der zwei MCP-Dateien und des AI-Manifests wurden erneuert.
Advisories, Risikobewertung und Wiedervorlage 2026-10-15 bleiben unveraendert.
Keine neue Ausnahme, keine Verlaengerung der Bewertung.

## Externe Grenzen

GitHub-Alert-Schliessung ist erst nach Integration in den Defaultbranch
und erneuter GitHub-Auswertung belegt. CI, erforderliche Branchchecks und
Deployment sind gesonderte Abnahmen; lokale Audits beweisen sie nicht.
Bekannte projektweite CI-/Godfile-/OpenAPI-Gaps bleiben sichtbar.
