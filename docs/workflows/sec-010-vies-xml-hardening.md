# SEC-010 - VIES XML Hardening

## Ziel

XML-Injection im SOAP-Body der VIES-USt-ID-Pruefung verhindern.

## Umsetzung

- `countryCode` und `vatNumber` werden vor dem SOAP-Request escaped

## Tests

- `tests/test_security_webhooks_vies.py`

