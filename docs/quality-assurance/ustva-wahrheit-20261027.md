---
title: QA USTVA-WAHRHEIT-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: Umsatzsteuer-Voranmeldung aus dem Hauptbuch ueber die Konten der Steuerschluessel; Ablauf berechnet, geprueft, freigegeben, uebermittelt mit geprueften Bearbeitern; Uebermittlung nur mit ELSTER-Transferticket.
---

# QA USTVA-WAHRHEIT-20261027

**Basis:** `claude/rls-domain-shared-20261027` (#79), wegen der Alembic-Kette. Migration
`vat_return_bearbeiter_20261027` folgt auf `rls_domain_shared_20261027`; `alembic heads` zeigt einen Head.

## Befunde

| Stelle | Befund | Korrektur |
|---|---|---|
| `GET /compliance/ustva` | `elster_uebermittlung = EINGEREICHT`, sobald der Zeitraum **keine Buchungsentwuerfe** hatte — ohne jede Uebermittlung; Mandant aus `?tenant_id=` mit `default`; Konten per `LIKE '17%'`/`'15%'`; Lesefehler wurden Nullen | Zahlen aus `app.finance.ustva`; `UEBERMITTELT` nur mit gespeichertem Transferticket; Mandant aus dem Token; Frist nach § 18 UStG; 503 bei Lesefehler |
| `GET /finance/vat-return/vorberechnung`, `POST /calculate` | Erloes-/Aufwandskonto am **ersten Zeichen der Konto-UUID** erkannt; pauschal **19 %**; Filter auf `journal_entry_lines.tax_code` — keine Buchung schreibt diese Spalte (live 0 von 41 Zeilen): **Ergebnis immer 0**; Fehler als 0 (Vorberechnung) bzw. 500 mit Fehlertext | Eine Berechnung aus den gebuchten Salden der Konten, die die Steuerschluessel nennen; Klaerungen statt Annahmen (422); 503 |
| `POST /calculate` | Steuerpflichtiger **„Company Name“** | Name des Mandanten |
| `POST /{id}/validate` | Verglich mit derselben nie gefuellten Spalte | Neuberechnung aus dem Hauptbuch je Summe und Kennzahl; offene Entwuerfe und Klaerungen verhindern die Pruefung |
| `POST /{id}/approve` | Freigebender **aus dem Rumpf**, nur in der Antwort, **nicht gespeichert** (keine Spalte) | Freigebender aus dem Token, gespeichert; geaendertes Hauptbuch seit der Pruefung ergibt 409 |
| `POST /{id}/submit` | Setzte `submitted` und **erfand eine ELSTER-Referenz** `ELSTER-<periode>-<id>`; nichts wurde uebermittelt | Haelt eine im ELSTER-Portal erfolgte Uebermittlung mit ihrem **Transferticket** fest; ohne Ticket 422; nur aus `approved` |
| `GET /vat-return` | Fehler ergab eine leere Liste | 503 |
| `_build_vat_return_response` | Las Spalten **nach Position** (`row[14]` war je nach Status Freigabe- oder Uebermittlungszeit, `row[15]` Freigebender, Referenz oder Notiz) | Zuordnung ueber Spaltennamen |
| ELSTER-XML | „gemaess offiziellem Schema“; Kz35/36 als Umsaetze 19 %/7 % (tatsaechlich andere Steuersaetze), Bemessungsgrundlagen mit Cent, Quartal als Monat | Kennzahlen aus der Berechnung, Bemessungsgrundlagen volle Euro, Steuer mit Cent, Zeitraum 01–12/41–44; ehrlich als Datenaustausch beschrieben (ERiC ist nicht angebunden) |

## Berechnung (`app/finance/ustva.py`)

Ein Steuerschluessel nennt Erloeskonto, Umsatzsteuerkonto, Vorsteuerkonto und die Kennzahl (live: 2 = 7 % → 86,
3 = 19 % → 81, 8/9 = Vorsteuer → 66). Bemessungsgrundlage = Haben−Soll der Erloeskonten, Umsatzsteuer =
Haben−Soll der USt-Konten, Vorsteuer = Soll−Haben der Vorsteuerkonten, je gebuchter Periode des Zeitraums
(Monat oder Quartal). Gutschriften mindern dadurch von selbst.

**Klaerung statt Annahme** (eine Anmeldung wird nicht angelegt):

- bebuchter Schluessel ohne Kennzahl;
- Konto, das Schluesseln mit verschiedener Kennzahl oder verschiedenem Satz gehoert;
- Schluessel mit Umsatz- **und** Vorsteuerkonto oder Reverse Charge (§ 13b, innergemeinschaftlicher Erwerb):
  braucht zwei Kennzahlen, die ein Schluessel heute nicht tragen kann;
- Umsatzsteuer einer Kennzahl passt nicht zu Satz × Bemessungsgrundlage (Toleranz 1 € bzw. 0,2 %).

## Datenbank

`vat_return_bearbeiter_20261027`: Spalten `calculated_by`, `validated_by`, `approved_by`, `approved_at`,
`submitted_by`, `elster_transferticket`; Vorgabe von `status` `'draft'` → `'calculated'`; Pruefbedingung
`ck_vat_returns_ablauf` (Status nur calculated/validated/approved/submitted, freigegeben nur mit Freigebendem,
uebermittelt nur mit Uebermittler und Ticket). Live 0 Anmeldungen: kein Abbruchgrund.

## Nachweise

```
pytest tests/test_ustva_wahrheit.py -rs                     -> 15 passed, 0 skipped (valeo_probe, Migrationen zurueckgerollt)
Gegenprobe alter Code (Endpunkte, Compliance, XML)          -> 12 rot
test_security_vat_return_export, test_process_kernel_wave1_contracts -> 39 passed (3 Tests auf den neuen Vertrag umgestellt)
test_gap_fixes_batch1 (UStVA), test_parallel_installation_endpoints gegen migriertes Schema -> 3 passed
alembic heads -> 1; generate_code_inventories --check OK; rls_domain_matrix --check OK; rls_system_read --check OK
OpenAPI: nur /compliance/ustva und /finance/vat-return*; vorbestehende Drift (closing-checklists, biostimulanzien, weighing-tickets) unveraendert
ruff/bandit: keine neuen Befunde (compliance.py hat vorbestehend 4 x E402)
```

**Bestand:** 246 betroffene Module auf dem Zweig (13 Pakete zu 20, nacheinander, mit Speicherpruefung): 8248 bestanden, 22 rot, 6 uebersprungen (auf der Basis ebenso). Die roten Module auf der Basis #79: 21 rot. **Nur im Zweig rot:** `test_gap_fixes_batch1::test_ustva_status_returns_200` — auf dem nicht migrierten Pruefstand fehlt `elster_transferticket`; gegen das migrierte Schema besteht er (siehe oben). 0 neu rot durch Code. Ein erster Lauf in Paketen zu 40 war wegen Speichermangel abgebrochen worden.

**Pruefstand ohne Migration:** Auf `valeo_probe` (Stand `loading_stop_fk_20261023`, wird nicht migriert) antwortet
`GET /compliance/ustva` mit 503, weil `elster_transferticket` fehlt. Mit migriertem Schema (wie in CI) bestehen
`test_ustva_status_returns_200` und `test_ustva_period_filter`.

| Abnahmekriterium | Test |
|---|---|
| Kennzahlen aus den Konten der Schluessel, Gutschrift mindert, anderer Monat/Mandant/Entwurf zaehlt nicht | `test_kennzahlen_aus_den_konten_der_steuerschluessel` |
| Quartal; ungueltiger Zeitraum 422 | `test_quartal_und_ungueltiger_zeitraum` |
| Klaerungen statt Annahmen, keine Anmeldung | `test_was_sich_nicht_zuordnen_laesst_ist_eine_klaerung` (4) |
| Ablauf mit Bearbeitern aus dem Token, Ticket gespeichert, keine Doppel-Uebermittlung, fremder Mandant 404 | `test_ablauf_speichert_bearbeiter_und_transferticket` |
| Freigabe nach geaendertem Hauptbuch 409 | `test_freigabe_nach_geaendertem_hauptbuch_wird_abgewiesen` |
| Ohne gepruefte Identitaet 403 | `test_ohne_gepruefte_identitaet_kein_schritt` |
| Datenbank haelt den Ablauf fest | `test_datenbank_haelt_den_ablauf_fest` |
| Compliance-Status: uebermittelt nur mit Ticket, Mandant getrennt, Frist | `test_compliance_status_meldet_uebermittlung_nur_mit_transferticket`, `test_frist_am_wochenende_verschoben` |
| XML-Kennzahlen wie im Formular | `test_xml_kennzahlen_wie_im_formular` |
| Lesefehler 503 statt Null oder leerer Liste | `test_lesefehler_ist_503_keine_null` |
| Mandant und Bearbeiter aus dem Token, keine Kontoheuristik | `test_mandant_und_bearbeiter_aus_dem_token` |

## Offen

- **Masken (Codex, Studio):** Auf dieser Basis sind `finance/ustva` und `export/ustva` generische Listen
  (`NativeListPage`) ohne Berechnen/Pruefen/Freigeben/Uebermitteln. Die Spalten von `finance/ustva`
  (`grunddaten`, `umsatz`, `berechnung` …) gibt `/finance/vat-return` nicht her. Auf `origin/main` ist
  `export/ustva` (Navigation) eine Attrappe mit Handeingabe und pauschal 19 %. Eine Studio-Maske fuer den Ablauf
  fehlt.
- **Abschluss-Checkliste TAX-001** (`closing_checklist_validation.py`, Codex-Bereich) zaehlt Anmeldungen in
  `calculated/validated/submitted`, nicht `approved`.
- **ERiC** ist nicht angebunden; Steuernummer und Finanzamt des Mandanten stehen nicht im Stamm (XML ohne Steuernummer).
- **Zwei Kennzahlen je Schluessel** (§ 13b, innergemeinschaftlicher Erwerb, Einfuhr) braucht der Tax Rules Service;
  bis dahin Klaerung.
