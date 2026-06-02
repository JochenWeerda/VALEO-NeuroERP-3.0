# Runbook — Kundenstamm-Konsolidierung Schritt 5 (Prod-Ausführung)

> Ziel: Die Identitätsbrücke `public.kunden.business_partner_id ↔ business_partners.partner_id`
> in **Produktion** füllen, per FK absichern, die Produktivmasken auf die Domänen-Satelliten
> umstellen und zuletzt die deprecateten Altspalten in `public.kunden` entfernen.
>
> Diese Schritte mutieren Produktivdaten und -schema. **Backup + Freigabe sind Pflicht.**
> Vorarbeiten (Satelliten, Backfill, Deprecation, Brücken-Plumbing) sind bereits ausgerollt
> (Commit `0a68bdeb7`). Fachlicher Kontext: `docs/kunden-konsolidierung.md`.

## Überblick

| | |
|---|---|
| **Betroffene Objekte** | `public.kunden` (+ Satelliten `kunden_adressen/zahlung/external_refs`), `domain_crm.business_partners`, `domain_crm.customers` |
| **Werkzeuge** | `python -m app.services.kunden_merge` (`--apply`, `--bridge-status`, `--format`, `--output`), Alembic |
| **Idempotenz** | `kunden_merge --apply` schreibt nur `exact/strong`-Matches, überschreibt **nie** `kunden_nr` oder eine gesetzte `business_partner_id` |
| **RPO/Rollback** | Pro Phase definiert (siehe unten); FK/Drop sind die einzigen schema-destruktiven Schritte |
| **Wartungsfenster** | Phasen 1–2 online möglich; Phase 3 (FK) kurzer Lock; Phase 6 (Drop) im Fenster |

## Voraussetzungen (Gate)

- [ ] Frisches, **verifiziertes** Prod-DB-Backup (siehe `docs/runbooks/DISASTER-RECOVERY.md`).
- [ ] Freigabe durch Verantwortliche/n eingeholt.
- [ ] Code-Stand enthält Commit `0a68bdeb7` (Brücken-Plumbing) — `alembic heads` zeigt
      `kunden_deprecate_legacy_cols_20260602` (oder neuer).
- [ ] Prod-Verbindung gesetzt: `DATABASE_URL` zeigt auf die Prod-DB
      (`app.core.database.SessionLocal` liest `DATABASE_URL`). Passwort **nicht** in Tickets/Chats.

```bash
# Backup (Beispiel; siehe scripts/backup-db.sh / DR-Runbook)
pg_dump "$DATABASE_URL" -Fc -f "valeo_prod_pre_schritt5_$(date +%Y%m%d_%H%M).dump"
# Integrität prüfen
pg_restore -l "valeo_prod_pre_schritt5_*.dump" | head
```

### Ziel-Verifikation (read-only, IMMER zuerst)

```bash
python - <<'PY'
from app.core.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
print(db.execute(text("SELECT current_database(), current_user, inet_server_addr()::text")).first())
print("alembic head erwartet: kunden_deprecate_legacy_cols_20260602")
print("version:", db.execute(text("SELECT version_num FROM alembic_version")).scalar())
db.close()
PY
```

> **Abbruch**, wenn `current_database()` nicht die erwartete Prod-DB ist.

---

## Phase 1 — Brücke füllen (`kunden_merge`)

### 1.1 Dry-Run + Review (keine Mutation)

```bash
python -m app.services.kunden_merge --format md --output schritt5_dryrun_$(date +%Y%m%d).md
# bzw. maschinenlesbar:
python -m app.services.kunden_merge --format json --output schritt5_dryrun.json
```

**Review-Kriterien (Gate vor `--apply`):**
- `Sicher backfillbar (exact/strong)` = die Zeilen, die geschrieben werden. Plausibilisieren.
- Klasse **`conflict`**: widersprüchliche Schlüssel (z. B. gleiche kunden_nr matcht zwei BP, oder
  USt/Betriebsnummer widersprechen Name+PLZ) → **manuell triagieren**, werden **nicht** auto-geschrieben.
- Klasse **`duplicate_candidate`**: mögliche Dubletten im Stamm → fachlich klären (mergen/ignorieren).
- `orphan_public_kunden`: kein BP-Match → später BP anlegen (nicht Teil von `--apply`).

> Triage-Ergebnis dokumentieren (Ticket-Anhang: der Dry-Run-Report).

### 1.2 Apply (Mutation: schreibt `business_partner_id`)

```bash
python -m app.services.kunden_merge --apply
# Ausgabe: "[APPLY] business_partner_id geschrieben: N, übersprungen: M"
```

- Schreibt **nur** `exact/strong` (`recommended_action = backfill_business_partner_id`).
- `WHERE business_partner_id IS NULL` → idempotent, nicht-überschreibend.
- Bei Unterbrechung gefahrlos erneut ausführbar.

**Rollback Phase 1** (nur die in diesem Lauf gesetzten Brückenwerte zurücknehmen, falls nötig):
```sql
-- VORSICHT: setzt ALLE business_partner_id auf NULL zurück. Nur wenn keine Alt-Verknüpfungen
-- existierten (vor Schritt 5 war coverage 0%). Sonst gezielt per Kunden-Liste aus dem Apply-Log.
-- UPDATE public.kunden SET business_partner_id = NULL WHERE business_partner_id IS NOT NULL;
```

---

## Phase 2 — Readiness prüfen

```bash
python -m app.services.kunden_merge --bridge-status
```

```
- Aktive Kunden:                   <total>
- Verbrueckt (bp_id gesetzt):      <linked>  (<coverage_pct>%)
- Per Match aufloesbar:            <resolvable>   # sollte nach Apply 0 sein
- Unaufloesbar (Orphan):           <unresolved>
- FK-Orphans (bp_id ohne BP):      <fk_orphans>   # MUSS 0 sein
- FK-aktivierbar:                  <fk_ready>      # True erforderlich für Phase 3
```

**Gate für Phase 3:** `fk_orphans = 0`. **`fk_ready = True`** verlangt zusätzlich 100 % Abdeckung
(`linked == total_active`). Ist die Abdeckung < 100 % (Orphans ohne BP), gibt es zwei Wege:
- BPs für Orphans anlegen (fachlich) und 1.2 erneut laufen, **oder**
- FK zunächst **`NOT VALID`** anlegen (Phase 3, Variante B) und später validieren.

---

## Phase 3 — FK aktivieren (Schema, kurzer Lock)

Neue Alembic-Migration anlegen (`down_revision = kunden_deprecate_legacy_cols_20260602`):

```python
def upgrade() -> None:
    # Variante A (nur wenn coverage 100% / fk_ready=True):
    op.execute(
        "ALTER TABLE public.kunden "
        "ADD CONSTRAINT fk_kunden_business_partner "
        "FOREIGN KEY (business_partner_id) "
        "REFERENCES domain_crm.business_partners(partner_id)"
    )
    # Variante B (Teilabdeckung): erst NOT VALID (kein Full-Table-Scan-Lock auf bestehende NULLs),
    # spaeter VALIDATE CONSTRAINT in separatem Schritt:
    # op.execute("... ADD CONSTRAINT ... FOREIGN KEY (...) REFERENCES ... NOT VALID")
    # op.execute("ALTER TABLE public.kunden VALIDATE CONSTRAINT fk_kunden_business_partner")

def downgrade() -> None:
    op.execute("ALTER TABLE public.kunden DROP CONSTRAINT IF EXISTS fk_kunden_business_partner")
```

```bash
python -m alembic upgrade head
python -m alembic current   # zeigt die neue FK-Revision
```

> NULL-`business_partner_id` ist FK-konform (FK erlaubt NULL) — unverbrückte Kunden blockieren die
> Constraint-Anlage nicht; nur **gesetzte** Werte ohne Ziel-BP (= `fk_orphans`) würden sie verhindern.

**Rollback Phase 3:** `alembic downgrade -1` (droppt die Constraint).

---

## Phase 4 — Produktivmasken auf die Brücke umstellen

Bisher additiv vorhanden (Commit `0a68bdeb7`), jetzt verdrahten:

- **Kundenstamm (BP-keyed):** Detail über `GET /api/v1/customers/by-partner/{business_partner_id}/detail`
  bzw. FE-Hook `useKundenDetailByPartner(businessPartnerId)`.
- **CustomerCombobox / kunden-liste (crm-id-keyed):** Identität über
  `GET /api/v1/customers/lookup/resolve?...` bzw. `useKundenIdentity({...})`, dann Satelliten-Detail
  via aufgelöster `kunden_nr` (`useKundenDetail`) oder direkt `by-partner`.

**Gate:** Smoke je Maske (Suche → Öffnen → Adresse/Zahlung/Refs sichtbar). Keine direkten Lesezugriffe
mehr auf `public.kunden`-Altspalten aus den Masken.

---

## Phase 5 — Reader-Fallback entfernen

Die Satelliten-Reader (`BusinessPartnerService.get_customer_address/_payment/_external_refs`) loggen
beim Rückfall auf `public.kunden` `logger.warning(... deprecated)`.

**Gate:** Über einen repräsentativen Zeitraum (z. B. 1–2 Wochen Prod) **0** dieser Warnungen:

```bash
# je nach Log-Sink:
grep -c "Fallback auf public.kunden" <logfile>          # erwartet 0
# oder in der Log-Aggregation nach "deprecated" + "Fallback" filtern
```

Erst dann den Fallback-Code aus den drei Methoden entfernen (Reader liest dann **nur** Satellit).
Bis dahin bleibt der Fallback als Sicherheitsnetz.

---

## Phase 6 — Altspalten droppen (Schema, im Wartungsfenster)

Erst wenn Phase 4 + 5 abgeschlossen sind. Die 30 deprecateten Spalten (7 Adresse, 20 Zahlung,
3 Refs) tragen bereits den `DEPRECATED`-Kommentar (Quelle für die Drop-Liste):

```sql
-- Drop-Kandidaten aus den Kommentaren ableiten:
SELECT a.attname
FROM pg_description d
JOIN pg_attribute a ON a.attrelid = d.objoid AND a.attnum = d.objsubid
WHERE d.objoid = 'public.kunden'::regclass
  AND d.description LIKE 'DEPRECATED 2026-06-02%'
ORDER BY a.attname;   -- erwartet 30 Spalten
```

Neue Migration `... DROP COLUMN`. **Zwingend vorher:**
- Vollständiges Backup (s. o.).
- Bestätigen, dass kein Code mehr diese Spalten liest/schreibt (Grep-Audit `public.kunden`,
  ORM `Kunde`-Model in `app/verkauf/models.py` — falls inzwischen verdrahtet — anpassen).
- `kunden_lookup`-View prüfen: liest Adresse bereits aus `kunden_adressen` (COALESCE-Fallback auf
  `public.kunden` entfällt mit dem Drop → View vorher auf reinen Satelliten-Join umstellen).

```python
def upgrade() -> None:
    # Reihenfolge: zuerst View vom public.kunden-Adressfallback loesen, dann Spalten droppen.
    op.execute("DROP VIEW IF EXISTS public.kunden_lookup")
    op.execute("CREATE VIEW public.kunden_lookup AS ... -- ohne public.kunden-Adressspalten")
    for col in [ ... 30 Spalten ... ]:
        op.execute(f"ALTER TABLE public.kunden DROP COLUMN IF EXISTS {col}")
```

**Rollback Phase 6:** nur über Restore aus Backup (DROP COLUMN ist nicht rücknehmbar). Daher Wartungsfenster + Backup-Pflicht.

---

## Abnahme / Verifikation (End-to-End)

```sql
-- Brücken-Abdeckung
SELECT count(*) FILTER (WHERE business_partner_id IS NOT NULL) AS verbrueckt,
       count(*) AS gesamt
FROM public.kunden WHERE coalesce(geloescht, FALSE) = FALSE;

-- FK aktiv?
SELECT conname FROM pg_constraint WHERE conrelid = 'public.kunden'::regclass AND contype = 'f';

-- keine FK-Orphans
SELECT count(*) FROM public.kunden k
WHERE k.business_partner_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM domain_crm.business_partners b WHERE b.partner_id = k.business_partner_id);
```

- [ ] `--bridge-status`: `fk_ready = True`, `fk_orphans = 0`
- [ ] FK `fk_kunden_business_partner` vorhanden
- [ ] Masken-Smokes grün (Phase 4)
- [ ] 0 Deprecation-Warnungen über Beobachtungszeitraum (Phase 5)
- [ ] (nach Phase 6) Altspalten weg, `kunden_lookup` liest nur Satelliten, Smoke `search_lookup` grün

## Abbruchkriterien

- Ziel-DB ist nicht die erwartete Prod-DB → sofort abbrechen.
- Dry-Run zeigt unerwartet viele `conflict`/`duplicate_candidate` → erst fachlich klären, kein `--apply`.
- `fk_orphans > 0` → FK nicht aktivieren; Datenursache klären.
- Deprecation-Warnungen reißen nicht ab → Fallback NICHT entfernen, Konsument finden.

## Reihenfolge-Kurzfassung

1. Backup + Ziel verifizieren →
2. `kunden_merge` Dry-Run → Review →
3. `kunden_merge --apply` →
4. `--bridge-status` bis `fk_orphans=0` →
5. FK-Migration (`upgrade head`) →
6. Masken auf `resolve`/`by-partner` + Smoke →
7. 0 Deprecation-Warnungen abwarten → Fallback entfernen →
8. View entkoppeln + Altspalten droppen (Wartungsfenster + Backup) → Abnahme.
