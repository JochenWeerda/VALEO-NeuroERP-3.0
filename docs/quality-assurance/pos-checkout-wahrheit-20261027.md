---
title: QA POS-CHECKOUT-WAHRHEIT-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: Offline-Abgleich und Retoure der Kasse melden Erfolg nur, wenn der Vorgang ueber den Fiskalisierungsdienst signiert und gespeichert ist; Mandant aus dem Token, kein angenommener Steuersatz.
---

# QA POS-CHECKOUT-WAHRHEIT-20261027

**Basis:** `origin/main` (d61993b9e). Keine Migration, keine neue Tabelle.

## Befunde

| Weg | Befund | Korrektur |
|---|---|---|
| `POST /pos/checkout` | Antwortete `completed` mit erfundener Bonnummer, **ohne irgendetwas zu speichern**. Die Offline-Warteschlange des Terminals (`pos-offline-queue.ts`) loescht nach einer erfolgreichen Antwort den Bon lokal: **jeder offline kassierte Bon ging verloren** (weder signiert noch im Z-Bon) | Bon laeuft ueber den `FiscalizationService` (derselbe Weg wie der Online-Verkauf, `domain_docflow.pos_fiscal_transactions`), Transaktionskennung = Offline-ID, idempotent; Mandant aus dem Token |
| `POST /pos/retoure` | Mandant aus dem Rumpf mit `settings.DEFAULT_TENANT_ID` als Rueckfall; Buchungsfehler verschluckt (`except Exception: rollback`), trotzdem „erfolgreich gebucht“; unbekannter Artikel ergab 0 Zeilen und Erfolg; **keine Signatur** (§ 146a AO: auch die Rueckgabe an der Kasse ist ein Geschaeftsvorfall) | Mandant aus dem Token; signierter Kassenbeleg mit negativen Betraegen; danach Bestandszugang; Fehler 422/503; idempotent ueber `vorgang_id` |
| Offline-Einreihung (`terminal.tsx`) | Speicherte den **unrabattierten** Preis und keinen Steuersatz; Kennung `offline-${Date.now()}` (je Millisekunde, nicht je Bon) | rabatt_pct und vat_rate werden mitgegeben, Kennung `offline-<uuid>` |
| `FiskalyProvider._receipt_payload` | Unbekannter Steuersatz (z. B. 7,8 % nach § 24 UStG) wurde **still als Normalsatz** signiert | `FiscalProviderError`, der Weg antwortet 503 |

## Entscheidungen

- **Kein angenommener Steuersatz** (Steuerlogik eine Quelle): Fehlt der Satz an der Position, kommt er aus
  `articles.steuerschluessel_verkauf` -> `domain_erp.tax_keys` (gueltig, aktiv, eigener Mandant). Sonst 422.
- **422 heisst: bleibt in der Warteschlange.** Ein Bon, dessen Positionen nicht zur Summe oder dessen Zahlungen nicht
  zum Betrag passen, wird nicht signiert. Die Warteschlange behaelt ihn und zaehlt `retry_count` hoch — sichtbar statt
  falsch. Altbestaende aus Geraeten mit der fehlerhaften Einreihung (Rabatt fehlte) bleiben dadurch ggf. haengen; das
  ist gewollt, ein Mensch muss sie pruefen.
- **Wiederholung = derselbe Vorgang.** Eine Kennung, die schon mit anderem Bruttobetrag signiert ist, ergibt 409.
- **Reihenfolge der Retoure:** Pruefen (Artikel, Steuerschluessel, Summe, Lager) -> signieren -> Bestand buchen.
  Scheitert nur die Bestandsbuchung, antwortet der Weg 503; das erneute Senden mit derselben `vorgang_id` signiert
  nicht neu und bucht den Bestand genau einmal (Pruefung ueber `source_document_id`).
- `kassierer` bleibt Anzeigename und wird nicht als Bearbeiter gespeichert.

## Nachweise

```
pytest tests/test_pos_checkout_wahrheit.py -rs           -> 18 passed, 0 skipped (valeo_probe, zurueckgerollt)
Gegenprobe alter Endpunkt                                -> 17 rot
Gegenprobe alter Provider                                -> 1 rot (Steuersatz 7,8 %)
POS-/Fiskal-/Identitaets-/Mandanten-/OpenAPI-Bestand (23 Module) -> 259 passed
generate_openapi.py --check                              -> OK (nur /pos/checkout, /pos/retoure)
tsc --noEmit (Gesamtprojekt), eslint (3 Dateien), ruff, bandit -> sauber
```

| Abnahmekriterium | Test |
|---|---|
| Offline-Bon signiert, gespeichert (Brutto, Zahlarten), Wiederholung ohne zweite Zeile | `test_offline_bon_wird_signiert_gespeichert_und_nur_einmal` |
| Unstimmige Summe/Zahlung, unbekannte Zahlart, nicht signierbarer Satz -> 422, nichts gespeichert | `test_unstimmiger_bon_bleibt_in_der_warteschlange` (4) |
| Steuersatz nie angenommen (ohne Schluessel, fremder, unbekannter Artikel) | `test_steuersatz_nie_angenommen` (3) |
| Ohne Fiskalisierung des Mandanten 503, keine fremde Kasse | `test_ohne_kasse_des_mandanten_kein_erfolg` |
| Wiederholung mit anderen Betraegen 409 | `test_wiederholung_mit_anderen_betraegen_wird_abgewiesen` |
| Retoure signiert negativ, bucht Bestand einmal | `test_retoure_signiert_negativ_bucht_bestand_und_nur_einmal` |
| Retoure ohne Grundlage bucht nichts | `test_retoure_ohne_grundlage_bucht_nichts` (4), `test_retoure_summe_muss_stimmen` |
| Mandant aus dem Token, kein Standardmandant, kein `except Exception` | `test_mandant_kommt_aus_dem_token_nicht_aus_dem_rumpf` |
| fiskaly signiert keinen unbekannten Satz als Normalsatz | `test_fiskaly_signiert_unbekannten_satz_nicht_als_normalsatz` |

## Offen (fachlich, nicht in diesem Slice)

- **Kassenverkauf bucht weder Bestand noch FiBu.** Online wie offline entsteht nur der signierte Kassenbeleg;
  `inventory_stock_movements` und Journal kennen keinen POS-Verkauf. Das ist eine Funktionsluecke mit eigenem
  Fachmodell (Lager je Terminal, Erloeskonten je Steuerschluessel, Tagesabschluss als Buchungszeitpunkt).
- **Geschaeftstag nachtraeglich signierter Bons** ist der Signaturtag (so legt der Fiskalisierungsdienst ihn an), nicht
  der Kassiertag aus `timestamp`. DSFinV-K kennt dafuer die Kennzeichnung „TSE-Ausfall“; der Dienst bildet sie noch
  nicht ab.
- Bricht der Online-Verkauf zwischen TSE-Start und -Abschluss ab, bleibt die gestartete Transaktion `ACTIVE`; der Z-Bon
  meldet sie als unfertig (`test_z_bon_wahrheit_vertrag`). Abbruch als signierter Vorgang fehlt (`cancelTransaction`).
- Maskenabnahme Terminal/Retoure mit konfigurierter Fiskalisierung liegt bei Codex.
