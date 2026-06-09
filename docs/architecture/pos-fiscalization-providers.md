# POS-Fiskalisierung: fiskaly und Swissbit

Stand: 2026-06-09

## Entscheidung

VALEO besitzt POS, Warenkorb, Zahlung, Beleg, Bestand und Fibu selbst. Externe
Provider liefern die technische Sicherheitseinrichtung und optionale
Compliance-Dienste.

Unterstuetzte Signaturprovider:

- `fiskaly`: SIGN DE per REST API und DSFINVK DE als getrennte API.
- `swissbit_cloud`: Swissbit Cloud TSE 2 per REST-Vertrag.
- `swissbit_gateway`: Swissbit Hardware-TSE 1/1.1/2 ueber einen lokalen,
  vom offiziellen Swissbit SDK gespeisten Gateway.
- `simulation`: expliziter Entwicklungsprovider, in Produktion gesperrt.

Die Swissbit-Detailvertraege und SDK-Pakete sind partner-/loginpflichtig.
Darum bleibt Livebetrieb blockiert, solange
`SWISSBIT_API_CONTRACT_VERSION` und Credentials fehlen.

## Sicherheitsgrenze

Provider-Secrets liegen ausschliesslich im Backend. Der Browser spricht nur:

- `GET /api/v1/pos/fiscalization/readiness`
- `POST /api/v1/pos/fiscalization/transactions/start`
- `POST /api/v1/pos/fiscalization/transactions/finish`
- `GET /api/v1/pos/fiscalization/daily-summary`
- `POST /api/v1/pos/fiscalization/cash-point-closings`
- `POST /api/v1/pos/fiscalization/exports`

`VITE_FISKALY_API_KEY` und `VITE_FISKALY_API_SECRET` sind nicht zulaessig.

## Fachliche Trennung

- TSE-Export: signierte technische Transaktionsdaten des TSE-Providers.
- DSFinV-K-Export: strukturierte Kassendaten und Cash Point Closings.

Swissbit wird als TSE-Provider angeboten. Da oeffentlich kein belastbarer
Swissbit-DSFinV-K-API-Vertrag dokumentiert ist, wird DSFinV-K bei Swissbit-TSE
separat ueber fiskaly DSFINVK DE angebunden. Die Providerwahl ist deshalb in
`provider` und `dsfinvk_provider` getrennt.

## Tagesabschluss

Vor einer Fibu-Buchung gelten folgende Gates:

1. Provider und Kasse sind tenantbezogen konfiguriert.
2. Es gibt keine unvollstaendige Fiskaltransaktion.
3. Der Cash Point Closing wurde vom DSFinV-K-Provider angenommen.
4. Ein simulierter Closing darf nicht produktiv gebucht werden.
5. Erst danach werden Abschluss und Fibu-Eintraege persistiert.

## Optionale fiskaly-Produkte

`SUBMIT DE`, `RECEIPT` und `SAFE` bleiben separate Ausbaustufen. Live-Aufrufe
werden nicht anhand geratener URLs oder Payloads implementiert. Vor Aktivierung
sind die im Workspace freigeschalteten OpenAPI-Vertraege, Produktlizenzen,
DPA/AVV und Credentials als Betriebs-Gate erforderlich.

## Externe Abnahme

- fiskaly Sandbox- und Live-Credentials
- Swissbit Partnerpaket/API- oder SDK-Vertrag
- DSFinV-K-Pruefwerkzeugvalidierung
- KassenSichV-/GoBD-Fachabnahme
- reale Drucker-, Offline- und Ausfallszenarien

