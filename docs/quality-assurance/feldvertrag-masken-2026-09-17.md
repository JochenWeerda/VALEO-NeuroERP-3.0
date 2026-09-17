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

## Stand 2026-09-17

    197 Felder gegen deklarierte Antworten geprueft (Start: 110)
      0 Abweichungen
      0 Maskenquellen ohne deklarierte Antwort

Aufruf: `python scripts/check_field_contracts.py [--list]`.
Gate: `tests/test_mask_field_contracts.py`, `tests/test_mask_bridge_field_contracts.py`.

## Die blinden Flecken: keine mehr

Von 13 ungetypten Quellen sind alle weg. Die zwoelf Bruecken-Koepfe hat Cursor
in P4 typisiert, `sales/invoice` der Rechnungsweg selbst: `GET /sales/invoices/{id}`
sagt jetzt `SalesInvoiceDetailOut` zu — Kopf, Positionen und je Position ihre
Herkunft, Mengen und Betraege als Zeichenketten, weil die Anzeige rundet und der
Wert nicht.

`NICHT_PRUEFBAR_MAX` steht damit auf **0**. Eine neue ungetypte Maskenquelle
macht das Gate an ihrer Stelle blind — und faellt ab jetzt sofort auf.

## Was das Gate nicht kann

- Es liest das **deklarierte** Schema, nicht die tatsaechliche Antwort. Ein
  Endpunkt, der mehr liefert als er zusagt, gilt hier als zusagend.
- Es prueft **Kopffelder** (`tabs[].fields` gegen die `entity`-Quelle).
  Tabellenspalten haengen an Seiten-Huellen (`items`), deren Zeilenform in aller
  Regel nicht deklariert ist; dort ist der Vertrag weiter offen.
- Es sagt nichts ueber **Inhalt**: Ein Feld kann heissen wie vereinbart und
  trotzdem etwas anderes bedeuten.
