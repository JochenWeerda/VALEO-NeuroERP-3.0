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

- `GET/PUT /api/v1/pos/fiscalization/config`
- `GET /api/v1/pos/fiscalization/readiness`
- `POST /api/v1/pos/fiscalization/transactions/start`
- `POST /api/v1/pos/fiscalization/transactions/finish`
- `GET /api/v1/pos/fiscalization/daily-summary`
- `POST /api/v1/pos/fiscalization/cash-point-closings`
- `POST /api/v1/pos/fiscalization/exports`

`VITE_FISKALY_API_KEY` und `VITE_FISKALY_API_SECRET` sind nicht zulaessig.
Tenantbezogene `settings` weisen Schluessel wie `secret`, `token`, `password`,
`credential` oder `api_key` ab. Die Admin-Seite unter
`/admin-suite/pos-fiscalization` verwaltet nur Providerwahl, Kassen-/TSS-ID,
Client-ID, Terminal-ID und die explizite Simulationsfreigabe.

## Fachliche Trennung

- TSE-Export: signierte technische Transaktionsdaten des TSE-Providers.
- DSFinV-K-Export: strukturierte Kassendaten und Cash Point Closings nach
  amtlicher DSFinV-K 2.4.

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

Die POS-Fibu-Uebergabe verwendet eine zentrale, ausgeglichene Buchungsmatrix:

| Vorgang | Soll | Haben | Umsatzwirkung |
|---|---|---|---|
| Barverkauf | 1000 Kasse | 8400 POS-Umsatz | ja |
| EC-/Kartenzahlung | 1200 Bank / EC | 8400 POS-Umsatz | ja |
| B2B-Verkauf | 1400 Forderungen | 8400 POS-Umsatz | ja |
| Gutscheinannahme | 1600 Gutscheinverbindlichkeit | 8400 POS-Umsatz | ja |
| Gutscheinausgabe gegen Bar | 1000 Kasse | 1600 Gutscheinverbindlichkeit | nein |
| Barentnahme | 1800 Privatentnahme/Barauszahlung | 1000 Kasse | nein |

Gutscheinausgaben duerfen nicht vor Einloesung als Umsatz erfasst werden. Jede
generierte Abschlussbuchung wird vor Persistenz auf Soll-Haben-Gleichheit
geprueft.

## Virtueller Belegdruck

Der interne PDF-Druckvertrag erzeugt fuer automatisierte Pruefer-Simulationen:

- einen Kassenbon mit Beleg- und Transaktionsnummer, Zeitstempeln,
  Signaturzaehler, Signatur, QR-Daten, Zahlungsarten und TSE-Zertifikatsdaten;
- einen Tagesabschlussbeleg mit Zahlungsarten, Barentnahmen,
  Gutscheinausgaben/-annahmen, FiBu-Belegnummer und allen Buchungszeilen.

Das verwendete Mock-Zertifikat ist im Beleg deutlich als
`MOCK - NICHT PRODUKTIV` gekennzeichnet. Diese Evidenz prueft Layout,
Vollstaendigkeit und Datenfluss. Sie ersetzt keine echte TSE-Signatur, keine
fiskaly-/Swissbit-Sandboxabnahme und keinen Test auf dem physischen
Produktionsdrucker.

## Optionale fiskaly-Produkte

`SUBMIT DE`, `RECEIPT` und `SAFE` besitzen getrennte Readiness-Eintraege.
Die Vertragsversion wird serverseitig ueber
`FISKALY_SUBMIT_DE_CONTRACT_VERSION`, `FISKALY_RECEIPT_CONTRACT_VERSION` und
`FISKALY_SAFE_CONTRACT_VERSION` nachgewiesen.

- SUBMIT DE: Mitteilungsverfahren fuer elektronische Aufzeichnungssysteme.
- RECEIPT: digitaler Beleg- und Auslieferungsvertrag.
- SAFE: revisionsorientierte Datei-/Exportablage mit eigener API.

Ein gesetzter Vertrag macht das Produkt sichtbar freigegeben, aktiviert aber
noch keinen geratenen Live-Call. Live-Ausfuehrung folgt erst aus dem
lizenzierten OpenAPI-Vertrag im fiskaly Workspace, Produktabnahme, DPA/AVV und
Credentials.

Offizielle Referenzen:

- https://developer.fiskaly.com/api/sign-de/submission/v1
- https://developer.fiskaly.com/api/receipt/v1
- https://developer.fiskaly.com/api/safe/v1
- https://www.swissbit.com/en/products/security-products/cloud-tse/
- https://www.swissbit.com/en/products/security-products/tse/

## Externe Abnahme

- fiskaly Sandbox- und Live-Credentials
- Swissbit Partnerpaket/API- oder SDK-Vertrag
- DSFinV-K-Pruefwerkzeugvalidierung
- KassenSichV-/GoBD-Fachabnahme
- reale Drucker-, Offline- und Ausfallszenarien
