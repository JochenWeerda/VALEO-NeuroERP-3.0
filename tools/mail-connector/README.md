# VALEO NeuroERP — E-Mail-Connector

Pollt ein IMAP-Postfach und meldet jede neue Mail an das ERP
(`POST /api/v1/crm/kim/mail-capture`). Daraus wird automatisch ein Kontakt in der
KIM-Kontakthistorie; nicht zuordenbare Mails landen in der **Klärfall-Inbox**
(`/crm/kim/capture-inbox`).

**Abhängigkeitsfrei** — nur Python-Standardbibliothek (`imaplib`, `email`,
`urllib`). Läuft ohne `pip install` auf jedem Python-3.8+-Host.

## Schnellstart

```bash
# Dauerbetrieb: Posteingang + Gesendet-Ordner, alle 60 s
python mail_connector.py \
  --host imap.example.de --user crm@example.de --password '***' \
  --sent 'Sent' --own crm@example.de \
  --api-base http://erp-server:8000 --token dev-token

# Einmal-Lauf für Cron / Windows-Aufgabenplanung (nur neue Mails seit letztem Lauf):
python mail_connector.py --once
```

## Konfiguration (ENV oder CLI; CLI hat Vorrang)

| ENV | CLI | Default | Bedeutung |
|---|---|---|---|
| `IMAP_HOST` | `--host` | — | IMAP-Server (imap.gmail.com, outlook.office365.com, …) |
| `IMAP_PORT` | `--port` | 993 | IMAP-SSL-Port |
| `IMAP_USER` | `--user` | — | Postfach / E-Mail-Adresse |
| `IMAP_PASSWORD` | `--password` | — | Passwort bzw. **App-Passwort** (Gmail/M365) |
| `IMAP_INBOX` | `--inbox` | INBOX | Posteingang-Ordner |
| `IMAP_SENT` | `--sent` | — | Gesendet-Ordner (leer = ausgehende Mails ignorieren) |
| `MAIL_OWN_ADDRESSES` | `--own` | — | eigene Adressen (kommagetrennt) → Richtungserkennung |
| `POLL_SECONDS` | `--poll-seconds` | 60 | Poll-Intervall |
| `VALEO_API_BASE` | `--api-base` | http://localhost:8000 | ERP-Basis-URL |
| `VALEO_API_TOKEN` | `--token` | dev-token | Bearer-Token |
| `VALEO_TENANT_ID` | `--tenant` | 0000…0001 | X-Tenant-ID |
| `STATE_FILE` | `--state-file` | `.mail_connector_state.json` | merkt die letzte IMAP-UID je Ordner |

## Idempotenz

Die `Message-ID` jeder Mail wird als `verweis` übergeben — das ERP legt keinen
Doppelkontakt an. Zusätzlich speichert der Connector die zuletzt verarbeitete
IMAP-UID je Ordner (State-Datei), sodass nur neue Mails geholt werden.

## Alternative: OSS-Webhooks statt Poller

Derselbe ERP-Endpoint nimmt auch geparste Webhooks entgegen — wer schon eine
freie Mail-Bridge betreibt, braucht diesen Poller nicht:

- **[ewildgoose/imap-api](https://github.com/ewildgoose/imap-api)** / **EmailEngine** — IMAP→REST/Webhook, Webhook-URL auf `…/crm/kim/mail-capture` setzen.
- **[MXHook](https://mxhook.dev/)** — eingehender SMTP → strukturiertes JSON-Webhook (Apache-2.0).
- **[mjl-/mox](https://github.com/mjl-/mox)** — vollständiger Mailserver mit HTTP/JSON-Webhooks.

Das ERP akzeptiert sowohl Einzelfelder (`fromAddr`/`toAddr`/`subject`/`text`/
`messageId`/`direction`) als auch eine rohe RFC822-Mail im Feld `raw`.
