# POS-Fiskalisierung Provider-UAT

Stand: 2026-06-09

## Automatisierter Nachweis

- fiskaly authentifiziert per Access Token und sendet `ACTIVE`/`FINISHED`
  idempotent per `PUT`.
- TSE- und DSFinV-K-Export verwenden getrennte Providerpfade.
- Swissbit Cloud und Hardware-Gateway nutzen denselben VALEO-Vertrag.
- Swissbit-Livebetrieb blockiert ohne Partner-Vertragsversion.
- Simulation blockiert in Produktion.
- Im Frontend existieren keine fiskaly-Secrets.
- Der fruehere Festdaten-DSFinV-K-Export ist entfernt.
- POS- und Parallelinstallationsregressionen sind gruen.

## Live-UAT

Pro Provider ausfuehren:

1. Terminal und Cash Register registrieren.
2. Barverkauf mit 19 Prozent signieren.
3. Verkauf mit 7 Prozent signieren.
4. Split Payment, Retoure, Storno und Gutschein signieren.
5. Netzunterbrechung zwischen `ACTIVE` und `FINISHED` provozieren.
6. Wiederholung mit identischer Transaktions-ID pruefen.
7. Tagesabschluss mit offenem Vorgang muss blockieren.
8. Cash Point Closing uebertragen.
9. TSE-Export und DSFinV-K-Export getrennt abrufen.
10. Export mit externem Pruefwerkzeug validieren.

## Aktuelle externe Gates

- Keine Produktiv-Credentials im Repository.
- Swissbit Detaildokumentation ist nicht oeffentlich und muss aus dem
  Partnerportal bereitgestellt werden.
- SUBMIT DE, Digitalbeleg und SAFE benoetigen separate Produktfreischaltung.
- Ein erfolgreicher Unit-Test ersetzt keine KassenSichV-/GoBD-Abnahme.

