# VALEO NeuroERP — TAPI-/Telefonie-Bridge

Lokaler Dienst, der eingehende Anrufe der Telefonanlage an das ERP meldet. Das
ERP löst die Rufnummer gegen den Kundenstamm auf; das Frontend zeigt automatisch
ein Anruf-Popup mit dem erkannten Kunden (Click-to-Customer).

```
Telefonanlage ──(Anruf)──▶ tapi_bridge.py ──POST /api/v1/crm/tapi/incoming──▶ ERP
                                                                               │
Frontend ◀── Popup ◀── GET /api/v1/crm/tapi/pending (Polling alle 5 s) ◀───────┘
```

## Voraussetzungen

- **Python 3.8+** auf dem Büro-PC (keine weiteren Pakete nötig — nur Standardbibliothek).
- Netzwerkzugriff vom Büro-PC auf den ERP-Server (Port 8000) **und** auf die Telefonanlage.

## Schnellstart

1. **Verbindung testen** (sendet einen Test-Anruf, ohne echte Telefonanlage):
   ```bash
   python tapi_bridge.py --source simulate --caller 049417360 \
     --api-base http://ERP-SERVER:8000 --token dev-token
   ```
   Erfolg → im ERP erscheint sofort das Anruf-Popup.

2. **FRITZ!Box-Callmonitor aktivieren** (einmalig): an einem angeschlossenen Telefon
   `#96*5*` wählen (deaktivieren: `#96*4*`).

3. **Bridge dauerhaft starten:**
   ```bash
   python tapi_bridge.py --source fritzbox --host fritz.box \
     --api-base http://ERP-SERVER:8000 --token dev-token
   ```

## Konfiguration

Alles per CLI-Argument oder Umgebungsvariable (Argument hat Vorrang):

| Argument        | Env-Variable       | Default                                   |
|-----------------|--------------------|-------------------------------------------|
| `--api-base`    | `VALEO_API_BASE`   | `http://localhost:8000`                   |
| `--token`       | `VALEO_API_TOKEN`  | `dev-token`                               |
| `--tenant`      | `VALEO_TENANT_ID`  | `00000000-0000-0000-0000-000000000001`    |
| `--host`        | `FRITZBOX_HOST`    | `fritz.box`                               |
| `--port`        | `CALLMONITOR_PORT` | `1012`                                     |

> **Produktion:** `--token` muss ein gültiges OIDC-Bearer-Token sein (der
> `API_DEV_TOKEN` ist nur für die Entwicklung). `--tenant` auf den Mandanten setzen.

## Quellen (`--source`)

- **`fritzbox`** *(Default)* — FRITZ!Box-Callmonitor (TCP 1012). De-facto-Standard
  im deutschen Mittelstand. Meldet nur eingehende, klingelnde Anrufe (`RING`).
- **`tcp-lines`** — generischer Listener: jede empfangene TCP-Zeile wird als
  Anrufer-Rufnummer behandelt. Für eigene CTI-/TSP-Adapter, die Rufnummern
  zeilenweise über einen Socket bereitstellen.
- **`simulate`** — sendet einen einzelnen Test-Anruf und beendet sich.

## Als Dienst betreiben

- **Windows:** als geplante Aufgabe „Bei Anmeldung", Aktion
  `python C:\...\tapi_bridge.py --source fritzbox ...`, Neustart bei Fehler.
  Alternativ über [NSSM](https://nssm.cc/) als echten Windows-Dienst.
- **Linux:** als `systemd`-Unit mit `Restart=always`.

Die Bridge verbindet sich bei Verbindungsabbruch automatisch neu (Backoff) und
meldet jeden Anruf nur einmal je Verbindungs-ID.
