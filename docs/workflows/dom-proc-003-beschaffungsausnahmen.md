# DOM-PROC-003 - Beschaffungsausnahmen und Folgefaelle

## Ziel

Einkaufsausnahmen, Matching, Nachforderung und Lieferantenkommunikation als echte Folgefaelle statt als lose Einzelaktionen fuehren.

## Scope

- Rechnungseingang und Matching-Ausnahmen
- Freigabe- und Nachforderungsfaelle
- Lieferantenkommunikation und Dokumentruecklauf
- Folgewege von Anfrage, Bestellung, Avis und Rechnung

## Dateibesitz

- `packages/frontend-web/src/pages/einkauf/*`
- relevante Beschaffungsendpunkte
- Dokument- und Kommunikationspfade

## Abnahmekriterien

- Beschaffungsfaelle bilden Matching-Ausnahmen, Nachforderung und Folgekommunikation als echte Arbeitsobjekte ab.
- Bulk- und Folgeaktionen fuehren nicht nur in lokale Quittung, sondern in belastbare naechste Schritte.
- Lieferanten- und Belegkontext bleibt ueber den ganzen Folgefall erhalten.

## Risiken

- grosse Heterogenitaet im Einkaufsraum
- hoher Anteil an Listenmasken mit begrenztem Platz
- Folgekommunikation haengt teilweise an externen Integrationen
