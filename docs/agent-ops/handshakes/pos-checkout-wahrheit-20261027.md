---
title: Handshake POS-CHECKOUT-WAHRHEIT-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Uebergabe Claude -> Codex fuer den Offline-Abgleich und die Retoure der Kasse ueber den Fiskalisierungsdienst.
---

# Handshake POS-CHECKOUT-WAHRHEIT-20261027 (Claude Code -> Codex)

## Basis

- `origin/main`, Zweig `claude/pos-checkout-wahrheit-20261027`. Unabhaengig von der RLS-Kette. Keine Migration.

## Fuer dich

1. **Live-relevant:** `POST /pos/checkout` und `POST /pos/retoure` verlangen eine konfigurierte Fiskalisierung des
   Mandanten (`/pos/fiscalization/config`), sonst 503. Vorher meldeten beide Erfolg ohne Signatur.
2. **API-Vertrag:** `/pos/retoure` verlangt `vorgang_id` (Idempotenz), `tenant_id` im Rumpf entfaellt. `/pos/checkout`
   ist typisiert (`CheckoutRequest`), Antwort `CheckoutResponse`. OpenAPI nur fuer diese zwei Pfade.
3. **Frontend:** `terminal.tsx` (nur Offline-Einreihung: Rabatt, Steuersatz, UUID-Kennung), `retoure.tsx`
   (Vorgangskennung), `pos-offline-queue.ts` (Typ). Keine Masken-/Studio-Bindung beruehrt.
4. **Provider:** `FiskalyProvider._receipt_payload` wirft bei einem Satz ohne DSFinV-K-Zuordnung, statt ihn als
   Normalsatz zu signieren. Das betrifft auch den Online-Verkauf.
5. **Offen (QA-Dokument):** Kassenverkauf ohne Bestands-/FiBu-Buchung, Geschaeftstag nachtraeglich signierter Bons,
   abgebrochene TSE-Transaktionen.
6. Nicht beruehrt: Codex-Claims, Studio/Masken, Systemrollen, Live.
