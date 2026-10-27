---
title: QA RLS-DOMAIN-MATRIX-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: Nachweis für Inventar, Entscheidungsmatrix, Ausnahmeliste und Policy-Form-Ratsche der offenen RLS-Domains.
---

# QA RLS-DOMAIN-MATRIX-20261027

**Basis:** `claude/rls-p7-guards-20261026` (#63) auf dem Integrationszweig @ c3142eb1d.
Zweig `claude/rls-domains-matrix-20261027`.

## Lieferung

| Datei | Inhalt |
|---|---|
| `scripts/rls_domain_matrix.py` | Matrix je Tabelle: Domain, Ursachen, Modell, Leser/Schreiber, Worker, Identität, Fundstellen Datei:Zeile, Bereinigung, Policy-Vorschlag; `--data` liest die gewachsene DB in einer Nur-Lese-Transaktion |
| `docs/admin/rls-domain-matrix.json` / `.md` | generierte Matrix (214 Tabellen) |
| `docs/admin/rls-domain-data.json` | Datenbefund der gewachsenen DB, Stand 27.10.2026 |
| `docs/admin/rls-exceptions.json` | eingefrorene Ausnahmeliste (214, mit Ursache); `system_lesbar` leer; `altform_hoechstens` 501 |
| `scripts/rls_policy_shape.py` | zulässige Policy-Formen (getrennt / getrennt_system / alt) und Klassifizierung aus `pg_policy` |
| `tests/test_rls_domain_matrix.py` | Matrix aktuell; jede ungeschützte Mandantentabelle ausdrücklich zurückgestellt; keine veralteten Einträge; Obergrenze 214 im Test; Selbsttest der Analyse |
| `tests/test_rls_policy_shape.py` | 13 Negativ- und Positivfälle der Formen; alle RLS-Tabellen des Prüfstands in zulässiger Form |
| `docs/architecture/rls-domaenen-entscheidungsmatrix.md` | Ursachen, Policy-Muster, Matrix je Domain, Reihenfolge, erste Domain |
| `docs/architecture/rls-dienste-identitaet-vorschlag.md` | Architekturvorschlag Dienst-Identität |

Abweichung vom Claim: Die Form-Definition liegt in `scripts/rls_policy_shape.py` und nicht
in `app/core/rls_policies.py`. Migrationen bleiben damit in sich geschlossen und importieren
keinen veränderlichen App-Code. Die Ratsche prüft das Ergebnis in `pg_policy` und nicht,
wie es entstanden ist.

## Nachweise

```
python scripts/pruefstand_db.py --status
  -> vorhanden, Revision loading_stop_fk_20261023 (nicht verändert)
python scripts/rls_inventory.py --check   -> OK (7 Revisionen zurückgerollt eingespielt)
python scripts/rls_rollout.py --check     -> OK
python scripts/rls_domain_matrix.py --data   (LIVE_DATABASE_URL, SET TRANSACTION READ ONLY)
  -> 199 von 214 Tabellen live; A 110, B 51, C 53
python scripts/rls_policy_shape.py        -> {'alt': 501}, keine abweichende
python -m pytest tests/test_rls_domain_matrix.py tests/test_rls_policy_shape.py -q
  -> 18 passed
```

## Ergebnisse

- Die Lücke umfasst **214** Mandantentabellen. Die bisher genannten 110 deckten nur
  Klasse A ab, Klasse B (51) und C (53) fehlten im Rollout.
- Die Ursachen verteilen sich so: standardmandant 62, position 51, referenzdaten 41,
  mandant_nullbar 38, dienst 20, identitaet 2.
- Die gewachsenen Daten sind weitgehend sauber. Blocker sind 49 NULL-Normzeilen (Fütterung),
  28 `system`-Zeilen im Kontenrahmen, `users`/`policy_rules`/`knowledge_objects`,
  8 `default`-Ereignisse in der Outbox und 1 `default`-Schlag im Feldbuch.
- Erste Domain ist **pricing**: 0 Zeilen, kein Worker, Positionsmuster.
  `price_lists.py` filtert Lesen, Ändern und Löschen heute nicht nach Mandant.

## Verbleibende Risiken

- Die Code-Befunde sind heuristisch und dateiweit. Falsch positive Treffer lassen eine
  Tabelle nur warten; falsch negative fängt der Verhaltenstest des Domain-Slices.
- `tests/test_rls_p5_rollout.py::test_alle_rls_tabellen_tragen_genau_die_mandantenpolicy`
  (Codex-Besitz) verlangt für jede RLS-Tabelle genau `tenant_isolation`. Er wird rot, sobald
  ein Domain-Slice die getrennte Form einführt. Gemeldet im Handshake.
- Der Datenbefund ist eine Momentaufnahme und wird vor jeder Domain-Migration erneuert.
- Klasse D (60 Tabellen ohne Mandant) gehört nicht zu diesem Slice.
