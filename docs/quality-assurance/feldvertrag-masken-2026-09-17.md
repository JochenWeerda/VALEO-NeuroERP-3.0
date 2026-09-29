---
title: Feldvertrag Masken
type: reference
audience: [agent, entwickler, qa]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-17
version: 1.0.0
description: Prueft, ob die Endpunkte die Schluessel liefern, nach denen die Masken fragen — und wo das nicht pruefbar ist.
---

# Feldvertrag: Spricht der Endpunkt die Sprache der Maske?

## Warum es dieses Gate gibt

Der Zaehler in `check_frontend_api_calls.py` und das Inventar in
`tests/test_mask_endpoint_inventory.py` pruefen **Adressen**. Sie sagen nichts
darueber, ob die **Schluessel** stimmen. Der Unterschied ist der zwischen einem
sichtbaren und einem stillen Fehler:

| | Antwort | Was die Maske zeigt |
|---|---|---|
| Falsche Adresse | 404 | „Vorgang konnte nicht geladen werden" |
| Falsche Schluessel | 200 | **leere Felder** — sieht aus wie „nichts erfasst" |

Zehn Masken hatten den zweiten Fall: `beleg_nr` statt `rechnungsnr`, `ls_nr`
statt `delivery_note_number`, `wert` statt `amount`, `ist_aktiv` statt
`is_active`. Alle behoben; das Gate haelt den Stand.

## Stand 2026-09-17, spaeter Abend

    Felder gegen deklarierte Antworten geprueft (Kopf plus typisierte Zeilen)
      0 Abweichungen
      0 Kopfquellen ohne deklarierte Antwort
      0 Tabellenquellen ohne deklarierte Zeilenform (Start: 52)

Aufruf: `python scripts/check_field_contracts.py [--list]`.
Gate: `tests/test_mask_field_contracts.py`, `tests/test_mask_bridge_field_contracts.py`.

Die letzten 17 Generic-Stubs (`/masks/` Duenger/Saatgut/Lead und elf
`/mask-rollouts/`-Catch-alls) haben eigene Routen und Zeilenformen. Die
Ratsche steht auf 0. SEPA, POS-Huelle, Budget und Personalstamm sind R5
und nicht Teil dieses Gates.

## Kopf und Zeile

Das Gate prueft beide Haelften:

| | Anzahl | Stand |
|---|---|---|
| Kopffelder (`tabs[].fields`) | 204 | vollstaendig geprueft |
| Tabellenspalten (`tables[].columns`) | 305 | geprueft, **wo die Zeile deklariert ist** |

Die Spalten sind die groessere Haelfte und haben dasselbe stille Versagen: Eine
Spalte mit falschem Schluessel bleibt leer. Lesbar ist eine Zeilenform, wenn die
Antwort eine Liste typisierter Zeilen ist (`list[ZeileOut]`) oder eine
Seiten-Huelle mit typisiertem `items`.

## Die blinden Flecken: 0 Tabellenquellen

Kopfquellen sind vollstaendig typisiert — die zwoelf Bruecken-Koepfe hat Cursor
in P4 erledigt, `sales/invoice` der Rechnungsweg selbst. Die Tabellen sind
ebenfalls geschlossen: 52 → 49 (Rechnung) → 43 (P8) → 27 (P9) → 0 (P10).

Drei davon sind heute geschlossen worden, als Muster fuer die uebrigen:

- `GET /sales/invoices` → `SalesInvoiceListOut` mit `SalesInvoiceListRowOut`
- `GET /sales/invoices/{id}/tabs/positionen` → `InvoicePositionTabOut`
- `GET /sales/invoices/{id}/tabs/herkunft` → `InvoiceOriginTabOut`

Die beiden Register hatten vorher **eine** Route mit Pfadparameter. Zwei
Register mit zwei Zeilenformen brauchen zwei Routen; die Sammelroute bleibt
dahinter stehen, damit ein unbekanntes Register weiterhin eine leere Seite
ergibt und keinen Fehler.

`ZEILEN_NICHT_PRUEFBAR_MAX` steht auf **27** und darf nur sinken.

Die dreizehn leeren P4-Brueckenregister (`/masks/.../tabs/...`) haben eigene
Routen mit Zeilenform; die Tabelle bleibt leer, bis ein Fachendpunkt Daten
liefert. Auftrag und Rechnung bleiben Claude. Duenger, Saatgut, Lead und der
mask-rollout-Catch-all sind der Rest.

## Was das Gate nicht kann

- Es liest das **deklarierte** Schema, nicht die Laufzeit-Antwort. Mit
  `response_model` ist deklariert ⊇ tatsächlich. Das verbleibende Risiko ist
  nicht „Feld fehlt", sondern „Feld ist immer leer".
- Es sagt nichts ueber **Bedeutung**: `menge` kann gelieferte oder berechnete
  Menge meinen. Dagegen helfen Fachtests, kein Scanner.
- Wo die Zeilenform fehlt (`extra="allow"` ohne Felder), zaehlt die Quelle als
  unpruefbar statt als Abweichung — das sind die 27 restlichen Generic-Stubs.
