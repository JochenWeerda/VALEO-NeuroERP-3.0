# NC-H2 — Email Channel

**Lane:** NC-H (Channels + Voice)
**Prioritaet:** P3
**Status:** umgesetzt

## Kontext
E-Mail ist der formale Kommunikationskanal fuer Geschaeftspartner.
Der Channel parst eingehende E-Mails, extrahiert den Intent-relevanten
Text (ohne Zitat-Bloecke) und routet ihn ueber die Pipeline.

## Loesung
- E-Mail-Parsing mit Prioritaets-Erkennung (dringend, wichtig, normal)
- Zitat-Bereinigung (entfernt > und Von:-Bloecke)
- Subject + Body-Kombination fuer Intent-Erkennung
- Thread-Tracking via In-Reply-To
- Reply-Builder mit korrektem Re:-Prefix

## Dateien
- `app/channels/email_channel.py` — Channel
- `app/api/v1/endpoints/channels.py` — REST-API
