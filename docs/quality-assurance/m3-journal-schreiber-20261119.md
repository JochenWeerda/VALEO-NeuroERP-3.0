# M3: Journal nur über den Buchungsdienst (19.11.2026)

Meilenstein M3 (vollständige Fibu), Integrität. `FinanceTransactionService` ist der kanonische Schreibweg ins
Journal: Periodensperre, eigene buchbare Konten, exakte Beträge, Belegbezug, lückenlose Sequenz und Hash-Kette.

## Ergebnis

Die Ratsche `tests/test_journal_schreiber_ratsche.py` stand bei **9** Dateien, die roh per SQL in
`domain_erp.journal_entries` / `journal_entry_lines` schrieben. Sie steht jetzt bei **0**; die Liste bleibt leer.

## Befunde und Änderungen

| Weg | Befund | Änderung |
|---|---|---|
| Abgrenzung/Rückstellung `POST /accruals-provisions/{id}/post` | Kopf `posted` **ohne Buchungszeile**, ohne Periodenprüfung, Sequenz, Hash | Dienst (Soll/Haben, Stichtag Periodenende, Bezug `ABGR-<id>`), Kontrollprüfung der manuellen Hauptbuchbuchung (FIN-CONTROL-001) |
| Periodenabschluss `FinanceClosingService.run` | INSERT in Spalten `closing_type`/`created_by`, die es nicht gibt; das verschluckte `except` ließ eine abgebrochene Transaktion zurück → `/closing/run` gelang nie | kein Scheinkopf; Abschluss = Salden + Sperre |
| Lagergeld `POST /storage-fees/run` | Forderung an Erlös direkt, **ohne Umsatzsteuer und offenen Posten**, Konten selbst angelegt | Direktbuchung entfernt, `post_to_ledger=true` → 422 |
| Offene Posten `/finance/open-items` | Lesequelle über den Suchpfad = verwaister Speicher `public.offene_posten` (**leer**); alle Buchungen, Bankabgleich, Mahnwesen schreiben `domain_erp`. Ausgleich buchte roh auf **Kontonummern statt IDs**, Status wurde nicht geschrieben, Debitoren und Kreditoren gleich | Lesen fest aus `domain_erp.offene_posten` (auch Screen-Summary, Monitoring, Abschluss-Checkliste); Suche nur über vorhandene Spalten; manuelle Schreibwege (Anlegen, Ändern, Löschen, Ausgleich, Sammelausgleich, Storno) entfernt – kein Aufrufer |
| Buchungsvorlagen `POST /booking-templates/{id}/apply` | roh, ohne Periodenprüfung, Konten des gemeinsamen Kontenrahmens (`system`), auf die alle Mandanten buchten | Dienst; eigenes Konto je Nummer, Belegbezug Pflicht; Steuerschlüssel, Kosten-/Profitcenter, Bezug je Zeile bleiben (Dienst übernimmt sie jetzt) |
| Massenimport `POST /bulk-journal-import/csv` | fehlendes Konto rollte mitten in der Schleife zurück, danach weitere Zeilen; jeder Auditeintrag committete halb | Dienst, alles oder nichts; Buchungsdatum in der Periode; Bezug Beleg → Belegnummer → Abdruck der freigegebenen Datei |
| Bestandskorrektur, Schwund, Inventur | buchten die **Menge (t) als Eurobetrag**, Konten selbst angelegt | keine Buchung ohne verifizierte Bewertung (wie Produktion); Bestand wird gebucht, `valuation_missing` gemeldet |
| Konnektorläufe Lohn/Anlagen | Buchung und Storno roh; Audit committete halb; Storno scheiterte an geschlossener Ursprungsperiode | Dienst (`create`+`post`, `reverse`); Storno in die laufende offene Periode |
| POS-Tagesabschluss | roh, Kassenkonten selbst angelegt | Dienst; Konten und Periode **vor** dem TSE-Abschluss geprüft |
| Buchungsdienst selbst | ORM kannte `journal_entries.period` nicht: **jede Buchung über den Dienst blieb ohne Periode** (gewachsen 22 von 23) – UStVA und Periodenabschluss filtern auf `period` und sahen sie nicht | Dienst setzt die Periode (Anlage: Buchungsmonat, Storno: laufender Monat); Migration `journal_periode_nachfuellen_20261119` füllt Altbuchungen aus `posting_date` (Periode nicht Teil der Hash-Kette). Kontierungszusätze (Steuerschlüssel, Kosten-/Profitcenter, Bezug) übernimmt der Dienst je Zeile und im Storno |

## Prüfung

Gemeinsamer Prüfstand `valeo_probe` (frisch aus main). Neue Tests gegen echtes Schema, zurückgerollt:
`test_abgrenzung_bucht_ueber_dienst.py`, `test_konnektorlauf_bucht_ueber_dienst.py`; angepasst u. a.
`test_rls_shared_booking_templates.py` (eigene Konten), `test_buchung_nicht_still.py`, `test_kontosperre_meldung.py`,
`test_studio_debtor_sql_channels.py` (OPs im Nebenbuch), `test_offene_posten_rollen_vertrag.py`.

## Offen

- **POS-Umsatzsteuer:** Der Tagesabschluss bucht den Bruttoumsatz auf 8400 ohne Steuer. `pos_fiscal_transactions`
  speichert keine Beträge je Steuersatz; die Trennung braucht die Sätze aus dem Kassiervorgang (Kasse: Codex zuerst,
  FIN-CONTROL-001). Übergabe: `docs/agent-ops/handshakes/claude-an-codex-pos-umsatzsteuer-20261119.md`.
- **Lagergeld-Abrechnung** als Ausgangsrechnung an den Einlagerer (DocFlow) – bis dahin wird Lagergeld berechnet,
  aber nicht gebucht.
- **Bestandsbewertung** (Menge × Wert) für Korrektur und Inventur.
- **`public.offene_posten`** per Migration entfernen, sobald #157 (S5) gemergt ist; dann auch
  `journal_periode_nachfuellen_20261119` hinter die S5-Migration hängen (ein Kopf).
- Migration geprüft in zurückgerollter Transaktion: frisch 0/0, gewachsen 22 → 0 ohne Periode, keine Abweichung vom Buchungsmonat.
- Saldenvortrag und Jahresabschlussbuchung als eigene Fachaktionen.
