# KIM Auto-Capture — Connectoren & freie OSS-Bausteine (2026-06-09)

Ergänzt [crm-kim-auto-capture-2026-06-09.md](./crm-kim-auto-capture-2026-06-09.md).
Alle drei genannten Connectoren sind fertig gebaut: **E-Mail**, **Telefon-Transkript**
und die **Klärfall-Inbox** als Sammelnetz. Jeder Kanal mündet im universellen
Eingang `POST /api/v1/crm/kim/auto-capture` → Kunde auflösen → LLM-Kurzfassung →
Kontakt (`bediener='AUTO'`). Nicht auflösbare Vorgänge landen automatisch in der
Klärfall-Inbox statt verloren zu gehen.

## 1) Klärfall-Inbox (Sammelnetz für alle Kanäle)

- DB: `public.crm_capture_inbox` (Migration `crm_capture_inbox_kim_20260609`).
- Service: `app/services/crm_capture_inbox_service.py` (add/list/assign/dismiss).
- API: `app/api/v1/endpoints/crm_capture_inbox.py`
  - `GET /crm/kim/capture-inbox?status=offen|zugeordnet|verworfen|alle`
  - `POST /crm/kim/capture-inbox/{id}/assign` `{kundenNr, resolvedBy}` → legt den Kontakt an, Status `zugeordnet`.
  - `POST /crm/kim/capture-inbox/{id}/dismiss` `{resolvedBy}` → Status `verworfen`.
- Auto-Verdrahtung: `CrmAutoCaptureService.capture()` schreibt `unresolved`-Fälle
  (inkl. LLM-Kurzfassung) in die Inbox; idempotent über `verweis`.
- Frontend: `pages/crm/klaerfall-inbox.tsx` + Hooks `lib/api/crm-capture-inbox.ts`
  + Nav „Klärfall-Inbox" (commercial.tsx). Pro Zeile Kunden-Zuordnung (Datalist
  aus `/crm/kim/customers`) oder Verwerfen, per-Entity-Pending-Guard.

## 2) E-Mail-Connector

- API: `app/api/v1/endpoints/crm_mail_capture.py` — `POST /crm/kim/mail-capture`
  nimmt **geparste Felder** (`fromAddr/toAddr/subject/text/messageId/direction/ownAddresses`)
  **oder** eine **rohe RFC822-Mail** (`raw`). Richtungserkennung über eigene
  Adressen; Idempotenz über Message-ID.
- Poller: `tools/mail-connector/mail_connector.py` (+ README) — abhängigkeitsfreier
  IMAP-Poller (stdlib `imaplib`/`email`), Posteingang + optional Gesendet,
  UID-State-Datei, `--once` für Cron. Konfig via ENV/CLI.

### Freie OSS-Alternativen (statt eigenem Poller, Webhook → `/crm/kim/mail-capture`)
- **[ewildgoose/imap-api](https://github.com/ewildgoose/imap-api)** (EmailEngine) — IMAP-Konten über REST/Webhook; Webhook-URL auf den Endpoint setzen. AGPL-3.0.
- **[MXHook](https://mxhook.dev/)** — eingehender SMTP → strukturiertes JSON-Webhook. Apache-2.0.
- **[mjl-/mox](https://github.com/mjl-/mox)** — vollständiger, wartungsarmer Mailserver mit HTTP/JSON-Webhooks.

## 3) Telefon-Transkript-Connector (mit STT)

- API: `app/api/v1/endpoints/crm_call_transcript.py` — `POST /crm/kim/call-transcript`
  nimmt `transcript` (fertiger Text) **oder** `audioUrl`/`audioBase64` (→ STT).
- STT: `app/services/stt_client.py` — anbieterunabhängig, OpenAI-kompatibel
  (`POST {STT_BASE_URL}/audio/transcriptions`). Ohne `STT_BASE_URL` funktioniert
  der reine Text-Weg; Audio-Weg meldet sauber `stt_unconfigured`.
- Telefonie: `tools/tapi-bridge/tapi_bridge.py` erweitert um `--source transcript`
  (`report_transcript`) — meldet nach Gesprächsende Text **oder** Aufnahme-URL.
  Aufruf aus dem Recording-/CTI-Hook der Telefonanlage.

### Freie OSS-Bausteine für STT (selbst gehostet, GPU/CPU)
- **[SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper)** + **[faster-whisper-server](https://github.com/kesjam/faster-whisper-server)** — OpenAI-kompatibler `/v1/audio/transcriptions`-Server. MIT.
- **[hwdsl2/docker-whisper](https://github.com/hwdsl2/docker-whisper)** — fertiges Docker-Image, OpenAI-kompatibel, mit Diarisierung.
- **[collabora/WhisperLive](https://github.com/collabora/WhisperLive)** / **[WhisperLiveKit](https://github.com/QuentinFuxa/WhisperLiveKit)** — Echtzeit-Transkription (WebSocket), falls Live-Mitschrift gewünscht.
- Aufnahme-Seite: **Asterisk/FreePBX** `MixMonitor` o. ä. liefert die WAV-Datei/URL für `audioUrl`.

### WhatsApp (bereits aktiv, hier zur Vollständigkeit)
- `whatsapp_intake_service` legt Bestell-Inbox + `kunden_kontakte` an; freie
  Nachrichten zusätzlich über `auto-capture`/`mail-capture`-Muster.
- Freie Gateways: **[WAHA](https://waha.devlike.pro/)**, **[WhiskeySockets/Baileys](https://github.com/whiskeysockets/Baileys)**, **[Evolution API](https://github.com/EvolutionAPI/evolution-api)** — Webhook → `/crm/kim/auto-capture` (`channel:'whatsapp'`).

## Admin-Maske — Connector-Konfiguration per Tenant (statt ENV)

Analog zur KI-Anbieter-Wahl konfiguriert der Administrator STT und IMAP pro
Mandant in der UI (`pages/admin-suite/connectoren.tsx`, Nav „Auto-Capture-Connectoren").
Gespeichert im JSONB `domain_shared.tenants.settings` unter `connectors` (Laufzeit-
Abruf-State unter `connectors_state`). Precedence: **Tenant-Settings > ENV** — ENV
bleibt als globaler Default/Bootstrap gültig.

- Service: `app/services/connector_config.py` (`SttConfig`/`ImapConfig`, load/save,
  `SttClient.for_tenant`), `app/services/mail_ingest_service.py` (server-seitiger IMAP-Abruf).
- API (`admin_suite.py`):
  - `GET /admin-suite/capture-connectors` — STT+IMAP, Secrets redigiert (`*_set`-Flags).
  - `PUT /admin-suite/capture-connectors` — Key/Passwort nur bei Angabe ersetzt.
  - `POST /admin-suite/capture-connectors/stt/test` — STT-Erreichbarkeit (`/models`).
  - `POST /admin-suite/capture-connectors/imap/test` — IMAP-Login-Probe.
  - `POST /admin-suite/capture-connectors/imap/poll` — „Jetzt abrufen" (server-seitig).
- Hooks: `lib/api/admin-suite.ts` (`useConnectors`/`useUpdateConnectors`/`useTestConnectorStt`/`useTestConnectorImap`/`usePollConnectorImap`).
- Der `call-transcript`-Endpoint nutzt jetzt `SttClient.for_tenant(db, tenant_id)`.
- Hinweis: Route `/admin-suite/capture-connectors` (nicht `/connectors` — letztere ist der bestehende Connector-Hub/Integrationen).

## Konfiguration (ENV) — Übersicht (Default/Fallback; UI hat Vorrang)

| Connector | Schlüssel |
|---|---|
| E-Mail-Poller | `IMAP_HOST/PORT/USER/PASSWORD`, `IMAP_INBOX/SENT`, `MAIL_OWN_ADDRESSES`, `POLL_SECONDS` |
| STT | `STT_BASE_URL`, `STT_MODEL`, `STT_API_KEY`, `STT_LANGUAGE` |
| ERP-Ziel (Tools) | `VALEO_API_BASE`, `VALEO_API_TOKEN`, `VALEO_TENANT_ID` |

## Verifiziert (2026-06-09)
- Auto-Capture unresolved (Telefon & E-Mail) → Inbox; `assign` legt Kontakt an, `dismiss` verwirft.
- `mail-capture` (geparst & roh), `call-transcript` (Text-Weg & sauberer `stt_unconfigured`-Fall).
- `tapi_bridge.py --source transcript` meldet live an `/crm/kim/call-transcript`.
- Frontend: Lint + tsc sauber für `klaerfall-inbox.tsx` / `crm-capture-inbox.ts`.
