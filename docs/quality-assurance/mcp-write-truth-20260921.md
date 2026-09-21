---
title: MCP-Ausfuehrung ohne Scheinerfolg
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-21
description: Korrigierte AI-MCP-Platzhalter und verbleibender Schreibadapter-Aufwand.
---

# MCP-Ausfuehrung: Lieferstand und Grenzen

Der AI-Dienst meldete fuer `create_procurement_order` immer
`PO-2025-001` mit Status `created`, ohne einen Fachprozess aufzurufen.
`query_database` und `search_documents` lieferten erfundene leere Ergebnisse.
Diese drei Handler liefern jetzt keine Erfolgsergebnisse mehr. Der Katalog
kennzeichnet sie mit `available: false`; Aufrufe antworten mit HTTP 501.
Unbekannte Tools liefern HTTP 404. Unerwartete Fehler geben keine internen
Exception-Texte mehr an den Aufrufer weiter.

## Nachweis

`python -m pytest tests/test_ai_mcp_truth.py --noconftest -q --override-ini addopts=''`

9 Tests bestanden. Abgedeckt sind Katalog, direkte Handler-Ausfuehrung,
HTTP-Aufruf aller drei nicht angeschlossenen Tools, unbekannte Tools sowie
ein tatsaechlich angeschlossener Test-Handler. Keine Datenbankmutation.
Testumgebung meldet eine Starlette/httpx-Deprecation-Warnung.

## Noch umzusetzen

Dieser Defekt-Fix ist Voraussetzung, kein Ersatz fuer produktives MCP-Write.
Der echte Adapter muss anhand des Masken-/Aktionsvertrags Authentifizierung,
Tenant-Scope, Agent-Verbote, Fachvalidierung, Freigabe, Idempotenz und Audit
bis zur nachweisbaren Fachpersistenz durchlaufen. Ein Eintrag im YAML-Katalog
oder eine `mutation`-Antwort allein belegt kein Speichern.

Getrennte Ist-Staende: Root-Registry mit 18 Tools, ein weiterer veralteter
Katalog unter `app/config` und der AI-Dienst mit eigenen Handlern. Sie bilden
aktuell keinen gemeinsamen ausfuehrbaren Masken-Schreibvertrag.
Die AI-Resource-Provider enthalten weiterhin Platzhalter und sind ebenfalls
noch nicht als produktive Datenquellen abgenommen.

UIX bleibt insgesamt offen: FSX/KIM-Seitenabnahme, Integration der vorhandenen
Kartenstapel sowie MCP-Schreibadapter. Die parallele native Einkaufsmaske
und ihre zwei Speicher werden durch diesen Fix nicht veraendert.

Architektur-Impact: Minor, Defektkorrektur vorhandener Handler; keine neue
Route, kein neuer Container, keine Datenmigration. Ruecknahme per Slice-Revert.
