# INT-SG-041 - Superglue Tool-Provisioning

## Ziel

Den frischen lokalen Superglue-Stack von einem leeren Katalog zu einem reproduzierbar provisionierten Pilotpfad weiterziehen und einen echten Tool-Run nachweisen.

## Umsetzung

- neuer Provisioning-Service fuer drei kanonische Pilot-Tools (`sg.document.search`, `sg.partner.adapter.preview`, `sg.customer.profile.preview`)
- neue kontrollierte Provider-Endpunkte fuer Provisioning und Smoke-Run
- Tool-Sync faellt fuer provisionierte Pilot-Tools sauber auf VALEO-Metadaten zurueck
- Smoke-Skripte warten jetzt retry-basiert auf Health/Tool-Listing

## Ergebnis

Der lokale Upstream-Container liefert nach dem Slice einen nicht-leeren `GET /v1/tools`-Katalog und einen erfolgreichen `POST /v1/tools/sg.document.search/run`.
