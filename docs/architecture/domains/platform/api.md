---
title: Platform — Identitaets-API
type: reference
audience: [architect, entwickler, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-12
description: Geschuetzte Sessionwege und gemeinsame Ausfuehrungsidentitaet.
---

# Identitaets-API

| Weg | Berechtigung und Wirkung |
| --- | --- |
| `GET /api/v1/identity/session` | Gepruefte eigene Sitzung; Subjekt, ERP-Mandant und konfigurierte Grenzen |
| `POST /api/v1/identity/session/logout` | Widerruft die eigene gebundene Sitzung einschliesslich erneuerter Token |
| `POST /api/v1/identity/subjects/revoke` | Mandantenadministration; widerruft bisherige Sitzungen eines Subjekts im eigenen Mandanten |

Alle Wege verwenden dieselbe Provider- und Mandantenpruefung. Der Rumpf des
administrativen Widerrufs benennt nur das Zielsubjekt; der Urheber kommt aus dem
geprueften Token. Widerrufe und ihre Urheber werden im gemeinsamen Speicher
atomar protokolliert. Ein Widerruf erzeugt kein Verbot kuenftiger Neuanmeldungen;
Benutzerabschaltung ist ein anderer Vertrag.

`identity_context` traegt die verifizierte Identitaet auch durch interne Aufrufe
und Arbeits-Threads und entfernt sie beim Ende der Anfrage. Das Modul ist kein
Ersatz fuer Mandate, Fachrechte oder Objektpruefungen. Die Agenten- und
Ressourcenvertraege werden daran angebunden und separat abgenommen.
