# KIM Auto-Capture — automatische Kontakt-Erfassung (2026-06-09)

Ziel: ein-/ausgehende Kommunikation (Telefon mit Transkript, E-Mail, WhatsApp/Futterbestellungen)
wird **automatisch** als Kontakt in der KIM-Kontakthistorie (`public.kunden_kontakte`) angelegt,
damit nichts Wesentliches verloren geht. Auto-erfasste Einträge tragen `bediener='AUTO'` und
zeigen im Journal ein **„Auto"-Badge**.

## Universeller Eingang (Backend)

`POST /api/v1/crm/kim/auto-capture`
```jsonc
{
  "channel": "telefon" | "email" | "whatsapp" | "persoenlich" | "brief" | "fax",
  "direction": "incoming" | "outgoing",
  "peer": "+49 4941 71729" | "kunde@example.de",   // Gegenseite (für Auflösung)
  "content": "<Transkript / Mailtext / WhatsApp-Text>",
  "kundenNr": "1280227",   // optional; überspringt die Auflösung
  "betreff": "...",        // optional; sonst LLM-Betreff
  "verweis": "call-4711"   // externe ID → Idempotenz (kein Doppel-Eintrag)
}
```
Ablauf: **Kunde auflösen** (explizite `kundenNr` → sonst Telefon-Tail-Match `kunden.tel` bzw.
E-Mail-Match `kunden.email`) → **Zusammenfassung** via LLM-Gateway (Betreff + 1–3 Sätze; mit
deterministischem Fallback ohne LLM) → **Kontakt anlegen** (`art`, `richtung`, `kurzinfo`=Betreff,
`notiz`=Zusammenfassung/Volltext, `bediener='AUTO'`, `verweis`).

Antwort-Status: `created` · `duplicate` (verweis schon vorhanden) · `unresolved` (kein Kunde
auflösbar — Caller kann in eine Inbox/Klärfall routen, statt still zu verlieren).

Service: `app/services/crm_auto_capture_service.py` · Endpoint: `app/api/v1/endpoints/crm_auto_capture.py`.

## Channel-Anbindung (Connectoren)

| Channel | Auslöser | Anbindung |
|---|---|---|
| **WhatsApp** | Eingehende Nachricht / Futterbestellung | `whatsapp_intake_service` legt Bestell-Inbox **und** bereits `kunden_kontakte` an; für freie Nachrichten zusätzlich `auto-capture` aufrufen. |
| **Telefon** | Anruf-Ende mit Transkript | TAPI-Bridge (`tools/tapi-bridge`) meldet Calls (`/crm/tapi/incoming`, `/dial`). Für Auto-Kontakt: nach Anrufende Transkript (STT) an `auto-capture` posten (`channel:'telefon'`, `verweis:<call-id>`). STT/Recording ist externe Telefonie-Integration. |
| **E-Mail** | Ein-/ausgehende Mail mit Kundenbezug | Mail-Connector (IMAP/Graph/SMTP-Journaling) postet Betreff+Text an `auto-capture` (`channel:'email'`, `peer:<absender/empfänger>`, `verweis:<message-id>`). |

## Frontend
Auto-erfasste Kontakte erscheinen **ohne weitere Arbeit** im KIM-Journal (`ContactHistoryTable`,
Tab „Übersicht/Historie") — Quelle ist dieselbe `kunden_kontakte`-Tabelle. Operator `AUTO` → „Auto"-Badge.

## Offen / Folge-Slices
- TAPI-Transkript-Posting (benötigt Recording+STT in der Telefonie-Schicht).
- Mail-Connector (IMAP/Graph) als eigener Worker.
- Optionaler Klärfall-Inbox für `unresolved` (analog WhatsApp-Intake-Inbox).
