# Portal OpenAPI Summary Gate 2026-06-26

## Zweck

Das Quality Gate verlangt `summary=` fuer alle FastAPI-Routen. Die Portal- und
WhatsApp-Routen waren fachlich vorhanden, aber 16 Route-Dekoratoren hatten noch
keine explizite OpenAPI-Zusammenfassung.

## Umfang

- `portal_intelligence.py`: 5 Empfehlungs- und Generierungsrouten.
- `portal_lohndienst.py`: 4 Lohndienst-Auftragsrouten.
- `portal_innendienst.py`: 3 Innendienst-Auswertungsrouten.
- `portal_interessent.py`: 2 Interessenten-Detail-/Statusrouten.
- `whatsapp_webhook.py`: 2 produktive Webhook-Routen.

## Ergebnis

Es wurden ausschliesslich `summary=`-Metadaten nachgetragen. Fachlogik,
Response-Modelle, Persistenz und Pfade bleiben unveraendert.

## Verifikation

- `python scripts/check_openapi_docs.py --threshold 0`
