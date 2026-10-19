---
title: VALEO-CLI
type: reference
audience: [entwickler, betrieb, agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-19
version: 0.1.0
description: Kommandozeile fuer Maskenaktionen — derselbe Kommandoweg wie Maske und MCP, Anmeldung per Device-Flow.
---

# VALEO-CLI

Die CLI bedient Maskenaktionen von der Kommandozeile. Sie ist ein reiner Client: Den Aktionsvertrag liest sie
aus der ScreenDefinition des Servers (`GET /api/v1/masks/{maske}/screen-definition`). Sie ruft denselben
Kommando-Endpunkt mit demselben Umschlag wie die Maske (`useActionRuntime`). Rechte, Mandant, Validierung,
Audit und Idempotenz bleiben beim Server. Eine Fachaktion, mehrere Zugaenge: Maske, MCP, CLI, REST.

## Anmelden

```bash
python -m valeo_cli anmelden          # zeigt Adresse und Code, oeffnet den Browser
python -m valeo_cli status            # Benutzer, Mandant, Identitaetsart, Restlaufzeit
python -m valeo_cli abmelden          # beendet die Sitzung auch beim Identity Provider
```

Die Anmeldung laeuft ueber den OAuth Device Authorization Grant (RFC 8628) am Keycloak-Client
`valeo-neuro-erp-cli`. Die Person meldet sich im Browser an, mit SSO, MFA oder Passkey. Die CLI sieht nie ein
Passwort und hat kein eigenes Dienstkonto. Die Sitzung liegt unter `%APPDATA%\valeo\cli-sitzung.json` bzw.
`~/.config/valeo/cli-sitzung.json` und ist nur fuer den Eigentuemer lesbar. Der Realm rotiert Refresh-Tokens; die
CLI schreibt jede Erneuerung sofort zurueck. Eine widerrufene Sitzung wird geloescht.

Fuer Automatisierung kann ein anderweitig ausgestelltes Token in `VALEO_ACCESS_TOKEN` stehen. Traegt es nicht
`identity_type=human`, gilt der Aufrufer als Agent. Dann sind Aktionen mit `forbiddenForAgents` oder
`humanApprovalRequired` gesperrt, wie in der Maske.

| Variable | Vorgabe |
|---|---|
| `VALEO_API_URL` | `http://localhost:8000` |
| `VALEO_OIDC_ISSUER` | `http://localhost:8080/realms/valeo-neuro-erp` |
| `VALEO_CLI_CLIENT_ID` | `valeo-neuro-erp-cli` |
| `VALEO_CLI_SESSION` | Sitzungsdatei, siehe oben |
| `VALEO_ACCESS_TOKEN` | Token fuer Automatisierung; hat Vorrang vor der Sitzung |

Den Client legt `scripts/provision_identity_provider.py` an, wenn er im Realm fehlt. Erlaubt ist nur ein
oeffentlicher Client mit Device-Grant: kein Browser-, Passwort- oder Dienstfluss, keine Weiterleitungsadressen.
Audience und Belegscopes erhaelt er wie jeder ERP-Client.

## Aktionen

```bash
python -m valeo_cli aktionen admin/postfaecher
python -m valeo_cli zeigen admin/postfaecher testen
python -m valeo_cli ausfuehren admin/postfaecher testen --id 42 --feld empfaenger=pruef@example.invalid
python -m valeo_cli ausfuehren admin/identity-budgets allocate --daten eingabe.json --grund "Pilot" --modus dryRun
```

- `--modus` ist einer von `execute` (Vorgabe), `dryRun`, `validate` oder `propose`.
- Vor jedem Aufruf prueft die CLI Pflichtfelder, Feldtypen und Auswahlwerte aus `inputFields`.
- Verlangt die Aktion eine Bestaetigung, fragt die CLI nach. Ohne Terminal gilt die Rueckfrage als abgelehnt; dann
  braucht es `--ja`.
- Verlangt die Aktion eine Begruendung (`auditReasonRequired`), braucht es `--grund`.
- `--idempotenz SCHLUESSEL` gibt den Wiederholungsschluessel mit. Wie die Maske sendet die CLI ihn nur auf
  ausdruecklichen Wunsch.

Exit-Codes: 0 erfolgreich, 1 fachlich abgelehnt oder nicht per CLI ausfuehrbar, 2 Bedienfehler, 3 Anmeldung oder
Rechte, 4 Server oder Netz.

## Was die CLI (noch) nicht ausfuehrt

Was nicht so ausgefuehrt werden kann wie in der Maske, weist die CLI mit Grund ab:

- **Command-Adapter** (`commandBinding`), d. h. die Belegfamilie (`docflow.v1`) und die Ernte-Regelsteuerung
  (`harvest.control.v1`). Die Maske baut deren Aufruf mit Version, Freigabekennung und Entwurfskontext. Das folgt
  als eigener Meilenstein.
- **Eingabeflüsse** (`inputFlow`, Formular nur fuer Menschen in der Maske).
- **Aktionen ohne Kommando-Endpunkt**, die die Seite selbst verdrahtet.

`config/cli_mask_commands.json` fuehrt, welche Maskenaktionen die CLI ausfuehren kann. Das Register erzeugt
`scripts/generate_cli_mask_commands.py` aus derselben Funktion (`valeo_cli.support.support`), mit der die CLI zur
Laufzeit entscheidet; `tests/test_valeo_cli.py` prueft, dass es aktuell ist. Das Masken-Studio-Inventar
(`scripts/mask_studio_inventory.py`) liest es fuer seine Ratsche: Jede neue serverwirksame Maskenaktion muss per
CLI ausfuehrbar sein.
