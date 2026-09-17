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

## Stand 2026-09-17, Abend

    285 Felder gegen deklarierte Antworten geprueft (Start: 110)
      0 Abweichungen
      0 Kopfquellen ohne deklarierte Antwort
     49 Tabellenquellen ohne deklarierte Zeilenform (Start: 52)

Aufruf: `python scripts/check_field_contracts.py [--list]`.
Gate: `tests/test_mask_field_contracts.py`, `tests/test_mask_bridge_field_contracts.py`.

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

## Die blinden Flecken: 49 Tabellenquellen

Kopfquellen sind vollstaendig typisiert — die zwoelf Bruecken-Koepfe hat Cursor
in P4 erledigt, `sales/invoice` der Rechnungsweg selbst. Bei den Tabellen liegt
der Rest: 49 von 63 Quellen sagen ihre Zeilenform nicht zu.

Drei davon sind heute geschlossen worden, als Muster fuer die uebrigen:

- `GET /sales/invoices` → `SalesInvoiceListOut` mit `SalesInvoiceListRowOut`
- `GET /sales/invoices/{id}/tabs/positionen` → `InvoicePositionTabOut`
- `GET /sales/invoices/{id}/tabs/herkunft` → `InvoiceOriginTabOut`

Die beiden Register hatten vorher **eine** Route mit Pfadparameter. Zwei
Register mit zwei Zeilenformen brauchen zwei Routen; die Sammelroute bleibt
dahinter stehen, damit ein unbekanntes Register weiterhin eine leere Seite
ergibt und keinen Fehler.

`ZEILEN_NICHT_PRUEFBAR_MAX` steht auf **49** und darf nur sinken.

## Was das Gate nicht kann

- Es liest das **deklarierte** Schema, nicht die tatsaechliche Antwort. Ein
  Endpunkt, der mehr liefert als er zusagt, gilt hier als zusagend.
- Es prueft **Kopffelder** (`tabs[].fields` gegen die `entity`-Quelle).
  Tabellenspalten haengen an Seiten-Huellen (`items`), deren Zeilenform in aller
  Regel nicht deklariert ist; dort ist der Vertrag weiter offen.
- Es sagt nichts ueber **Inhalt**: Ein Feld kann heissen wie vereinbart und
  trotzdem etwas anderes bedeuten.
