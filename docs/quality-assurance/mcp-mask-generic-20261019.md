# Generische MCP-Werkzeuge fuer Maskenaktionen (MCP-MASK-GENERIC-20261019)

## Ergebnis

Zwei MCP-Werkzeuge statt eines handgebauten Adapters je Aktion:

- `mask.actions.list` (Scope `masks:read`) liest die Aktionen einer Maske aus derselben mandantengenauen
  ScreenDefinition wie Maske und CLI und nennt je Aktion, ob ein Agent sie ausfuehren darf und warum nicht.
- `mask.action.execute` (Scope `masks:write`) ruft den deklarierten Kommando-Endpunkt mit dem Bearer-Token des
  Aufrufers und dem Umschlag der Maske (`_mode`, `_auditReason`, `_idempotencyKey`). Rechte, Mandant, Audit und
  Wiederholungsschutz prueft der Ziel-Endpunkt. Gesperrt: `forbiddenForAgents`, `humanApprovalRequired`,
  Command-Adapter (Belege, Ernte-Steuerung), Eingabefluesse der Maske, Aktionen ohne Endpunkt. Identitaetsfelder
  und Umschlagfelder im Input werden abgewiesen. Die Regel ist paritaetisch zu `valeo_cli.support` (Test).

Die Scopes stehen im administrativ gepflegten Attribut `erp_scopes`; ein Agent bekommt sie nur ausdruecklich.

## Befund und Korrektur: Agentengrenze der Spezialwerkzeuge

Sieben schreibende Spezialwerkzeuge fuehrten Maskenaktionen aus, die die Maske Menschen vorbehaelt, ohne
`identity_type` zu pruefen: Ration freigeben/aktivieren/zurueckziehen/archivieren (`agrar.ration.transition`),
Fahrzeug loeschen, Futteranalyse freigeben, Lagerbewegung stornieren. Ein Agent mit Fach-Scope konnte damit
menschliche Genehmigungen ersetzen. `execute_mcp_tool` prueft jetzt zentral und datengetrieben aus
`config/mcp_mask_action_map.yaml` und der ScreenDefinition: Gehoert ein Werkzeugaufruf zu einer Maskenaktion
mit `humanApprovalRequired` oder `forbiddenForAgents`, verlangt `execute` `identity_type=human`; Werkzeuge mit
mehreren Zielaktionen werden ueber `action_key` eingegrenzt, sonst gilt die strengste. Vorschaumodi bleiben fuer
Agenten offen. Ausgenommen sind Werkzeuge mit eigenem deklariertem Freigabeschritt
(`human_approval_required: true`, z. B. `sales.gutschrift.buchen`: Mensch gibt frei, Agent bucht genau das).

## Befund und Korrektur: config/ fehlte im Produktions-Image

`Dockerfile.backend` kopierte `config/` nicht. Im Betrieb fehlten damit Belegvarianten, Studio-Katalog,
MCP-Werkzeugkatalog und Aktionskarte (lokal sichtbar als 500 auf `beleg/*`). Das Image kopiert jetzt `config/`
(1,3 MB).

## Nachweis

- 26 Vertraege in `tests/test_mcp_mask_actions.py` (Paritaet mit der CLI-Regel ueber alle registrierten Aktionen,
  Liste, Token-Weitergabe ohne Mandanten-Header, Umschlag, Wiederholungsschluessel, unzulaessige Aufrufe ohne
  Transport, gesperrte Aktion, fehlender Token, durchgereichte Ablehnung, 404/422/503, Scope, Agentengrenze der
  Spezialwerkzeuge, Vorschau fuer Agenten, eigener Freigabeschritt).
- Gegen `valeo_probe`: MCP-Suiten, `test_agent_tool_contracts`, `test_fuhrpark_isolation_effects`,
  `test_gutschrift_umsatzsteuer` zusammen 453 gruen (ausser den bekannten Windows-Faellen in
  `test_mcp_client_lifecycle`, `tasklist` ohne stdout). Angepasst: Zaehltest des Katalogs (62 -> 64),
  Lagerstorno-Test (Agent 403, Mensch bucht), Fuhrpark-Isolation laeuft als Mensch.
- Gates: Architekturindex, Drift, Godfile, MCP-REST-Bindungen, Kommando-Inventar, Aktionskatalog, Container-
  und Code-Inventare gruen; MCP-Referenz, Agentenhandbuch und Aktionskarte neu erzeugt (nur eigene Aenderungen).
- Echt ueber `/api/v1/mcp/tools/call` (Testkennung voruebergehend `masks:read`/`masks:write`, danach exakt
  zurueckgesetzt, Sitzungen beendet): Liste 200; Belegaktion 403 `adapter_nur_mensch`; generischer Trockenlauf
  bis zum Ziel-Endpunkt, dort 403 mangels Ernterolle; Mandant im Input abgewiesen. Nichts geschrieben.

## Stand des Inventars

Von 182 serverwirksamen Maskenaktionen: 46 mit eigenem Werkzeug, 2 generisch, 93 bewusst Menschen
vorbehalten, 41 ohne Kommando-Endpunkt (nur Frontend-Kommando) und damit weder per CLI noch per MCP
erreichbar. Diese 41 brauchen je Maske einen deklarierten Endpunkt oder die Einstufung als reine
Oberflaechenaktion.
