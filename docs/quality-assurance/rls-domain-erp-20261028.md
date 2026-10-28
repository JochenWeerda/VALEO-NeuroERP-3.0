---
title: QA RLS-DOMAIN-ERP-20261028
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-28
version: 1.0.0
description: domain_erp Teil 1 unter RLS (sieben Tabellen, Nummern je Mandant, Verbund-FKs); Debitoren-, Export- und FiBu-Connector-Wege mit Mandant aus dem Token und funktionsfaehig.
---

# QA RLS-DOMAIN-ERP-20261028

**Basis:** `claude/standardmandant-abbau-20261028` (#86). Migration `rls_domain_erp_20261028` folgt auf
`rls_nutrient_compositions_20261028`; `alembic heads` zeigt einen Head. Live: alle sieben Tabellen 0 Zeilen.

## Befunde

| Weg | Befund | Korrektur |
|---|---|---|
| `POST /debtors` | Mandant aus dem Rumpf (`DebtorCreate.tenant_id`): Debitor unter fremdem Mandanten anlegbar | Mandant aus dem Token, abweichender Rumpf 403 (wie Kreditoren) |
| `POST /debtors` | `debitors.id` hat keine Vorgabe (frisch und live): **jede Anlage endete mit 500** | ID wird vergeben (uuid7) |
| `GET/PUT/DELETE /debtors/{id}`, `/balance` | ohne Mandantenfilter: fremde Debitoren lesbar, aenderbar, deaktivierbar | Filter auf den Token-Mandanten, fremd 404 |
| Debitoren-/Kreditoren-Saldo | las `amount`, `paid_amount`, `status` — Spalten, die `offene_posten` nicht hat: **immer 500**; Debitoren-OP tragen `kunde_id`, nicht `debtor_id` | gemeinsame Abfrage `app/finance/op_saldo.py`: `offen` (die Spalte, die alle Zahlungs-/Stornowege schreiben), `op_status` offen/teilweise, Mandant, Kontotyp; Debitor ueber `debtor_id` oder seinen Kunden |
| `POST /export/list` | `filter.tenant_id` waehlte den Mandanten des Exports (Debitoren, Kreditoren, Nutzer, Prueflog, Mahnungen eines fremden Mandanten), Kommentar „admin use“ ohne Rollenpruefung | nur der eigene Mandant, fremder Filter 403 |
| `POST /export/list` (CSV) | `TextIOWrapper` schloss beim Verlassen der Funktion den Puffer: **jeder CSV-Export endete mit 500** | `StringIO`, dann UTF-8 mit BOM |
| Export Kreditoren | las Kreditoren-OP mit nicht vorhandenen Spalten (`konto_nr`, `op_betrag`, `saldo`, `mahn_stufe`), Fehler gefangen: **Datei immer leer** | Kreditoren-Stamm wie bei den Debitoren |
| Export Futtermittel/Chargen | Artikel und Chargen **aller Mandanten**, Fehler gefangen (leere Datei) | Mandantenfilter, Fehler nicht mehr verschluckt |
| FiBu-Connector `validate/post/cancel/reverse` | SQL bindet `:tid`, uebergeben wurde `tenant_id`: **alle vier scheiterten immer** (die API-Tests ersetzten den Ablauf durch Attrappen) | Bindungen korrigiert |
| Connector buchen | Zeilen mit unbekanntem Konto liess der Lauf weg (Beleg **unausgeglichen gebucht**), unausgeglichene Belege stillschweigend aus; keine Periodenpruefung; doppelte Belegnummer erst als Datenbankfehler | alles oder nichts: erst alle Belege pruefen (Konto, Soll = Haben, Periode offen, Nummer frei und im Lauf eindeutig), dann buchen; `period` wird gesetzt |
| Connector stornieren | Storno ohne Verweis auf die Ursprungsbuchung, `STorno-`, Zeilen ohne Mandantenfilter, gesperrte Periode erst als Datenbankfehler | `reversed_entry_id`, `STORNO-`, Mandantenfilter, gesperrte Periode 400 |
| Connector Upload | gleicher Idempotenzschluessel lieferte den Lauf, parste ihn aber **neu**: doppelte Positionen, Status zurueck auf PARSED — ein gebuchter Lauf liess sich erneut buchen | bestehender Lauf wird unveraendert gemeldet; unbekanntes/fremdes Profil 404 |
| Connector Profil | Einstellungen des Profils ohne Mandantenfilter gelesen (fremde Zuordnung) | Filter |
| `fibu_connector_run_items` | ohne Mandant; Positionen lasen nur nach Lauf | Mandant aus dem Lauf, Verbund-FK `(run_id, tenant_id)` |

**Schema:** getrennte Policies fuer `domain_erp.bank_accounts`, `creditors`, `debitors`, `dunning_notices`,
`gift_cards`, `open_items`, `fibu_connector_run_items`; `tenant_id` NOT NULL mit Vorgabe aus dem Kontext.
Kreditoren- und Debitorennummern waren **systemweit** eindeutig (der zweite Mandant konnte 10001 nicht vergeben) und
sind es jetzt je Mandant; die gewachsene Datenbank hatte die alten Constraints verloren, teils lag die Mandanten-
Eindeutigkeit schon als Index vor — die Migration sucht nach Definition, nicht nach Namen. `debitors.customer_id`
verweist ueber `(customer_id, tenant_id)` (SET NULL nur auf die Verweisspalte). Ausnahmen 76 → 69.

## Nachweise

```
pytest tests/test_rls_domain_erp.py                                   -> 21 passed, 0 skipped (valeo_probe)
Gegenprobe alter Code ohne Migration                                  -> 21 rot
Gegenprobe alter Code mit Migration                                   -> 8 rot (alle Fachwege), 13 Schema gruen
49 betroffene Bestandsmodule (3 Pakete zu 20, Speicherpruefung)      -> 0 neu rot
   (4 rot wie auf der Basis: test_meridian_beleg_systemweit; 2 Tests auf die neuen Signaturen umgestellt:
    create_debtor mit Token-Mandant, Connector-API-Attrappe kennt find_run)
RLS-Suite + Fallback-, Identitaets-, Urheber- und Kontenplan-Vertrag            -> 660 passed, 0 skipped
alembic heads 1; RLS-Inventar/Matrix/Systemlesen/Rollout und Code-Inventare neu erzeugt
```

## Offen (Teil 2)

- `domain_erp.offene_posten` (30 Schreiber, live 25 Zeilen in 2 Mandanten), `chart_of_accounts` (28 `system`-Zeilen),
  `policy_rules` bleiben zurueckgestellt.
- `dunning_notices.op_id`/`debtor_id` ohne Fremdschluessel (folgt mit `offene_posten`).
- **Klasse „Mandant aus dem Rumpf“:** dieselbe Form wie bei Debitoren/Export steht noch in `background_jobs`,
  `blockchain_runtime`, `supply_chain_blockchain`, `e2e_chain`, `process_sla`, `reporting_api`, `tenant_limits`,
  `users`, `whatsapp_webhook`, `crm_consents` (`payload.tenant_id or tenant_id`) — eigener Slice mit Vertragstest.
- Buchungen entstehen an 12 Stellen per direktem `INSERT INTO domain_erp.journal_entries`; der Connector prueft
  jetzt Periode und Konten selbst, ein zentraler Buchungsweg (Hash-Kette, Nummernkreis) fehlt weiterhin.
