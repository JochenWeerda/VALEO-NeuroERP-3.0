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

    110 Felder gegen deklarierte Antworten geprueft
      0 Abweichungen
     13 Maskenquellen ohne deklarierte Antwort

Aufruf: `python scripts/check_field_contracts.py [--list]`.
Gate: `tests/test_mask_field_contracts.py`.

## Die 13 blinden Flecken

Diese Endpunkte typisieren ihre Antwort nicht (`extra="allow"` ohne Felder oder
rohe `dict`-Rueckgabe). Das Gate kann dort **nichts** zusagen — weder dass die
Schluessel stimmen noch dass sie fehlen:

- `einkauf/anfrage`, `einkauf/angebot`, `einkauf/anlieferavis`,
  `einkauf/auftragsbestaetigung`, `einkauf/purchase-order`, `einkauf/supplier`
- `finance/ap-invoice`, `finance/bankkonto`, `finance/debitor`,
  `finance/kreditor`
- `futtermittel/mischfuttermittel`
- `qualitaet/reklamation`
- `sales/invoice`

**Der Weg dahin, wenn jemand weitermacht:** Antwortmodelle deklarieren, dann
faellt die Zahl von selbst. Jede Maske, die aus der Liste verschwindet, ist eine
Maske, deren Kopf nicht mehr stillschweigend leer bleiben kann.

`NICHT_PRUEFBAR_MAX` im Test steht auf 13 — die Zahl darf **sinken**, nicht
steigen. Eine neue ungetypte Maskenquelle macht das Gate an dieser Stelle blind,
und das soll auffallen.

## Was das Gate nicht kann

- Es liest das **deklarierte** Schema, nicht die tatsaechliche Antwort. Ein
  Endpunkt, der mehr liefert als er zusagt, gilt hier als zusagend.
- Es prueft **Kopffelder** (`tabs[].fields` gegen die `entity`-Quelle).
  Tabellenspalten haengen an Seiten-Huellen (`items`), deren Zeilenform in aller
  Regel nicht deklariert ist; dort ist der Vertrag weiter offen.
- Es sagt nichts ueber **Inhalt**: Ein Feld kann heissen wie vereinbart und
  trotzdem etwas anderes bedeuten.
