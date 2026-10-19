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

## Masken im Studio erzeugen

`python -m valeo_cli studio …` bedient dieselbe Studio-API (`/api/v1/studio`) wie die Studio-App. Vorschlag,
Pruefung, Entwurf, Uebernahme, Vier-Augen-Pruefung, Simulation und Freigabe entscheidet der Server, mit seinen
Rechten: Gestalten braucht das Belegschreibrecht; Freigeben und Zurueckziehen braucht menschliche Administration.

```bash
python -m valeo_cli studio katalog                       # Datenquellen, Kommandoaktionen, eigene Studio-Rechte
python -m valeo_cli studio vorschlag "Lieferanten mit Ort und Status" --maske tenant/lieferanten --speichern
python -m valeo_cli studio neu --maske tenant/duenger-liste --titel "Duenger" --domaene agrar     --quelle duenger --spalte artikelnummer=Nr --spalte name=Bezeichnung --aktion freigeben --speichern
python -m valeo_cli studio quellen duenger               # vorhandene Masken als Ausgangsfassung
python -m valeo_cli studio uebernehmen agrar/duenger     # bindet den angezeigten Quellhash
python -m valeo_cli studio entwuerfe
python -m valeo_cli studio zeigen <entwurf> --ausgabe maske.json     # Revision merken, Datei bearbeiten
python -m valeo_cli studio pruefen maske.json            # ohne zu speichern
python -m valeo_cli studio speichern maske.json --entwurf <entwurf> --revision <revision>
python -m valeo_cli studio pruefung <entwurf>            # Vier-Augen-Pruefung
python -m valeo_cli studio simulieren <entwurf>
python -m valeo_cli studio freigeben <entwurf> --revision <gepruefte revision>
python -m valeo_cli studio historie <entwurf>
```

- **Verlorene Aenderungen:** Aendern und Freigeben verlangen die gesehene Revision. Eine veraltete Revision
  lehnt der Server mit 409 ab (Exit-Code 1). Pruefung, Simulation und Rueckzug nehmen ohne `--revision` die
  aktuelle Revision.
- **Wiederholung:** Jeder schreibende Aufruf traegt einen neuen Wiederholungsschluessel. `--idempotenz`
  wiederholt einen Aufruf mit demselben Schluessel.
- **Kennung:** `--maske tenant/<kennung>` setzt die Maskenkennung und zieht die eigene Adapterbindung mit. Ob die
  Kennung zulaessig und frei ist, entscheidet der Server.
- **Gezielt zusammensetzen:** `neu` baut eine Arbeitsliste nur aus Datenquelle und Kommandoaktionen des
  Server-Katalogs (`studio katalog --json`); Gefahrenstufe und Agentensperre kommen unveraendert aus dem Katalog,
  Spalten sind nur lesbar. Freie Adressen oder eigene Aktionen gibt es nicht. `vorschlag` dagegen kennt heute nur
  vier feste Vorlagen (Kunden, Offene Posten, Artikel, sonst Lieferanten) und beachtet die Absicht kaum.
- **Dateien:** `speichern` und `pruefen` nehmen eine reine Definition oder die Ausgabe von `zeigen` bzw.
  `vorschlag`; `-` liest von stdin.

Eine freigegebene Studio-Maske liefert `GET /api/v1/masks/{kennung}/screen-definition` mandantengenau aus. Ihre
Aktionen sind damit sofort ueber `aktionen`, `zeigen` und `ausfuehren` bedienbar.

Jede Studio-Maske ist per CLI und MCP bedienbar, soweit es ihre Katalogaktionen sind. Das
Masken-Studio-Inventar prueft jede Katalogaktion auf echte Route, CLI-Zugang und ausfuehrbare MCP-Abbildung
und jede Katalogquelle auf eine echte Route (Ratsche `studio_katalog_nicht_bedienbar`).

Grenze des Servers: Die Freigabe verlangt eine bestandene Simulation. Das einzige Simulationsprofil
`grain.v1` deckt nur die Getreidekette (Domaene `agrar`) ab. Andere Masken lassen sich anlegen, pruefen und
zur Pruefung geben, aber noch nicht freigeben. Freigabefaehig sind im Profil nur lesende Agrar-Masken (ohne
Aktionen, bearbeitbare Felder, Regeln, eingebettete Transporte). Die Simulation braucht den Pruefstand
`valeo_probe` ueber `TEST_DATABASE_URL`; ohne ihn scheitert sie mit `simulation_probe_not_configured`.

## Belege (DocFlow)

Die Aktionen der Belegfamilie (`beleg/*`) laufen ueber den versionierten Adapter `docflow.v1`, den
`valeo_cli.docflow` Regel fuer Regel wie `docflow-command-adapter.ts` nachbaut. Die CLI laedt den Belegzustand
aus derselben Quelle wie die Maske (`/api/v1/belege/{art}/{id}/kopf`):

- Ausgefuehrt wird nur, was der Server dort erlaubt (`aktionen[].erlaubt`) und was `enabledWhen` freigibt.
- Die Belegversion schuetzt vor verlorenen Aenderungen; `--version` bindet an die gesehene Version.
- Nur die zulaessigen Felder je Kommando werden gesendet. Stornieren verlangt `--grund` (3 bis 300 Zeichen).
- Freigaben binden an die Freigabekennung des Servers.
- Eine schreibfreie Vorschau gibt es nur beim Umwandeln (`--modus dryRun`).
- Agenten schreiben hier nie. Die Antwort wird gegen den Aufrufvertrag geprueft.

```bash
python -m valeo_cli aktionen beleg/purchase-invoice
python -m valeo_cli ausfuehren beleg/purchase-invoice umwandeln:purchase_credit_memo --id <beleg> --modus dryRun
python -m valeo_cli ausfuehren beleg/purchase-invoice buchen --id <beleg> --version 3
python -m valeo_cli ausfuehren beleg/sales-invoice stornieren --id <beleg> --grund "Doppelt erfasst" --ja
python -m valeo_cli ausfuehren beleg/sales-order bearbeiten --id <beleg> --daten entwurf.json
```

Gesperrter Zustand, veraltete Version oder fehlende Bindung: Exit-Code 1, nichts gesendet.

## Was die CLI (noch) nicht ausfuehrt

Was nicht so ausgefuehrt werden kann wie in der Maske, weist die CLI mit Grund ab:

- **Ernte-Regelsteuerung** (`harvest.control.v1`): Ihr Adapter braucht die ausgewaehlte Regelversion aus der
  Maske und ist noch nicht nachgebaut.
- **Eingabeflüsse** (`inputFlow`, Formular nur fuer Menschen in der Maske).
- **Aktionen ohne Kommando-Endpunkt**, die die Seite selbst verdrahtet.

`config/cli_mask_commands.json` fuehrt, welche Maskenaktionen die CLI ausfuehren kann. Das Register erzeugt
`scripts/generate_cli_mask_commands.py` aus derselben Funktion (`valeo_cli.support.support`), mit der die CLI zur
Laufzeit entscheidet; `tests/test_valeo_cli.py` prueft, dass es aktuell ist. Das Masken-Studio-Inventar
(`scripts/mask_studio_inventory.py`) liest es fuer seine Ratsche: Jede neue serverwirksame Maskenaktion muss per
CLI ausfuehrbar sein.
