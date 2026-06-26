# Slack App Install

**Zweck:** Vereinfachte Slack-Anbindung fuer VALEO NeuroERP per importierbarem App-Manifest statt manueller Einzelkonfiguration.

## Aktueller Integrationsstand

- Inbound Events: `POST /api/v1/channels/slack/events`
- Signaturpruefung: `CHANNEL_SLACK_SIGNING_SECRET`
- Thread-Antworten in Slack: `CHANNEL_SLACK_BOT_TOKEN`
- Unterstuetzter Einstieg: `app_mention`

## Schnellstart

1. Oeffentliche Basis-URL fuer das Backend bereitstellen, z. B. ueber `ngrok`.
2. Manifest rendern:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\render-slack-manifest.ps1 `
  -BaseUrl https://deine-url.example `
  -AppName "VALEO NeuroERP"
```

3. Die erzeugte Datei `dist/slack-app-manifest.generated.yaml` in Slack importieren:
   `api.slack.com/apps` -> `Create New App` -> `From an app manifest`
4. App im Workspace installieren.
5. In Slack unter `Basic Information` den `Signing Secret` kopieren.
6. In Slack unter `OAuth & Permissions` den `Bot User OAuth Token` kopieren.
7. Beide Werte in `.env` setzen:

```env
CHANNEL_SLACK_SIGNING_SECRET=...
CHANNEL_SLACK_BOT_TOKEN=xoxb-...
```

8. Backend neu starten.
9. Bot in den Ziel-Channel einladen:

```text
/invite @VALEO NeuroERP
```

10. Testen:

```text
@VALEO NeuroERP oidc login
```

## Localhost-Variante

Wenn dein Backend lokal auf Port `8000` laeuft, kannst du den Tunnel und das Manifest direkt erzeugen:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-slack-localhost.ps1 -Port 8000
```

Das Skript:

- startet `localtunnel`
- ermittelt die oeffentliche HTTPS-URL
- rendert direkt `dist/slack-app-manifest.generated.yaml`

Danach nur noch:

1. `dist/slack-app-manifest.generated.yaml` in Slack importieren
2. App installieren
3. `Signing Secret` und `Bot Token` in `.env` uebernehmen
4. Backend neu starten

Zum Stoppen des Tunnels:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop-slack-localhost.ps1
```

## Was das Manifest aktuell setzt

- Bot User
- Event Subscriptions
- `app_mention`
- Bot-Scopes:
  - `app_mentions:read`
  - `chat:write`

## Grenzen des aktuellen Setups

- Noch kein Slack-OAuth-Installflow im Backend
- Noch keine Slash Commands
- Noch keine Interactivity/Buttons fuer Freigaben
- Installation bleibt einmalig Slack-adminseitig bestaetigungspflichtig

## Relevante Dateien

- [channel_work_surfaces.py](c:/Users/Jochen/VALEO-NeuroERP-3.0/app/api/v1/endpoints/channel_work_surfaces.py)
- [channel_ingress.py](c:/Users/Jochen/VALEO-NeuroERP-3.0/app/core/channel_ingress.py)
- [config.py](c:/Users/Jochen/VALEO-NeuroERP-3.0/app/core/config.py)
- [slack-app-manifest.template.yaml](c:/Users/Jochen/VALEO-NeuroERP-3.0/config/slack/slack-app-manifest.template.yaml)
- [render-slack-manifest.ps1](c:/Users/Jochen/VALEO-NeuroERP-3.0/scripts/render-slack-manifest.ps1)
- [start-slack-localhost.ps1](c:/Users/Jochen/VALEO-NeuroERP-3.0/scripts/start-slack-localhost.ps1)
- [stop-slack-localhost.ps1](c:/Users/Jochen/VALEO-NeuroERP-3.0/scripts/stop-slack-localhost.ps1)
