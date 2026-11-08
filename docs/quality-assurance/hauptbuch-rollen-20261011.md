# Hauptbuch: Rollen vor der Datenbank

Stand: 2026-10-11 · Slice `HAUPTBUCH-ROLLEN-20261011` · Befund aus
[Offene Posten: Rollen](offene-posten-rollen-20261011.md)

## Befund

Vermessung aller Finanzwege am 11.10.2026 (Abhängigkeitsbaum jeder Route, nicht Textsuche):

| | Wege |
|---|---|
| Finanzwege gesamt | 413 |
| prüfen eine Rolle | 56 |
| prüfen keine Rolle, lesend | 182 |
| prüfen keine Rolle, schreibend | 175 |

Dieser Slice schließt den Kern: die 54 Wege des Hauptbuchs. Wer angemeldet war, konnte dort buchen,
stornieren, Konten löschen, Perioden öffnen und Buchungen in Masse einspielen.

## Entscheidung

Vorgabe des Auftraggebers: „Was nicht einfach läuft, läuft einfach nicht." Eine Regel für alle neun
Dateien, mit genau einer Ausnahme beim Lesen:

| Zugang | Rollen | Wege |
|---|---|---|
| Lesen (`finance_read`) | `FINANCE_LESEN`, `FINANCE_BEARBEITEN`, `FINANCE_ADMIN`, `admin`, `manager` | Buchungen, Konten und Salden, Perioden, Geschäftsjahre, Vorlagen, periodische Buchungen, Kontenplan prüfen und nach DATEV ausgeben |
| Kontenplan lesen (`kontenplan_read`) | wie Lesen, dazu `EINKAUF_*` | Kontenplan: Liste und einzelnes Konto |
| Bearbeiten (`finance_write`) | `FINANCE_BEARBEITEN`, `FINANCE_ADMIN`, `admin`, `manager` | Buchung erfassen, ändern, buchen, stornieren; Konto anlegen und ändern; Vorlage anlegen, ändern, anwenden; periodische Buchung anlegen, sperren, ausführen |
| Leitung (`finance_admin`) | `FINANCE_ADMIN`, `admin` | löschen (Buchung, Konto, Vorlage, periodische Buchung); Periode anlegen, ändern, abschließen, öffnen, sperren; Geschäftsjahr anlegen; Buchungsimport aus CSV |

**Warum die Buchhaltung selbst bucht und storniert:** Das ist ihre tägliche Arbeit. Eine Buchhaltung,
die nur Entwürfe anlegen darf, arbeitet am System vorbei. Ein Storno bleibt als Gegenbuchung im
Journal sichtbar.

**Was der Leitung bleibt:** alles, was sich nicht durch eine Gegenbuchung zurücknehmen lässt –
löschen, Perioden sperren und öffnen, ein Geschäftsjahr anlegen, der Massenimport.

**Warum der Einkauf den Kontenplan liest:** Der Rechnungseingang (`pages/einkauf/rechnungseingang.tsx`)
kontiert damit. Salden, Buchungen und die Kontenverwaltung unter `/accounts` liest der Einkauf nicht.

Die Rolle wird **vor** dem ersten Datenbankzugriff geprüft (Abhängigkeit am Dekorator).

## Geänderte Dateien

- `app/auth/finance_roles.py` – `kontenplan_read` (additiv), Regel im Kopf ergänzt
- nur Dekoratoren und ein Import in `journal_entries.py`, `accounts.py`, `chart_of_accounts.py`,
  `accounting_periods.py`, `finance_period.py`, `bulk_journal_import.py`, `booking_templates.py`,
  `periodische_buchungen.py`, `fibu_geschaeftsjahre.py`
- `tests/test_hauptbuch_rollen_vertrag.py` (neu)
- vier Testdateien mit eigener Mini-Anwendung bekommen einen Nutzer mit Finanzrolle:
  `test_api_smoke_waves.py`, `test_booking_templates_api.py`, `test_chart_of_accounts_api.py`,
  `test_process_kernel_wave81_journal_blockchain_anchors.py`

## Nachweis

| Prüfung | Ergebnis |
|---|---|
| `tests/test_hauptbuch_rollen_vertrag.py` – 13 Rollen × 54 Wege, ohne Anmeldung, Vollständigkeit je Datei, Einkauf nur Kontenplan | 766 bestanden |
| 57 Testdateien, die diese Wege oder Module berühren (Prüfstand `valeo_probe`) | 1616 bestanden, 3 übersprungen, 1 erwartet rot |
| Schnittstellenbeschreibung der 42 betroffenen Pfade gegen `docs/schnittstellen/openapi.json` | keine Abweichung |
| Ruff auf den zehn geänderten Dateien unter `app/` | keine neue Meldung gegenüber dem Stand davor |

Der Vertrag fällt rot, sobald ein neuer Weg in einer der neun Dateien ohne Zugangsklasse dazukommt.

Keine Sichtprüfung: Im Entwicklungsbetrieb trägt der Dev-Nutzer `admin`; die Masken verhalten sich
dort unverändert.

## Betrieb

Vor einer Inbetriebnahme im Anmeldedienst prüfen: Buchhaltung `FINANCE_BEARBEITEN`, Finanzleitung
`FINANCE_ADMIN`, Prüfer und Steuerberater `FINANCE_LESEN`. Wer den Rechnungseingang kontiert, braucht
eine `EINKAUF_*`- oder Finanzrolle.

## Offen

- **303 Finanzwege ohne Rolle** bleiben, 145 davon schreibend. Größte Blöcke: `finance_actions` (15 schreibend, teils Codex), `fibu_connectors` (8),
  `kostenrechnung` (8), `closing_checklists` (6), `finance_stammdaten` (6), `fibu_stammdaten` (6),
  `auto_matching` (5), `billing_batch` (5).
- **Stammdaten, die andere Bereiche lesen** (Steuerschlüssel, Zahlungsbedingungen, Wechselkurse,
  Debitoren, Kreditoren): Dort muss das Lesen breit bleiben; nur das Schreiben gehört der Buchhaltung.
- **Kontenplan nimmt den Mandanten aus der Abfrage:** `chart_of_accounts.py` liest `tenant_id` als
  Query-Parameter mit Vorgabewert, nicht aus dem Mandantenkontext. Wer lesen darf, kann damit den
  Kontenplan eines anderen Mandanten anfragen. Eigener Slice – das ist Mandantentrennung, keine Rolle.
- **Startseite:** `lib/api/dashboard.ts` liest die Buchungen für eine Kennzahl. Ohne Finanzrolle
  bleibt sie leer; ob die Kachel das sagt, ist nicht geprüft.
