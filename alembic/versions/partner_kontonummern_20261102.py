"""Stufe 3b Geschaeftspartnerstamm: eigene Debitoren- und Kreditorennummer je Partner.

Revision ID: partner_kontonummern_20261102
Revises: partner_rueckfuellung_20261101

ADR ``docs/adr/adr-business-partner-debitoren-kreditoren-20261101.md``, Nutzerentscheidung vom
01.11.2026: Jeder Geschaeftspartner fuehrt hoechstens eine Debitorennummer (``debtor_account``) und
eine Kreditorennummer (``creditor_account``), vergeben bei der ersten Kunden- bzw. Lieferantenrolle.

* Die Nummern sind je Mandant eindeutig (Teilindex, leere Konten zaehlen nicht). Fuehrt ein Mandant
  schon doppelte Nummern, bricht die Migration ab, statt eine davon zu aendern.
* Partner mit Rolle und ohne Konto bekommen eine Nummer aus dem Kreis des Mandanten. Ohne
  eingerichteten Kreis gilt der DATEV-Standard: Debitoren 10000-69999, Kreditoren 70000-99999.
  Vorhandene Nummern bleiben, wie sie sind; eine vergebene Nummer wird uebersprungen.
* Das SEPA-Mandat bekommt ``partner_id`` und bezieht sich damit auf den Partner; ``debitor_id``
  bleibt erhalten.

Jede vergebene Nummer und jeder angelegte Kreis steht in ``domain_crm.partner_konto_protokoll``.
Das ``downgrade`` leert nur protokollierte Nummern, die noch unveraendert sind, und entfernt nur
protokollierte Kreise. ``sepa_mandates.partner_id`` bleibt beim ``downgrade`` stehen: Ein Mandat ist
eine Einzugsermaechtigung, sein Partnerbezug kein Zwischenstand.
"""
from __future__ import annotations

import uuid

import sqlalchemy as sa

from alembic import op

revision = "partner_kontonummern_20261102"
down_revision = "partner_rueckfuellung_20261101"
branch_labels = None
depends_on = None

PROTOKOLL = "domain_crm.partner_konto_protokoll"
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))
#: Rollenflag -> (Kontospalte = range_type, Kreisanfang, Kreisende) wie ``KONTOKREISE`` im Partnerdienst.
KREISE = {"is_customer": ("debtor_account", 10000, 69999), "is_supplier": ("creditor_account", 70000, 99999)}


def _protokoll() -> None:
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS {PROTOKOLL} (
            id varchar(36) PRIMARY KEY,
            tenant_id varchar NOT NULL,
            art varchar(10) NOT NULL CHECK (art IN ('konto', 'kreis')),
            spalte varchar(20) NOT NULL CHECK (spalte IN ('debtor_account', 'creditor_account')),
            partner_id varchar(36),
            nummer varchar(40),
            vergeben_am timestamptz NOT NULL DEFAULT now()
        )""")
    op.execute(f"ALTER TABLE {PROTOKOLL} ENABLE ROW LEVEL SECURITY")
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {PROTOKOLL}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {PROTOKOLL} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {PROTOKOLL} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {PROTOKOLL} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {PROTOKOLL} FOR DELETE USING ({OWN})")


def upgrade() -> None:
    bind = op.get_bind()
    q = lambda sql, **p: bind.execute(sa.text(sql), p)  # noqa: E731

    for spalte, _start, _ende in KREISE.values():
        doppelt = q(f"SELECT tenant_id, {spalte} FROM domain_crm.business_partners "  # nosec B608
                    f"WHERE {spalte} IS NOT NULL AND {spalte} <> '' "
                    f"GROUP BY 1, 2 HAVING count(*) > 1 LIMIT 5").all()
        if doppelt:
            raise RuntimeError(f"Doppelte {spalte} je Mandant, bitte am Partner klaeren: "
                               + ", ".join(f"{t}/{n}" for t, n in doppelt))
        op.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS ux_business_partners_tenant_{spalte} "
                   f"ON domain_crm.business_partners (tenant_id, {spalte}) "
                   f"WHERE {spalte} IS NOT NULL AND {spalte} <> ''")

    _protokoll()

    def protokoll(tid, art, spalte, pid=None, nummer=None):
        q(f"INSERT INTO {PROTOKOLL} (id, tenant_id, art, spalte, partner_id, nummer) "
          "VALUES (:id, :t, :a, :s, :p, :n)", id=str(uuid.uuid4()), t=tid, a=art, s=spalte, p=pid, n=nummer)

    mandanten = {str(r[0]) for r in q("SELECT id FROM domain_shared.tenants")}
    for flag, (spalte, start, ende) in KREISE.items():
        offen = q(f"SELECT partner_id, tenant_id FROM domain_crm.business_partners "  # nosec B608
                  f"WHERE {flag} IS TRUE AND ({spalte} IS NULL OR {spalte} = '') "
                  "ORDER BY tenant_id, created_at NULLS LAST, partner_id").all()
        je_mandant: dict[str, list[str]] = {}
        for p in offen:
            # number_ranges verweist auf domain_shared.tenants; ohne Stammsatz kein Kreis (Klaerfall Stufe 2).
            if str(p.tenant_id) in mandanten:
                je_mandant.setdefault(str(p.tenant_id), []).append(str(p.partner_id))
        for tid, partner in je_mandant.items():
            kreis = q("SELECT prefix, start_number, current_value, digit_count FROM domain_shared.number_ranges "
                      "WHERE tenant_id = :t AND range_type = :s FOR UPDATE", t=tid, s=spalte).first()
            if kreis is None:
                q("INSERT INTO domain_shared.number_ranges (id, tenant_id, range_type, prefix, start_number, "
                  "current_value, digit_count, reserved_prefix_digits, is_active) "
                  "VALUES (:id, :t, :s, '', :start, :start, 5, 1, TRUE)",
                  id=str(uuid.uuid4()), t=tid, s=spalte, start=start)
                protokoll(tid, "kreis", spalte)
                prefix, wert, stellen, bis = "", start, 5, ende
            else:
                prefix, wert, stellen = kreis.prefix or "", kreis.current_value, kreis.digit_count
                bis = ende if kreis.start_number == start and not prefix else None
            vergeben = {r[0] for r in q(f"SELECT {spalte} FROM domain_crm.business_partners "  # nosec B608
                                        f"WHERE tenant_id = :t AND {spalte} IS NOT NULL", t=tid)}
            for pid in partner:
                while f"{prefix}{wert:0{stellen}d}" in vergeben:
                    wert += 1
                if bis is not None and wert > bis:
                    raise RuntimeError(f"Nummernkreis {spalte} des Mandanten {tid} ist ausgeschoepft")
                nummer = f"{prefix}{wert:0{stellen}d}"
                q(f"UPDATE domain_crm.business_partners SET {spalte} = :n WHERE partner_id = :p",  # nosec B608
                  n=nummer, p=pid)
                protokoll(tid, "konto", spalte, pid, nummer)
                vergeben.add(nummer)
                wert += 1
            q("UPDATE domain_shared.number_ranges SET current_value = :w, updated_at = now() "
              "WHERE tenant_id = :t AND range_type = :s", w=wert, t=tid, s=spalte)

    op.execute("ALTER TABLE domain_shared.sepa_mandates ADD COLUMN IF NOT EXISTS partner_id varchar(36)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_sepa_mandates_tenant_partner "
               "ON domain_shared.sepa_mandates (tenant_id, partner_id)")
    # debitor_id war je nach Weg Partner-ID oder Kunden-ID; nur eindeutige Bezuege im selben Mandanten.
    op.execute("""UPDATE domain_shared.sepa_mandates m SET partner_id = b.partner_id
                  FROM domain_crm.business_partners b
                  WHERE m.partner_id IS NULL AND b.partner_id = m.debitor_id AND b.tenant_id = m.tenant_id""")
    op.execute("""UPDATE domain_shared.sepa_mandates m SET partner_id = c.business_partner_id
                  FROM domain_crm.customers c
                  WHERE m.partner_id IS NULL AND c.id::text = m.debitor_id AND c.tenant_id = m.tenant_id
                    AND c.business_partner_id IS NOT NULL""")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": PROTOKOLL}).scalar() is not None:
        for _flag, (spalte, _start, _ende) in KREISE.items():
            op.execute(f"""UPDATE domain_crm.business_partners b SET {spalte} = NULL FROM {PROTOKOLL} p
                           WHERE p.art = 'konto' AND p.spalte = '{spalte}' AND p.partner_id = b.partner_id
                             AND b.{spalte} = p.nummer""")  # nosec B608
        op.execute(f"""DELETE FROM domain_shared.number_ranges n USING {PROTOKOLL} p
                       WHERE p.art = 'kreis' AND n.tenant_id = p.tenant_id AND n.range_type = p.spalte""")
    op.execute(f"DROP TABLE IF EXISTS {PROTOKOLL}")
    for _flag, (spalte, _start, _ende) in KREISE.items():
        op.execute(f"DROP INDEX IF EXISTS domain_crm.ux_business_partners_tenant_{spalte}")
