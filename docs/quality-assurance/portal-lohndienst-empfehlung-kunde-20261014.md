# PORTAL-LOHN-EMPF-KUNDE-20261014: Lohndienste und Empfehlungen nur fuer das eigene Kundenkonto

Stand: 2026-10-14 · Slice `PORTAL-LOHN-EMPF-KUNDE-20261014` · letzter Folgeslice von `PORTAL-KUNDE-001`, Umsetzung
TENANT-DOC-001 Punkt 1 (Nutzerentscheidung 14.10.2026)

## Befund

- `portal_lohndienst.py` (`/portal/lohndienste`) und `portal_intelligence.py` (`/portal/empfehlungen`) nahmen den
  Mandanten aus dem rohen Kopf `X-Tenant-ID` statt aus der Anmeldung (`get_tenant_id`).
- Lohndienste: Kunde aus `kunden_nr` im Body (Anlegen) bzw. in der Query (Liste; ohne Parameter **alle** Auftraege
  des Mandanten); Einzelabruf jedes Auftrags; Statuswechsel (bestaetigen, einplanen, Preis) durch jede Anmeldung.
- Empfehlungen: die Kundennummer im Pfad genuegte, um die Cross-Sell-Empfehlungen jedes Kunden zu lesen und als
  gesehen zu markieren; erzeugen konnte jede Anmeldung fuer jede Kundennummer.
- Beide Dienste halten ihre Daten nur im Arbeitsspeicher des Prozesses (`_SVC_CACHE`) — nach Neustart leer, bei
  mehreren Workern je Worker verschieden. Unveraendert, siehe Offen.

## Aenderung

- `app/auth/portal_kunde.py`: `kundennummer(db, kunde)` — die fachliche Kundennummer des gewaehlten Kontos (Schluessel
  beider Dienste); `kundennummer_des_mandanten(db, tenant, nr)` fuer interne Wege, die eine Nummer nennen.
- Lohndienste: Anlegen, Liste, Einzelabruf nur ueber `portal_kunde`; `kunden_nr` aus Body und Query entfernt
  (mitgeschickt wirkungslos); fremder Auftrag 404. Interne Betreuung legt nur mit Bearbeitungsrecht fuer Auftraege an.
  Statuswechsel nur Innendienst (`sales_order` bearbeiten), Mandant aus der Anmeldung.
- Empfehlungen: Lesen, Zusammenfassung, gesehen nur unter der Kundennummer des angemeldeten Kontos, sonst 404 (Pfad
  bleibt). Erzeugen (Ration, Schlagkartei) nur mit `sales_order` bearbeiten und nur fuer Kunden des Mandanten.
- Frontend `pages/portal/empfehlungen.tsx`: statt der festen Demo-Nummer `K-10001` das Konto aus
  `/portal/kundenkonten` (erstes Konto, Kopf `X-Kundenkonto`).
- OpenAPI: nur die neun Operationen beider Router und die Komponente `AuftragCreateBody`.

## Nachweis

- `tests/test_portal_kunde_trennung.py` (frische Datenbank `valeo_probe`), drei neue Faelle: Lohndienst — fremde
  `kunden_nr` in Body/Query wirkungslos, nur eigene Auftraege, fremder Auftrag 404, ohne Zuordnung 403; Status —
  Portalkunde und Leserolle 403, fremder Mandant 404, Bearbeiter 200; Empfehlungen — Erzeugen nur mit
  Bearbeitungsrolle (Leserolle 403) und nur fuer Kunden des Mandanten (404), Kunde liest nur unter eigener Nummer,
  fremde Nummer 404 fuer Liste, Zusammenfassung und gesehen. Gesamt 28 gruen.
- `tests/test_portal_services.py`, `tests/test_welle13_response_models.py` gruen; Frontend `tsc` und ESLint sauber.
- `tests/test_small_endpoints_wave57.py`: vorbestehend rot (9 × 401 mit altem Dev-Token), unveraendert.

## Offen

- **Persistenz:** Lohndienst-Auftraege und Empfehlungen liegen nur im Prozessspeicher — fuer den Produktivbetrieb
  ungeeignet (eigene Tabellen + Migration noetig).
- `pages/agrar/kunden-schlagkartei.tsx` (interne Seite mit Demo-Kunde) legt Lohndienste ohne `X-Kundenkonto` an —
  jetzt 400; braucht die Kundenwahl. `pages/portal/lohndienste.tsx` schickt `kunden_nr` noch mit (wirkungslos).
- Kontowahl im Frontend fuer Mehrfachzuordnung; Rolle je Portalweg nicht entschieden.
