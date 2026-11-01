"""Stufe 2 Geschaeftspartnerstamm: bestehende Kunden und Lieferanten Partnern zuordnen.

Revision ID: partner_rueckfuellung_20261101
Revises: kundennummer_mandant_20261101

ADR ``docs/adr/adr-business-partner-debitoren-kreditoren-20261101.md``. Seit Stufe 1 haengt jede
neue Kunden- und Lieferantenrolle an einem Geschaeftspartner. Diese Migration ordnet den Bestand
nach derselben Regel zu, ohne IDs, Nummern, Belege oder Buchungen anzufassen:

* Ein vorhandener Partner wird nur verwendet, wenn USt-IdNr. **und** Name im Mandanten eindeutig
  passen. Ein Name allein ordnet nie zu.
* Ohne USt-IdNr. entsteht ein neuer Partner, ausser ein Partner gleichen Namens existiert schon:
  dann Klaerfall statt Dublette.
* Mehrere Kunden (bzw. mehrere Lieferanten) mit gleicher USt-IdNr. und Name sind moegliche
  Dubletten: Klaerfall, keine Zusammenfuehrung. Ein Kunde und ein Lieferant mit gleicher
  USt-IdNr. und Name werden ein Partner mit beiden Rollen.
* Gleiche USt-IdNr. bei anderem Namen, mehrere passende Partner, ein Mandant ohne Stammsatz in
  ``domain_shared.tenants`` oder eine bestehende Verknuepfung auf einen fehlenden oder fremden
  Partner: Klaerfall.

Klaerfaelle stehen in ``domain_crm.partner_klaerfaelle`` (RLS je Mandant), jede Zuordnung in
``domain_crm.partner_rueckfuellung_protokoll``. Das ``downgrade`` nimmt nur die protokollierten
Verknuepfungen zurueck und loescht nur Partner, die diese Migration angelegt hat und auf die nichts
anderes mehr zeigt.
"""
from __future__ import annotations

import json
import re
import uuid
from collections import defaultdict

import sqlalchemy as sa

from alembic import op

revision = "partner_rueckfuellung_20261101"
down_revision = "kundennummer_mandant_20261101"
branch_labels = None
depends_on = None

KLAERFAELLE = "domain_crm.partner_klaerfaelle"
PROTOKOLL = "domain_crm.partner_rueckfuellung_protokoll"
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))
LAENDER = {"deutschland": "DE", "germany": "DE", "oesterreich": "AT", "österreich": "AT", "austria": "AT",
           "niederlande": "NL", "netherlands": "NL", "schweiz": "CH", "frankreich": "FR", "polen": "PL",
           "belgien": "BE", "daenemark": "DK", "dänemark": "DK", "luxemburg": "LU"}


def _ust(wert) -> str:
    return re.sub(r"[\s.-]", "", wert or "").upper()


def _name(wert) -> str:
    return (wert or "").strip().lower()


def _land(wert):
    wert = (wert or "").strip()
    if len(wert) == 2 and wert.isalpha():
        return wert.upper()
    return LAENDER.get(wert.lower())


def _tabellen() -> None:
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS {KLAERFAELLE} (
            id varchar(36) PRIMARY KEY,
            tenant_id varchar NOT NULL,
            quelle varchar(20) NOT NULL CHECK (quelle IN ('kunde', 'lieferant')),
            satz_id varchar NOT NULL,
            grund varchar(200) NOT NULL,
            kandidaten jsonb NOT NULL DEFAULT '[]'::jsonb,
            erstellt_am timestamptz NOT NULL DEFAULT now(),
            erledigt_am timestamptz,
            UNIQUE (quelle, satz_id)
        )""")
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS {PROTOKOLL} (
            quelle varchar(20) NOT NULL CHECK (quelle IN ('kunde', 'lieferant')),
            satz_id varchar NOT NULL,
            tenant_id varchar NOT NULL,
            partner_id varchar(36) NOT NULL,
            partner_neu boolean NOT NULL,
            zugeordnet_am timestamptz NOT NULL DEFAULT now(),
            PRIMARY KEY (quelle, satz_id)
        )""")
    for table in (KLAERFAELLE, PROTOKOLL):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        for name in POLICIES:
            op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
        op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({OWN})")
        op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({OWN})")
        op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
        op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({OWN})")


def upgrade() -> None:
    _tabellen()
    bind = op.get_bind()
    q = lambda sql, **p: bind.execute(sa.text(sql), p)  # noqa: E731

    mandanten = {str(r[0]) for r in q("SELECT id FROM domain_shared.tenants")}
    partner = q("SELECT partner_id, tenant_id, name_1, vat_id FROM domain_crm.business_partners").all()
    partner_ids = {str(p.partner_id): str(p.tenant_id) for p in partner}
    nach_ust: dict[tuple, list] = defaultdict(list)
    nach_name: dict[tuple, list] = defaultdict(list)
    for p in partner:
        if _ust(p.vat_id):
            nach_ust[(str(p.tenant_id), _ust(p.vat_id))].append(p)
        nach_name[(str(p.tenant_id), _name(p.name_1))].append(str(p.partner_id))

    saetze = [("kunde", r) for r in q(
        "SELECT id, tenant_id, company_name AS name, tax_id AS ust, business_partner_id AS bp, "
        "postal_code AS plz, city AS ort, country AS land, email, phone FROM domain_crm.customers "
        "WHERE deleted_at IS NULL")]
    saetze += [("lieferant", r) for r in q(
        "SELECT id, tenant_id, firmenname AS name, ust_id AS ust, partner_id AS bp, strasse, plz, ort, land, "
        "email, telefon AS phone FROM domain_einkauf.lieferanten")]

    def klaerfall(quelle, satz, grund, kandidaten=()):
        q(f"INSERT INTO {KLAERFAELLE} (id, tenant_id, quelle, satz_id, grund, kandidaten) "
          "VALUES (:id, :t, :q, :s, :g, CAST(:k AS jsonb)) ON CONFLICT (quelle, satz_id) DO NOTHING",
          id=str(uuid.uuid4()), t=str(satz.tenant_id or ""), q=quelle, s=str(satz.id), g=grund,
          k=json.dumps(sorted(set(kandidaten))))

    offen: list[tuple[str, object]] = []
    for quelle, satz in saetze:
        tid = str(satz.tenant_id or "")
        if satz.bp:
            if partner_ids.get(str(satz.bp)) != tid:
                klaerfall(quelle, satz, "Verknuepfter Partner fehlt oder gehoert einem anderen Mandanten", [str(satz.bp)])
            continue
        if tid not in mandanten:
            klaerfall(quelle, satz, "Mandant ohne Stammsatz in domain_shared.tenants")
            continue
        offen.append((quelle, satz))

    gruppen: dict[tuple, list] = defaultdict(list)
    for quelle, satz in offen:
        ust = _ust(satz.ust)
        schluessel = (str(satz.tenant_id), ust, _name(satz.name)) if ust else ("ohne", quelle, str(satz.id))
        gruppen[schluessel].append((quelle, satz))

    def zuordnen(quelle, satz, pid, neu):
        if quelle == "kunde":
            q("UPDATE domain_crm.customers SET business_partner_id = :p WHERE id = :id AND tenant_id = :t",
              p=pid, id=satz.id, t=satz.tenant_id)
            q("UPDATE domain_crm.business_partners SET is_customer = TRUE WHERE partner_id = :p", p=pid)
        else:
            q("UPDATE domain_einkauf.lieferanten SET partner_id = :p WHERE id = :id AND tenant_id = :t",
              p=pid, id=satz.id, t=satz.tenant_id)
            q("UPDATE domain_crm.business_partners SET is_supplier = TRUE WHERE partner_id = :p", p=pid)
        q(f"INSERT INTO {PROTOKOLL} (quelle, satz_id, tenant_id, partner_id, partner_neu) "
          "VALUES (:q, :s, :t, :p, :n)", q=quelle, s=str(satz.id), t=str(satz.tenant_id), p=pid, n=neu)

    # Pflicht-Booleans ohne Default (gewachsene Datenbanken haben Defaults verloren) ausdruecklich FALSE.
    flags = q("SELECT column_name FROM information_schema.columns WHERE table_schema = 'domain_crm' "
              "AND table_name = 'business_partners' AND data_type = 'boolean' AND is_nullable = 'NO' "
              "AND column_default IS NULL ORDER BY column_name").scalars().all()
    flag_spalten, flag_werte = "".join(f", {f}" for f in flags), ", FALSE" * len(flags)

    def neuer_partner(satz) -> str:
        pid = str(uuid.uuid4())
        q("INSERT INTO domain_crm.business_partners (partner_id, tenant_id, partner_number, name_1, street, "
          f"postal_code, city, country, vat_id, email, phone, status, created_at, updated_at{flag_spalten}) VALUES "
          f"(:p, :t, :nr, :name, :street, :plz, :ort, :land, :ust, :email, :tel, 'active', now(), now(){flag_werte})",
          p=pid, t=str(satz.tenant_id), nr="GP-" + pid.replace("-", "").upper()[:20],
          name=(satz.name or "").strip()[:255] or "Geschaeftspartner",
          street=(getattr(satz, "strasse", None) or None) and satz.strasse[:120],
          plz=(satz.plz or None) and satz.plz[:20], ort=(satz.ort or None) and satz.ort[:120],
          land=_land(satz.land), ust=(satz.ust or None) and satz.ust.strip()[:50],
          email=satz.email or None, tel=satz.phone or None)
        # Ein spaeterer Satz gleichen Namens ohne USt-IdNr. wird so Klaerfall statt zweiter Partner.
        nach_name[(str(satz.tenant_id), _name(satz.name))].append(pid)
        return pid

    for schluessel, mitglieder in gruppen.items():
        if schluessel[0] == "ohne":
            quelle, satz = mitglieder[0]
            gleichnamig = nach_name.get((str(satz.tenant_id), _name(satz.name)), [])
            if gleichnamig:
                klaerfall(quelle, satz, "Ohne USt-IdNr.; Partner gleichen Namens vorhanden", gleichnamig)
            else:
                zuordnen(quelle, satz, neuer_partner(satz), True)
            continue
        tid, ust, name = schluessel
        alle = nach_ust.get((tid, ust), [])
        passend = [str(p.partner_id) for p in alle if _name(p.name_1) == name]
        if len(passend) > 1:
            for quelle, satz in mitglieder:
                klaerfall(quelle, satz, "Mehrere Partner mit gleicher USt-IdNr. und Name", passend)
            continue
        if not passend and alle:
            for quelle, satz in mitglieder:
                klaerfall(quelle, satz, "USt-IdNr. gehoert einem Partner anderen Namens",
                          [str(p.partner_id) for p in alle])
            continue
        je_quelle: dict[str, list] = defaultdict(list)
        for quelle, satz in mitglieder:
            je_quelle[quelle].append(satz)
        eindeutig = []
        for quelle, liste in je_quelle.items():
            if len(liste) > 1:
                for satz in liste:
                    klaerfall(quelle, satz, "Moegliche Dublette: gleiche USt-IdNr. und Name",
                              [str(s.id) for s in liste])
            else:
                eindeutig.append((quelle, liste[0]))
        if not eindeutig:
            continue
        neu = not passend
        pid = passend[0] if passend else neuer_partner(eindeutig[0][1])
        for quelle, satz in eindeutig:
            zuordnen(quelle, satz, pid, neu)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": PROTOKOLL}).scalar() is not None:
        op.execute(f"""UPDATE domain_crm.customers c SET business_partner_id = NULL FROM {PROTOKOLL} p
                       WHERE p.quelle = 'kunde' AND p.satz_id = c.id AND c.business_partner_id = p.partner_id""")
        op.execute(f"""UPDATE domain_einkauf.lieferanten l SET partner_id = NULL FROM {PROTOKOLL} p
                       WHERE p.quelle = 'lieferant' AND p.satz_id = l.id::text AND l.partner_id = p.partner_id""")
        op.execute(f"""DELETE FROM domain_crm.business_partners b
                       WHERE b.partner_id IN (SELECT partner_id FROM {PROTOKOLL} WHERE partner_neu)
                         AND NOT EXISTS (SELECT 1 FROM domain_crm.customers c WHERE c.business_partner_id = b.partner_id)
                         AND NOT EXISTS (SELECT 1 FROM domain_einkauf.lieferanten l WHERE l.partner_id = b.partner_id)""")
    op.execute(f"DROP TABLE IF EXISTS {PROTOKOLL}")
    op.execute(f"DROP TABLE IF EXISTS {KLAERFAELLE}")
