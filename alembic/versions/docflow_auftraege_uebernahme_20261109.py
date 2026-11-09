"""Verkaufsauftraege nach DocFlow uebernehmen; domain_crm.sales_orders wird Sicht auf DocFlow (BELEG-052).

Revision ID: docflow_auftraege_uebernahme_20261109
Revises: docflow_auftragsbestaetigung_20261109

DocFlow ist der einzige Belegspeicher (Nutzerentscheidung 08.11.2026). Schreibwege des alten Auftragsspeichers sind
entfernt (Router ``sales_orders``, Maske ``sales/sales-order``). Hier:

1. Jeder Auftrag aus ``domain_crm.sales_orders`` wird DocFlow-Beleg ``sales_order`` mit derselben ID (Belegnummer,
   Kunde, Waehrung, Datum, Positionen). Kopfangaben gehen in die Kopfbausteine: Betreff/Beschreibung/Notizen ->
   ``texte``, Ansprechpartner -> ``kontakt``, Liefertermin/-adresse/Versandart -> ``lieferung``, Zahlungsbedingung ->
   ``zahlung``. Steuer wird nicht angenommen: ohne Schluessel kein Satz (keine Vorgabe 19 %).
2. Stand: Entwurf -> ``draft``; offen -> ``open``; bestaetigt/in Lieferung -> ``confirmed`` (Auftragsbestaetigung,
   Nutzerentscheidung 09.11.2026); geliefert/abgeschlossen -> ``completed``; storniert -> ``cancelled``. Ein
   unbekannter Stand bricht die Migration ab - er wird nicht geraten.
3. Die Tabellen bleiben unveraendert als ``*_vor_docflow`` erhalten (GoBD: Ursprungsdaten) und sind schreibgeschuetzt
   (Aendern/Loeschen nur ueber den Wartungsschalter ``valeo.docflow_wartung``); unter dem alten Namen steht eine Sicht
   auf DocFlow fuer die Leser (``security_invoker``: es gilt die Mandantentrennung von DocFlow).
4. Indizes fuer die Leser: Kunde je Belegart (Kunden-360, Kreditlimit, Berichte) und Rueckverweis der
   Belegverknuepfungen (Angebot des Auftrags, Belegkette rueckwaerts).
"""
from __future__ import annotations

from alembic import op

revision = "docflow_auftraege_uebernahme_20261109"
down_revision = "docflow_auftragsbestaetigung_20261109"
branch_labels = None
depends_on = None

KOMMANDO = "migration:auftraege_20261109"  # Kommandospalte der Statushistorie: hoechstens 40 Zeichen

_STAND = """
    CASE
        WHEN lower(coalesce(s.status, 'open')) IN ('draft', 'entwurf') THEN 'draft'
        WHEN lower(coalesce(s.status, 'open')) IN ('open', 'offen') THEN 'open'
        WHEN lower(s.status) IN ('confirmed', 'bestaetigt', 'approved', 'in_delivery', 'in_lieferung') THEN 'confirmed'
        WHEN lower(s.status) IN ('completed', 'geliefert', 'abgeschlossen', 'delivered') THEN 'completed'
        WHEN lower(s.status) IN ('cancelled', 'storniert', 'canceled') THEN 'cancelled'
    END
"""


def _baustein(*paare: str) -> str:
    """jsonb-Objekt aus (Feld, Ausdruck)-Paaren ohne leere Werte."""
    teile = ", ".join(paare)
    return f"NULLIF(jsonb_strip_nulls(jsonb_build_object({teile})), '{{}}'::jsonb)"


def _leer(spalte: str) -> str:
    return f"NULLIF(btrim({spalte}), '')"


def upgrade() -> None:
    bind = op.get_bind()
    vorhanden = bind.exec_driver_sql(
        "SELECT c.relkind FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
        "WHERE n.nspname = 'domain_crm' AND c.relname = 'sales_orders'").scalar()
    if vorhanden != "r":
        return  # schon Sicht (oder nie angelegt): nichts zu uebernehmen

    unbekannt = bind.exec_driver_sql(
        f"SELECT DISTINCT s.status FROM domain_crm.sales_orders s WHERE ({_STAND}) IS NULL").scalars().all()
    if unbekannt:
        raise RuntimeError(f"Unbekannter Auftragsstand in domain_crm.sales_orders: {sorted(map(str, unbekannt))}. "
                           "Erst fachlich zuordnen, dann migrieren.")
    doppelt = bind.exec_driver_sql("""
        SELECT s.tenant_id, s.order_number FROM domain_crm.sales_orders s
        JOIN domain_docflow.document_headers h
          ON h.tenant_id = s.tenant_id AND h.doc_type = 'sales_order' AND h.doc_number = s.order_number
        WHERE h.id <> s.id
    """).all()
    if doppelt:
        raise RuntimeError(f"Auftragsnummer schon als anderer DocFlow-Auftrag vergeben: {doppelt[:10]}")

    op.execute(f"SELECT set_config('valeo.docflow_command', '{KOMMANDO}', true)")
    op.execute("SELECT set_config('valeo.docflow_reason', 'Uebernahme aus domain_crm.sales_orders (BELEG-052)', true)")
    texte = _baustein(f"'betreff', {_leer('s.subject')}", f"'kopftext', {_leer('s.description')}",
                      f"'notiz', {_leer('s.notes')}")
    kontakt = _baustein(f"'ansprechpartner', {_leer('s.contact_person')}")
    lieferung = _baustein("'liefertermin', to_char(s.delivery_date AT TIME ZONE 'Europe/Berlin', 'YYYY-MM-DD')",
                          f"'lieferadresse', {_leer('s.delivery_address')}",
                          f"'versandart', {_leer('s.shipping_method')}")
    zahlung = _baustein(f"'zahlungsbedingung', {_leer('s.payment_terms')}")
    op.execute(f"""
        INSERT INTO domain_docflow.document_headers
            (id, tenant_id, doc_type, doc_number, status, source_system, source_ref, customer_id, supplier_id,
             currency, total_net, total_tax, total_gross, document_date, version, created_by, updated_by,
             created_at, updated_at, deleted_at, printed_at, print_count, bausteine)
        SELECT s.id, s.tenant_id, 'sales_order', s.order_number, {_STAND}, 'domain_crm.sales_orders', s.id,
               s.customer_id, NULL, coalesce(NULLIF(s.currency, ''), 'EUR'), 0, 0, 0,
               coalesce(s.created_at, now()), 1, '{KOMMANDO}', '{KOMMANDO}',
               coalesce(s.created_at, now()), coalesce(s.updated_at, s.created_at, now()), s.deleted_at,
               s.printed_at, coalesce(s.print_count, 0),
               jsonb_strip_nulls(jsonb_build_object('texte', {texte}, 'kontakt', {kontakt},
                                                    'lieferung', {lieferung}, 'zahlung', {zahlung}))
        FROM domain_crm.sales_orders s
        WHERE NOT EXISTS (SELECT 1 FROM domain_docflow.document_headers h WHERE h.id = s.id)
    """)
    op.execute(f"""
        INSERT INTO domain_docflow.document_items
            (id, tenant_id, header_id, line_number, source_line_id, article_number, description, quantity, unit,
             unit_price, discount_percent, tax_rate, line_total_net, line_total_tax, line_total_gross,
             created_at, updated_at)
        SELECT gen_random_uuid()::text, i.tenant_id, i.order_id, coalesce(i.line_number, 0), i.id,
               coalesce(i.article_number, ''), i.description, coalesce(i.quantity, 0), NULLIF(i.unit, ''),
               coalesce(i.unit_price, 0), coalesce(i.discount_percent, 0), 0, n.netto, 0, n.netto,
               coalesce(i.created_at, now()), coalesce(i.updated_at, i.created_at, now())
        FROM domain_crm.sales_order_items i
        JOIN domain_docflow.document_headers h ON h.id = i.order_id AND h.created_by = '{KOMMANDO}'
        CROSS JOIN LATERAL (SELECT round(coalesce(i.quantity, 0) * coalesce(i.unit_price, 0)
                                         * (1 - coalesce(i.discount_percent, 0) / 100), 2) AS netto) n
    """)
    op.execute(f"""
        UPDATE domain_docflow.document_headers h
        SET total_net = t.netto, total_gross = t.netto
        FROM (SELECT header_id, sum(line_total_net) AS netto FROM domain_docflow.document_items GROUP BY header_id) t
        WHERE t.header_id = h.id AND h.created_by = '{KOMMANDO}'
    """)
    # Angebot -> Auftrag: nur, wenn das Angebot selbst DocFlow-Beleg ist.
    op.execute(f"""
        INSERT INTO domain_docflow.document_links (id, tenant_id, from_header_id, to_header_id, relation_type, created_at)
        SELECT gen_random_uuid()::text, s.tenant_id, s.sales_offer_id, s.id, 'offer_to_order', now()
        FROM domain_crm.sales_orders s
        JOIN domain_docflow.document_headers a ON a.id = s.sales_offer_id AND a.doc_type = 'sales_offer'
        JOIN domain_docflow.document_headers h ON h.id = s.id AND h.created_by = '{KOMMANDO}'
    """)

    op.execute("CREATE INDEX IF NOT EXISTS ix_docflow_headers_tenant_type_customer "
               "ON domain_docflow.document_headers (tenant_id, doc_type, customer_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_docflow_links_tenant_to_relation "
               "ON domain_docflow.document_links (tenant_id, to_header_id, relation_type)")

    op.execute("ALTER TABLE domain_crm.sales_order_items RENAME TO sales_order_items_vor_docflow")
    op.execute("ALTER TABLE domain_crm.sales_orders RENAME TO sales_orders_vor_docflow")
    op.execute("""
        CREATE OR REPLACE FUNCTION domain_crm.ursprungsdaten_unveraenderlich() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            IF current_setting('valeo.docflow_wartung', true) = 'loeschen' THEN
                RETURN COALESCE(OLD, NEW);
            END IF;
            RAISE EXCEPTION 'Ursprungsdaten vor DocFlow sind unveraenderlich (GoBD): %', TG_TABLE_NAME
                USING ERRCODE = 'check_violation';
        END $$
    """)
    for tabelle in ("sales_orders_vor_docflow", "sales_order_items_vor_docflow"):
        op.execute(f"CREATE TRIGGER {tabelle}_unveraenderlich BEFORE INSERT OR UPDATE OR DELETE "
                   f"ON domain_crm.{tabelle} FOR EACH ROW EXECUTE FUNCTION domain_crm.ursprungsdaten_unveraenderlich()")
    op.execute("COMMENT ON TABLE domain_crm.sales_orders_vor_docflow IS "
               "'Ursprungsdaten der Auftraege vor BELEG-052 (unveraendert, GoBD). Fuehrend ist DocFlow.'")
    op.execute("""
        CREATE VIEW domain_crm.sales_orders WITH (security_invoker = true) AS
        SELECT h.id, h.tenant_id,
               (SELECT l.from_header_id FROM domain_docflow.document_links l
                 WHERE l.to_header_id = h.id AND l.tenant_id = h.tenant_id AND l.relation_type = 'offer_to_order'
                 ORDER BY l.created_at LIMIT 1) AS sales_offer_id,
               h.customer_id,
               (SELECT c.company_name FROM domain_crm.customers c
                 WHERE c.id = h.customer_id AND c.tenant_id = h.tenant_id LIMIT 1) AS customer_name,
               h.doc_number AS order_number,
               h.bausteine #>> '{texte,betreff}' AS subject,
               h.bausteine #>> '{texte,kopftext}' AS description,
               h.total_gross AS total_amount, h.currency,
               CASE h.status WHEN 'reversed' THEN 'cancelled' ELSE h.status END AS status,
               h.bausteine #>> '{kontakt,ansprechpartner}' AS contact_person,
               CASE WHEN h.bausteine #>> '{lieferung,liefertermin}' ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
                    THEN (h.bausteine #>> '{lieferung,liefertermin}')::date::timestamptz END AS delivery_date,
               h.bausteine #>> '{lieferung,lieferadresse}' AS delivery_address,
               h.bausteine #>> '{lieferung,versandart}' AS shipping_method,
               h.bausteine #>> '{zahlung,zahlungsbedingung}' AS payment_terms,
               h.bausteine #>> '{texte,notiz}' AS notes,
               false AS is_pauschale,
               h.created_at, h.updated_at, h.deleted_at, h.version, h.printed_at, h.print_count,
               NULL::timestamptz AS posted_at
        FROM domain_docflow.document_headers h
        WHERE h.doc_type = 'sales_order'
    """)
    op.execute("""
        CREATE VIEW domain_crm.sales_order_items WITH (security_invoker = true) AS
        SELECT i.id, i.tenant_id, i.header_id AS order_id, i.line_number, i.article_number, i.description,
               i.quantity, i.unit, i.unit_price, NULL::numeric AS ek_price, i.discount_percent,
               i.line_total_net AS line_total, i.created_at, i.updated_at,
               -- Noch in keinen Folgebeleg gegangen: wie die Belegmaske (docflow_belegadapter._offene_mengen) -
               -- der groessere der Wege Lieferschein/Rechnung; stornierte Folgebelege geben ihre Menge frei.
               GREATEST(i.quantity - GREATEST(
                   COALESCE((SELECT sum(l.quantity_linked) FROM domain_docflow.document_links l
                             JOIN domain_docflow.document_headers z ON z.id = l.to_header_id AND z.tenant_id = l.tenant_id
                             WHERE l.tenant_id = i.tenant_id AND l.from_header_id = i.header_id
                               AND l.from_item_id = i.id AND l.relation_type = 'order_to_delivery'
                               AND z.deleted_at IS NULL AND z.status NOT IN ('reversed', 'cancelled')), 0),
                   COALESCE((SELECT sum(l.quantity_linked) FROM domain_docflow.document_links l
                             JOIN domain_docflow.document_headers z ON z.id = l.to_header_id AND z.tenant_id = l.tenant_id
                             WHERE l.tenant_id = i.tenant_id AND l.from_header_id = i.header_id
                               AND l.from_item_id = i.id AND l.relation_type = 'order_to_invoice'
                               AND z.deleted_at IS NULL AND z.status NOT IN ('reversed', 'cancelled')), 0)), 0)
                   AS offene_menge
        FROM domain_docflow.document_items i
        JOIN domain_docflow.document_headers h ON h.id = i.header_id AND h.tenant_id = i.tenant_id
        WHERE h.doc_type = 'sales_order'
    """)
    op.execute("COMMENT ON VIEW domain_crm.sales_orders IS "
               "'Leseweg: Verkaufsauftraege aus DocFlow (BELEG-052). Schreiben nur ueber die Belegmaske.'")
    op.execute("COMMENT ON VIEW domain_crm.sales_order_items IS 'Leseweg: Auftragspositionen aus DocFlow (BELEG-052).'")


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS domain_crm.sales_order_items")
    op.execute("DROP VIEW IF EXISTS domain_crm.sales_orders")
    for tabelle in ("sales_orders_vor_docflow", "sales_order_items_vor_docflow"):
        op.execute(f"DROP TRIGGER IF EXISTS {tabelle}_unveraenderlich ON domain_crm.{tabelle}")
    op.execute("DROP FUNCTION IF EXISTS domain_crm.ursprungsdaten_unveraenderlich()")
    op.execute("DROP INDEX IF EXISTS domain_docflow.ix_docflow_links_tenant_to_relation")
    op.execute("DROP INDEX IF EXISTS domain_docflow.ix_docflow_headers_tenant_type_customer")
    op.execute("ALTER TABLE IF EXISTS domain_crm.sales_orders_vor_docflow RENAME TO sales_orders")
    op.execute("ALTER TABLE IF EXISTS domain_crm.sales_order_items_vor_docflow RENAME TO sales_order_items")
    op.execute("COMMENT ON TABLE domain_crm.sales_orders IS NULL")
    # Nur die uebernommenen, seither unveraenderten Belege; Folgebelege oder Aenderungen halten den Rueckweg an.
    op.execute("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)")
    op.execute(f"""
        DELETE FROM domain_docflow.document_links l
        USING domain_docflow.document_headers h
        WHERE l.to_header_id = h.id AND l.relation_type = 'offer_to_order' AND h.created_by = '{KOMMANDO}'
          AND h.version = 1
    """)
    op.execute(f"""
        DELETE FROM domain_docflow.document_status_history sh
        USING domain_docflow.document_headers h
        WHERE sh.header_id = h.id AND h.created_by = '{KOMMANDO}' AND h.version = 1
          AND NOT EXISTS (SELECT 1 FROM domain_docflow.document_links l WHERE l.from_header_id = h.id)
    """)
    op.execute(f"""
        DELETE FROM domain_docflow.document_headers h
        WHERE h.created_by = '{KOMMANDO}' AND h.version = 1
          AND NOT EXISTS (SELECT 1 FROM domain_docflow.document_links l WHERE l.from_header_id = h.id)
    """)
    # Der Wartungsschalter gilt nur fuer dieses Aufraeumen, nicht fuer den Rest der Transaktion.
    op.execute("SELECT set_config('valeo.docflow_wartung', '', true)")
