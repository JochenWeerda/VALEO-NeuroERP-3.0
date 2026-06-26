# ELSTER UStVA Integration

Vollständiges Prozedere zur Umsatzsteuer-Voranmeldung mit ELSTER-konformem Export.
Referenz: JuryOberst/Elster (GitHub), offizielle ELSTER-Dokumentation.

## Ablauf

1. **Berechnen** – UStVA aus Sachkonten (Steuerschlüssel mit UStVA-Position)
2. **Export** – ELSTER-konforme XML (Schema Anmeldungssteuern v2023, ISO-8859-15)
3. **Übermittlung** – manueller Upload bei Mein ELSTER

## Technische Komponenten

- ELSTER XML-Builder: `app/elster/ustva_xml.py`
- VAT Return API: `app/api/v1/endpoints/vat_return_export.py`
- Frontend: `packages/frontend-web/src/pages/fibu/elster-online.tsx`

## API

- POST /api/v1/finance/vat-return/calculate
- GET /api/v1/finance/vat-return
- GET /api/v1/finance/vat-return/{id}/elster-xml

## ELSTER-Kennziffern

Kz35/Kz36 (Umsätze 19%/7%), Kz66 (Vorsteuer), Kz81/Kz86, Kz83 (Zahllast).

## Schema

Namespace: finkonsens.de/elster/elsteranmeldung/ustva/v2023, Encoding ISO-8859-15.
