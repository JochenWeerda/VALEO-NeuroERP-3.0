# Übergabe Claude Code — 06.10.2026, vor Windows-Neustart

Alles Eigene ist committet und gepusht. Letzter eigener Commit: `6f2888662`.
Nichts von mir liegt unkommittiert im Arbeitsbaum. Das unkommittierte WIP dort
gehört **anderen Agenten** (geänderte `h1`-Klassen, Card-Farben, Inventare) —
beim Weitermachen nicht mitstagen.

## Das Erste nach dem Neustart

**Der Docker-Dienst war gestoppt** (`com.docker.service`, StartType `Manual`), der
Daemon antwortete nicht, PostgreSQL war nicht erreichbar. Ein `Start-Service` ist an
fehlenden Rechten gescheitert, das Starten von `Docker Desktop.exe` hat den Dienst
nicht hochgezogen. Nach dem Neustart zuerst Docker Desktop starten und prüfen:

```bash
python -c "from sqlalchemy import create_engine; create_engine('postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe').connect(); print('OK')"
```

## Offene Schuld: der Nachweis für BEWERBUNG-EINWILLIGUNG-20261006

Der Slice ist **gebaut und gepusht** (`b7b6a042c`), aber **nicht geprüft** — die
Datenbank war weg. Im Workboard steht er deshalb weiter als *in Arbeit*. Nachzuholen,
in dieser Reihenfolge:

```bash
# 1. Schema hochziehen — frisch UND gewachsen
DATABASE_URL=postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe \
  python -m alembic upgrade head
DATABASE_URL=postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp \
  python -m alembic upgrade head

# 2. Die 42 Verträge
DATABASE_URL=postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe \
  python -m pytest tests/test_bewerbung_einwilligung_vertrag.py -q --no-cov

# 3. Nachbarschaft (dürfen nicht kippen)
DATABASE_URL=…/valeo_probe python -m pytest \
  tests/test_bewerbung_loeschlauf_vertrag.py \
  tests/test_bewerbermanagement_ordnung_vertrag.py \
  tests/test_personal_zerlegung_vertrag.py -q --no-cov     # waren 105 passed

# 4. Die fünfte Ratsche (braucht die DB)
python scripts/check_table_references.py                    # Schwelle lebend = 1
```

Einziger Alembic-Head: `bewerbung_einwilligung_20261006`. Ist er hochgezogen, dann:
QA-Doku `docs/quality-assurance/bewerbung-einwilligung-20261006.md` — der
Warnkasten unter „Nachweis" **ersetzen** durch die wirklichen Zahlen; offenen Punkt 1
dort streichen; in `bewerbung-loeschlauf-20261006.md` Punkt 4 den Satz „Der Nachweis
dieses Folgeslices ist noch nicht gelaufen" entfernen; Workboard-Abschnitt auf
*abgeschlossen* setzen.

**Mögliche Stolpersteine in diesen Verträgen** (geschrieben, nie gelaufen):
`domain_hr.applications.tenant_id` ist `VARCHAR(64)`, meine neuen Tabellen führen
`VARCHAR(36)` — kein FK darauf, also unkritisch. Der FK `fk_beweinw_bewerbung` geht
auf `domain_hr.applications.id` (`VARCHAR(36)`), das passt. Die Aufräumreihenfolge in
`aufraeumen()` löscht Verzeichnis vor Bewerbungen.

## Was zuletzt fertig wurde (alles gepusht)

| Commit | Slice |
| --- | --- |
| `b9a71eab4` | BEWERBUNG-LOESCHLAUF-20261006 — Löschlauf, Frist, Protokoll ohne Personenbezug. 52 Verträge grün, fünf Ratschen grün. |
| `b7b6a042c` | BEWERBUNG-EINWILLIGUNG-20261006 — Erteilen/Widerrufen, Verzeichnis als Nachweis. **Nachweis offen.** |
| `6f2888662` | FRONTEND-INITIALDATA-MOUNTFETCH-20261006 — 199 Stellen, neue Ratsche, 8 Vitest-Verträge grün, `tsc` 0 Fehler. Braucht keine DB. |

## Zwei Dinge, die ich unterwegs repariert habe

* **Entwicklungs-DB-Drift:** `domain_shared.jobs` und `job_artifacts` fehlten in
  `valeo_neuro_erp`, obwohl `job_runner_tables_repair_20260625` in `alembic_version`
  steht. Mit dem **wörtlichen** SQL dieser Revision nachgezogen (idempotent). Falls
  die DB neu aufgesetzt wird: nicht nötig, eine frische Installation hat sie.
* **Wörterbücher sind englisch:** `gobd_loeschsperren.status` = `ACTIVE/RELEASED/
  EXPIRED`, `shifts.status` = `planned/cancelled`. Ein deutscher Vergleichswert
  trifft nie und fällt **still** aus. Steht als Gedächtniseintrag.

## Nächste Schritte danach (Reihenfolge ist ein Vorschlag)

1. Den ausstehenden Nachweis (oben) — **vor** allem Neuen.
2. Offene Punkte aus `bewerbung-einwilligung-20261006.md`: Maske für Frist/
   Trockenlauf/Widerruf; Selbstbedienungs-Widerruf für Bewerbende (Art. 7 Abs. 3
   meint auch Zugänglichkeit); versionierte Einwilligungserklärung.
3. `scripts/check_initial_data.py` in `.github/workflows/quality-gate.yml`
   verdrahten — **erst prüfen, ob Codex die Datei noch geclaimt hat**
   (Tabellenkatalog-Drift-Evidenz, `d18e4d190`).
4. Der letzte lebende Leerverweis: `domain_shared.notifications` in `compat.py`.
   Achtung: `compat.py` wurde am 06.10.2026 von einem anderen Agenten angefasst
   (`1a77ee718`).
5. Zwei Tabellen für einen Begriff: `domain_crm.crm_consents` vs.
   `crm_contact_consents` — die zweite migriert aus der ersten, die erste bleibt
   stehen.
6. `Promise.allSettled` in den Dashboard-Hooks macht aus einem Verbindungsfehler
   einen Umsatz von 0 €; `isError` in den Masken (zweite Hälfte des
   Attrappen-Fehlers).

## Geltende Disziplin (nicht neu, aber leicht zu vergessen)

* Claim im Workboard **vor** dem Code, Push **sofort** nach jedem Slice.
* Schema gegen `valeo_probe` (frisch), Daten gegen `valeo_neuro_erp` (gewachsen).
  Den geteilten Prüfstand **nie** zurücksetzen, während andere arbeiten.
* Geteilter Arbeitsbaum **und** geteilter Index: stagen und committen in **einem**
  Aufruf, vorher `git diff --cached` lesen, hinterher prüfen, dass die eigenen
  Dateien im **eigenen** Commit liegen. Liegt fremdes WIP in derselben Datei: aus der
  HEAD-Fassung heraus stagen (`git hash-object -w` + `git update-index --cacheinfo`).
  **Nie `git stash`.**
* `index.lock` gehört einem anderen Agenten — warten, nicht löschen.
* Keine parallelen, schemaändernden pytest-Läufe.
