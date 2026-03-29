# NC-H1 — WhatsApp Business API Adapter

**Lane:** NC-H (Channels + Voice)
**Prioritaet:** P3
**Status:** umgesetzt

## Kontext
WhatsApp ist der primaere Kanal fuer Landwirte und Lieferanten.
Der Adapter empfaengt Webhooks, parst Nachrichten (Text, Bilder,
interaktive Buttons) und routet sie ueber die Neuro-Core Pipeline.

## Loesung
- Webhook-Verifikation (HMAC-SHA256)
- Message-Parsing fuer alle gaengigen WhatsApp-Nachrichtentypen
- Consent-Pruefung vor Pipeline-Aufruf (DSGVO)
- Guardrails-Check (Prompt Injection, PII)
- Text- und Template-Reply-Builder

## Dateien
- `app/channels/whatsapp_adapter.py` — Adapter
- `app/api/v1/endpoints/channels.py` — REST-API
