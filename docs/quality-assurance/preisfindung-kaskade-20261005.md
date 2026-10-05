# Preisfindung — die Kaskade (Slice PREISFINDUNG-KASKADE-20261005)

Stand: 2026-10-05 · Welle 2, Slice 15

## Der Befund

`/pricing/calculate` ist **der** Preisfindungsweg: Die Lieferscheinerfassung ruft
ihn beim Artikelwechsel, `lib/api/konditionen.ts` und der Live-Kalkulator im
Konditionssystem ebenso. Er hat fünf Stufen, und **drei von ihnen haben nie
funktioniert**:

| Stufe | Liest | Lage |
| --- | --- | --- |
| 1 Preisliste | `domain_pricing.price_list_items` | funktioniert |
| 2 Kontraktrabatt | `domain_contracts.contracts.discount_percent` / `.discount_amount` | **Spalten gibt es nicht** |
| 3 Kundenrabatt | `BusinessPartnerService.get_customer_discount` | liefert `None` — `domain_crm.customers` führt keine Rabattspalten (dort dokumentiert) |
| 4 Mitarbeiterrabatt | `domain_pricing.discount_rules` | **Tabelle gibt es nicht** |
| 5 Basispreis | `domain_inventory.articles.sales_price` | funktioniert |

`domain_contracts.contracts` ist ein **Vertragsregister** (`title`,
`counterparty_id`, `notice_period_days`, `auto_renewal_days`) — kein
Handelskontrakt. Es hat nie Rabattspalten gehabt.

Jeder Fehlschlag lief in:

```python
except Exception:
    db.rollback()
```

Das Ergebnis ist der **volle Listenpreis** mit `source: "base"` — ein plausibler,
falscher Preis. Ein Preis ist keine Anzeige, sondern die Grundlage der Rechnung;
ein verschluckter Rabatt ist ein Abrechnungsfehler, der wie ein richtiger Preis
aussieht. Und `source` log mit: Es stand `"price_list"` auch dann, wenn die
Kundenrabattstufe danach gescheitert war.

### Die vierte Lücke: gepflegte Staffeln ohne Wirkung

`domain_pricing.staffelrabatte` führt in der Entwicklungsdatenbank **20 Zeilen**
— Mengenstaffeln, die ein Haus angelegt hat, mit Stufen wie
`[{ab_menge: 10, rabatt_prozent: 3}, {ab_menge: 25, rabatt_prozent: 5}]`. Es gibt
Wege zum Anlegen und Auflisten. Die Kaskade **liest sie nicht**. Zwei Umsetzungen
eines Begriffs, von denen die gepflegte wirkungslos ist.

### Und der Mandant kam aus einem Query-Parameter

```python
tenant_id: str = Query(DEFAULT_TENANT)
```

Wer den Parameter setzt, fragt die Preislisten und Staffeln eines **fremden**
Hauses ab; wer ihn wegläßt, bekommt stillschweigend die des Vorgabemandanten. Die
Frontend-Aufrufer setzen ihn nicht und schicken ohnehin `X-Tenant-ID`.

Zwei bestehende Tests hießen `test_pricing_find_tenant_isolation` und
`test_staffelrabatte_tenant_isolation` und prüften die Trennung **über genau
diesen Parameter** — ein Aufrufer, der seinen Mandanten selbst wählen kann, ist
aber keine Trennung. Beide sind auf den Kopf umgestellt und prüfen jetzt
zusätzlich, dass ein mitgegebener Parameter ihn nicht aushebelt.

## Was jetzt gilt

### Die Reihenfolge

```
Preisliste  (ersetzt den Basispreis)
   └─▶ Kontrakt  ──▶ Mengenstaffel ──▶ Kundenrabatt ──▶ Rollenrabatt
                                                           └─▶ sonst Basispreis
```

Es gilt **eine** Stufe — die erste, die greift. Nicht additiv (das war schon
vorher so dokumentiert).

**Die Entscheidung zur Einordnung der Staffel** (sie ist neu): Sie steht über dem
Kundenrabatt, weil sie an der **tatsächlich bestellten Menge** hängt und damit die
spezifischere Aussage ist; der Kontrakt steht darüber, weil er eine Zusage ist.
Ein `festpreis` in der Staffel ersetzt den Listenpreis, wie es eine Preisliste
tut. Das ist eine fachliche Festlegung und gehört dem Vertriebs-Owner zur
Abnahme.

Die Reihenfolge steht einmal im Code (`preisfindung_service.STUFEN`), und
`QUELLEN` leitet sich daraus ab — damit `source` nicht an zwei Stellen gepflegt
werden muss.

### Der Kontraktpreis kommt aus dem führenden Modell

`domain_ops.kon_contract_line` trägt `unit_price`, `discount_pct` und `surcharge`
**je Artikel**. Das ist genauer als ein pauschaler Kopfrabatt — und es gibt den
Kopfrabatt nicht. Gelesen wird die Position des Artikels im angegebenen Kontrakt;
`unit_price` ersetzt den Listenpreis, `discount_pct` ist der Rabatt.

`domain_contracts.contracts` bleibt unberührt (eigener Zweck,
`central_contracts.py`).

### Die Staffelauswahl

Zutreffend ist eine aktive, heute gültige Staffel, die den Artikel betrifft —
direkt, über die Zuordnungstabelle `staffelrabatt_artikel` oder über die
Warengruppe — und, falls sie einen Kunden nennt, diesen Kunden. Sortiert wird vom
Besonderen zum Allgemeinen: kundenbezogen vor allgemein, artikelbezogen vor
gruppenbezogen.

Innerhalb der Staffel gilt die **höchste** Stufe, deren Mindestmenge erreicht ist.

**Eine Stufe ohne Wirkung zählt nicht als Treffer.** Die Bestandsdaten enthalten
Nullstufen (`ab_menge: 1, rabatt_prozent: 0`); würden sie greifen, verdrängten
sie den Kundenrabatt und den Rollenrabatt mit einem Rabatt von null — die
Kaskade wäre wirkungslos, und `source` sagte `staffelrabatt`.

### Migration `preisfindung_rabattregeln_20261005`

`domain_pricing.discount_rules` mit `tenant_id`, `role`, `discount_percent`,
`is_active`, `valid_from`/`valid_until`.

| Prüfbedingung / Index | Was sie verhindert |
| --- | --- |
| `ck_rabattregel_prozent_bereich` | Ein Rabatt außerhalb 0…100 % — über 100 % wäre der Preis negativ. |
| `ck_rabattregel_zeitraum` | Ein Gültigkeitsende vor dem Beginn: eine Regel, die nie gilt und gepflegt aussieht. |
| `ux_rabattregel_rolle` (partiell auf `is_active`) | Zwei aktive Regeln für dieselbe Rolle. Mit `LIMIT 1` ohne Sortierung hätte der Zufall den Preis bestimmt. |

`pruefe_rabatt()` prüft denselben Bereich auch für Preislisten, Kontraktzeilen
und Staffeln: Dort sind die Spalten älter und ohne Prüfbedingung, also wird
geprüft statt gehofft.

### Ein Fehlschlag ist kein Preis

Jede Stufe liefert ein Ergebnis oder einen **503** mit der Stufe im Text
(`stufe_nicht_lesbar`). Wer einen Preis nicht vollständig ermitteln kann, darf
keinen nennen — sonst wird auf einer Störung abgerechnet.

### Masken

* `lieferschein-erfassung.tsx`: Der Preisfindungs-`catch` war leer
  (`// Fallback: Verwende bereits gesetzten sales_price`). Jetzt ein Toast mit dem
  Hinweis, was fehlt. Geldbeträge werden mit `Number()` gelesen statt auf eine
  implizite Umwandlung zu bauen.
* `konditionssystem.tsx`: `Mengenstaffel` im Quellenwörterbuch, die Kaskade in der
  Beschreibung richtiggestellt, die getroffene Staffelstufe wird angezeigt.
* `lib/api/konditionen.ts`: `PreisfindungResult` sagt jetzt `number | string` —
  Geldbeträge kommen als `Decimal` und damit als Zeichenkette; `number` zu
  behaupten war falsch.

## Nachweis

```
DATABASE_URL=…/valeo_probe python -m pytest \
  tests/test_preisfindung_kaskade_vertrag.py      → 29 passed
  tests/test_api_gap_lager_pricing_scan.py        → zusammen 47 passed
  + Kontrakt-Hedging/Preis                        → 65 passed
```

Die 29 Verträge prüfen unter anderem: der Mandant kommt aus dem Kopf und ein
mitgegebener Parameter hebelt ihn nicht aus; eine Staffel greift ab der Menge und
die höchste erreichte Stufe gilt; ein Festpreis ersetzt den Listenpreis; eine
Nullstufe verdrängt nichts; abgelaufene und inaktive Staffeln wirken nicht; die
Gruppenstaffel greift über die Warengruppe; die kundenbezogene geht der
allgemeinen vor; die Kontraktzeile bestimmt Preis und Rabatt und geht der Staffel
vor; das Vertragsregister wird nicht mehr gelesen; der Rollenrabatt greift nur
aktiv, gültig und für den eigenen Mandanten; ein Rabatt außerhalb 0…100 % und eine
zweite aktive Regel je Rolle sind in der Datenbank unmöglich; eine unlesbare
Stufe ist ein 503 mit Stufenangabe und kein Listenpreis.

Migration gegen die frische `valeo_probe` und die gewachsene `valeo_neuro_erp`
hochgezogen. Gates: Tabellenverweise **8 → 7** an lebenden Wegen, Paginierung,
Baseline-Integrität, tote Transaktionen und Godfile alle grün.

### Zum Alembic-Kopf

Beim Hochziehen standen zwei Köpfe: Ein anderer Agent arbeitet an
`journal_number_tenant_20261005` — dem Handshake aus dem
Genossenschafts-Slice (`journal_entries.entry_number` systemweit eindeutig).
Dessen Revisionsdatei ist noch **unversioniert**, deshalb wurde **nicht** darauf
gechaint und nicht zusammengeführt: Eine Migration, die auf eine unversionierte
Revision zeigt, bricht in der CI mit `KeyError`. Meine Revision hängt an
`kontrakt_disposition_20261005` (committet); hochgezogen wurde mit explizitem
Revisionsziel statt `head`. Die Zusammenführung macht, wer zuletzt committet.

## Offene Punkte (Handshake)

1. **Die Reihenfolge Kontrakt > Staffel > Kundenrabatt** ist eine fachliche
   Entscheidung — Abnahme beim Vertriebs-Owner.
2. **Der Kundenrabatt ist weiter wirkungslos:** `domain_crm.customers` führt keine
   Rabattspalten, `get_customer_discount` liefert `None` und dokumentiert das.
   Zielquelle sind laut Kommentar die BP-Rabatt-Satelliten
   (`business_partner_discount_items`, `business_partner_price_agreements`).
   Eigener Slice, nicht hier.
3. **Sechzehn weitere Preis- und Rabatttabellen** (`preis_rabattsaetze`,
   `preis_rabattgruppen`, `individualpreise`, `article_price_thresholds`,
   `price_adjustment_rules`, `rohware_za_staffeln`, …) stehen neben den hier
   benutzten. Ein ADR zum führenden Preismodell fehlt.
4. Dass die Kaskade jetzt 503 statt des Listenpreises liefert, macht bisher
   unsichtbare Störungen sichtbar. Beabsichtigt.
