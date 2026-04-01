# SEC-023 - Sales Credit Notes / Returns Hardening

## Ziel

Gutschriften und Retouren sollen weder freie Query-Tenants noch Payload-Tenant-Overrides akzeptieren.

## Scope

- `app/api/v1/endpoints/sales_credit_notes.py`
- `tests/test_security_sales_credit_notes.py`

## Umsetzung

- Create/List/Post/Return-Status ziehen `tenant_id` aus dem Kontext
- Payload-Tenant-Mismatch wird mit `403` abgelehnt
- Credit-Note-Post und Return-Status-Update sind tenant-gescoped

## Verifikation

- `pytest tests/test_security_sales_credit_notes.py -q --no-cov`
- `python -m py_compile app/api/v1/endpoints/sales_credit_notes.py tests/test_security_sales_credit_notes.py`
