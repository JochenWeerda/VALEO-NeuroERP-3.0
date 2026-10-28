---
title: QA RLS-DOMAIN-OPS-20261028
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-28
version: 1.0.0
description: RLS-Domain ops Teil 1 auf valeo_probe abgenommen - Kontrakte und PCN-Meldungen getrennt, Vorgaben aus dem Kontext, Eindeutigkeit je Mandant, Kinder ueber Verbundschluessel; Teil 2 (Tabellen ohne Mandant) mit Live-Befund.
---

# QA RLS-DOMAIN-OPS-20261028

**Basis:** `claude/urheber-aus-token-20261028` (#83). Migration `rls_domain_ops_20261028` folgt auf
`service_anfragen_20261027`; `alembic heads` zeigt einen Head. Keine Datenaenderung.

## Teil 1 (dieser Slice)

| Tabelle(n) | Befund | Entscheidung |
|---|---|---|
| `kon_contract` (live 4), `ops_pcn_meldungen` (live 0) | ohne RLS; Matrix „standardmandant“ waren Fehltreffer (`user_ref="default"` im Kalender, ein Kommentar in `compliance.py`); Schreiber tokengebunden | getrennte Policies, kein `system`-Lesen |
| 17 Tabellen mit Vorgabe `'default'`/`'legacy-unassigned'` | ein vergessener Mandant fiel still auf einen Platzhalter | Vorgabe = Mandant des Kontexts; bestehende Zeilen unveraendert |
| `ops_tank_bestand.artikel`, `ops_versicherungen.vertragsnummer`, `edi_partner.gln`, `edi_nachrichten.nachricht_id` | **systemweit** eindeutig: ein zweiter Mandant mit demselben Artikel scheiterte an der Datenbank | eindeutig je Mandant (auch im ORM) |
| Kontrakt -> Positionen/Bewegungen, Position -> Bewegung, Projekt -> Aufgaben, Anlage -> Protokolle, Prozessinstanz -> Dokumente/Ereignisse, Fahrzeug -> Fuhrparkrechnung | Einzel-FK, Verweis auf Eltern eines anderen Mandanten moeglich | Verbund-FK `(schluessel, tenant_id)`, ON DELETE wie bisher (SET NULL nur auf die Verweisspalte) |

**Gewachsene DB (lesend):** kein fremder Verweis, keine Platzhalterzeile in den Policy-Tabellen: kein Abbruchgrund.
Bestehende Platzhalter (eine Prozessinstanz und 31 EDI-Nachrichten mit `default`, ein Fahrzeug mit `legacy-unassigned`)
bleiben unveraendert; ihre Zuordnung ist eine Datenentscheidung.

## Teil 2 (offen, Live-Befund)

21 Tabellen in `domain_ops` haben **keine** Mandantenspalte; 13 davon tragen live Zeilen: `ops_disposition` 74,
`ops_labor_auftraege` 74, `ops_zertifikate` 61, `ops_labor_proben` 7, `ops_compliance_items` 3, `ops_enni_meldungen`,
`ops_foerderantraege`, `ops_marketing_kampagnen`, `ops_qs_checks`, `ops_zulassungen_register` je 2, `ops_fahrer`,
`ops_saatgut_nachbau`, `ops_sachkunde_register`, `ops_vvvo_register` je 1. Ohne Spalte liest und schreibt jeder Mandant
alles (auch `GET /api/contracts/RV-…`, Rahmenvertraege). Die Spalte einzufuehren heisst, die Zeilen einem Mandanten
zuzuordnen — das ist nicht zu raten (live gibt es zwei echte Mandanten). Ebenso offen: `ops_chargen` (79 Zeilen
`legacy-unassigned`, Dienst-Identitaet) und `reklamationen` (Codex-Claim).

## Nachweise

```
pytest tests/test_rls_domain_ops.py -rs           -> 18 passed, 0 skipped (valeo_app, zurueckgerollt)
Gegenprobe ohne Migration                         -> 18 rot
RLS-Suite + Fallback- + Identitaetsvertrag        -> 568 passed
Inventar/Matrix/Systemlesen/Rollout regeneriert; Ausnahmen 86 -> 84 (Ratsche gesenkt)
127 betroffene Bestandsmodule (Pakete zu 20)        -> 4920 passed, 12 rot, 3 uebersprungen; alle 12 auf der Basis #83 gleich rot
   (test_mcp_local_action_classification 5, test_meridian_beleg_systemweit 4, test_stammdaten_bearbeiten 2,
    test_tourenplanung_definition 1 - Folgen der Studio-Migration), 0 neu rot
```

| Abnahmekriterium | Test |
|---|---|
| Mandantengrenze (eigen ok; fremd und `system` SELECT/INSERT/UPDATE/DELETE gesperrt; kein Wechsel; fail-closed) | `test_mandantengrenze_je_tabelle` (2) |
| kein Verweis auf fremden Eltern, auch nicht umgehaengt | `test_kein_verweis_auf_fremden_eltern` (8) |
| Eltern mit Verweisen behaelt seinen Mandanten | `test_eltern_mit_verweisen_behaelt_seinen_mandanten` |
| Vorgabe ist der Kontext | `test_vorgabe_ist_der_kontext_nicht_default` |
| eindeutig je Mandant | `test_eindeutig_je_mandant_nicht_systemweit` (4) |
| Kontextwechsel/Savepoint, Hintergrund | `test_kontextwechsel_savepoint_hintergrund` |
