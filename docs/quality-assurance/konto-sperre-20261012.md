# Kontosperre

Stand: 2026-10-12 · Slice `KONTO-SPERRE-20261012` · offener Punkt aus
[Kontenplanpflege nach gängiger Praxis](kontenplan-praxis-20261012.md)

## Befund

Ein bebuchtes Konto bleibt erhalten; für ein Konto, das nicht mehr benutzt werden soll, nennt die
Praxis die Sperre. Das Konto hatte kein solches Feld. „Manuelle Buchungen erlauben"
(`allow_manual_entries`) stand in Schema und Maske, aber nicht in der Tabelle: Die Maske zeigte
„Manuell: Ja/Nein" und speicherte nichts.

## Entscheidung

**Eine Durchsetzungsstelle.** Rund zwanzig Wege schreiben Buchungszeilen (Journal, Vorlagen, Import,
Eingangsrechnung, Wareneingang, Lagergeld, Gutschrift, Ausgleich, Konnektoren), viele mit rohem SQL.
Die Sperre sitzt deshalb an der Tabelle: Ein Trigger an `domain_erp.journal_entry_lines` lehnt jede
neue Zeile auf ein gesperrtes Konto ab, ebenso das Umhängen einer Zeile dorthin. Ein neuer
Buchungsweg kann die Sperre nicht vergessen.

| | |
|---|---|
| Feld | `domain_erp.chart_of_accounts.posting_blocked`, `NOT NULL`, Vorgabe `false` |
| Sperren, entsperren | über „Konto ändern" – Kontenpflege (`KONTENPLAN_PFLEGE`, Finanzleitung); gemeinsamer Rahmen zusätzlich `KONTENRAHMEN_PFLEGE` |
| Wirkung | keine neue Buchungszeile, weder von Hand noch automatisch; bestehende Zeilen bleiben und lassen sich weiter ändern, solange sie auf ihrem Konto bleiben |
| Sichtbarkeit | das Konto bleibt aktiv und im Kontenplan, Spalte „Buchbar: Gesperrt" |
| Bebuchtes Konto | lässt sich sperren (deaktivieren weiterhin nicht) |
| Manuelle Buchung | `POST /journal-entries` prüft vorab und antwortet 409 „Konto … ist fuer Buchungen gesperrt." – bevor etwas angelegt wird |

**Bewusst in Kauf genommen:** Auch eine automatische Buchung scheitert an einem gesperrten Konto.
Das ist die Bedeutung der Sperre (so auch in SAP und Dynamics); Maske und Handbuch sagen es vor dem
Sperren. Ebenso scheitert das Storno einer Buchung, solange ihr Konto gesperrt ist – das Storno ist
eine neue Buchung.

## Migration

`konto_sperre_20261012` auf `audit_urheber_20261011` (einziger Head davor und danach). Additiv:
eine Spalte mit Vorgabewert, eine Funktion, ein Trigger. Die Rücknahme entfernt alle drei.

| Datenbank | Ergebnis |
|---|---|
| `valeo_probe` (frisches Schema) | Migration gelaufen; Spalte und Trigger vorhanden |
| `valeo_neuro_erp` (gewachsene Daten) | Migration gelaufen; 29 Konten, keines gesperrt; Trigger vorhanden |

## Geänderte Dateien

- `alembic/versions/konto_sperre_20261012.py` (neu)
- `app/infrastructure/models/__init__.py` (Spalte), `app/api/v1/schemas/finance.py` (`Account`,
  `AccountUpdate`)
- `app/api/v1/endpoints/chart_of_accounts.py` (Meldung), `app/api/v1/endpoints/journal_entries.py`
  (Vorabprüfung)
- `tests/test_kontenplan_mandant_vertrag.py` – acht neue Fälle
- `packages/frontend-web/src/pages/finance/chart-of-accounts.tsx`,
  `packages/frontend-web/src/lib/services/finance-service.ts`
- `docs/benutzerhandbuch/finanzbuchhaltung.md` (Abschnitt „Konten, die nicht mehr benutzt werden
  sollen")
- `docs/admin/table-catalog.json`/`.md`, `docs/admin/migration-inventory.md`,
  `docs/schnittstellen/openapi.json` – nur die eigenen Zeilen

## Nachweis

| Prüfung | Ergebnis |
|---|---|
| `tests/test_kontenplan_mandant_vertrag.py` gegen `valeo_probe` | 33 bestanden (acht neu) |
| 46 Testdateien rund um Kontenplan, Journal und Buchungszeilen | 2107 bestanden, 3 übersprungen, 1 erwartet rot |
| `generate_openapi.py --check` | aktuell |
| `tsc --noEmit`, ESLint auf Maske und Finanzdienst | ohne Fehler |
| Entwicklungsdatenbank, in zurückgerollter Transaktion: Konto 1400 sperren, Buchungszeile einfügen | `ERROR: Konto 1400 ist fuer Buchungen gesperrt`; nichts zurückgeblieben |

Die acht neuen Fälle: bebuchtes Konto sperren und in der Liste sehen; rohes `INSERT` auf das
gesperrte Konto scheitert mit der Meldung; bestehende Zeilen bleiben änderbar; Umhängen auf das
gesperrte Konto scheitert; nach dem Entsperren wird wieder gebucht; Buchhaltung sperrt nicht,
Kontenpflege schon; gemeinsamer Rahmen nur mit Rahmenrecht; manuelle Buchung antwortet 409 mit
Begründung, bevor etwas angelegt wird.

**Nicht geprüft: die Maske im Browser.** Im geteilten Arbeitsbaum liegt nicht committete Arbeit eines
anderen Agenten (`app/core/tenant_binding.py`, `app/auth/*`, Slice `SYSTEM-TENANT-BOUNDARY-20261012`),
die das laufende Entwicklungs-Backend lädt: Es lehnt den Dev-Token an jedem Weg mit 403 ab
(„Verified subject and unambiguous ERP tenant are required"). Die Maske ist damit über Typprüfung und
Lint belegt, nicht über eine Sichtprüfung.

**Tabellenkatalog:** nicht blind aus `valeo_probe` erzeugt (dort fehlen Tabellen, die nur
`create_all` anlegt), sondern HEAD-Fassung plus die Struktur von `chart_of_accounts` und die
Codebezüge. Dabei fiel bei `domain_crm.customers` ein Bezug weg, der schon vorher nicht mehr zum Code
passte.

## Offen

- **Sichtprüfung der Maske**, sobald der Dev-Token wieder angenommen wird.
- **Die übrigen Buchungswege melden die Sperre als Datenbankfehler** (meist 500 mit dem Satz des
  Triggers im Text). Verständlich abgelehnt wird nur die manuelle Buchung.
- **Wo ist das Konto hinterlegt?** Vor dem Sperren zeigt nichts, in welchen automatischen Buchungen
  ein Konto steht.
- **`allow_manual_entries` und `currency`** stehen weiter im Schema und werden nicht gespeichert; das
  Anlegen-Formular schickt beide mit. Die Währung zeigt die Maske als Spalte, obwohl es sie am Konto
  nicht gibt.
- **Zahlenkorrektur zu `kontenplan-praxis-20261012.md`:** Dort standen 27 und 818 bestandene Fälle;
  gemessen waren es 25 und 820 (Summe 845 stimmte). In diesem Commit berichtigt.
