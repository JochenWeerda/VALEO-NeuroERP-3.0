---
title: Ernte-MCP-Folgeprojektion und gesperrte menschliche Aktionen
type: qa
audience: [entwickler, qa, agent]
owner: Codex
status: active
last_reviewed: 2026-10-15
version: 1.0.0
---

# Vollstaendige Karte ohne neue Agentenrechte

Nach Ergaenzung des kanonischen Aktionskatalogs meldete der GitHub-Metacheck 38794074505 die davon abhaengige MCP-Aktionskarte als veraltet. Der Generator muss den aktuellen Katalog mit 106 Aktionen verwenden.

Alle acht COMMAND_PATHS der nativen Erntekontrolle sind bereits forbiddenForAgents. Die kuratierte Karte uebernimmt diese eine Commandliste und klassifiziert die acht Wege ausdruecklich als blocked_human_only mit mcp_tool_id=null. Auch Bindung, Messbestaetigung und Widerruf sind erfasst, die eine generische Regex allein nicht vollstaendig als Mutation erkennt. Es wird kein MCP-Tool angelegt oder freigeschaltet; bestehende Autorisierung und Nachweispflichten bleiben unveraendert.

Der zusammenfassende Text nennt nun die tatsaechlichen Kategoriezaehler; die alte Aussage open_high nur Zahlauf war angesichts vier bestehender gesperrter High-Wege falsch. Diese vier bestehenden Eintraege werden nicht umklassifiziert oder verborgen.

Ergebnis: 74 betrachtete Aktionen, 59 Mutationen, acht blocked_human_only; weiterhin vier open_high, null open_medium, 43 mapped und 15 local_ui. Vier bestehende/neue Kartenvertraege und Generator --check bestanden. Der nachfolgende Action-Matrix-Report besteht ebenfalls seinen kanonischen --check (38 Aktionen, 32 dokumentierte Gaps; keine Gesamtschliessung behauptet). Der kanonische Agent-Handbuch-Check bestaetigt ebenfalls alle fuenf Artefakte als aktuell. Nachweise: artifacts/harvest-mcp-tests.txt, harvest-action-matrix-check.txt und harvest-mcp-handbook-check.txt.

Generator und Folgeartefakte wurden gegen kanonische committed Quellen geprueft. Keine Fremdtestdateien oder Gatekonfigurationen geaendert. Keine Datenbank oder Dockerinstanz. Neue GitHub-Gesamtabnahme nach Push steht aus; Service-Security-ChromaDB-Review und sichere develop-Historiensynchronisierung bleiben separat offen.
