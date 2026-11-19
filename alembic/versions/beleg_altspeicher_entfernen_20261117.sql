-- Rueckweg der Migration beleg_altspeicher_entfernen_20261117 (BELEG-052 S5): die alten Belegspeicher, leer,
-- mit Schluesseln, Indizes, RLS und Schreibschutz - erzeugt per pg_dump --schema-only aus einer frisch
-- migrierten Datenbank. Die Daten sind nach Nutzerentscheidung vom 10.11.2026 Testdaten und kommen nicht zurueck.

CREATE TABLE domain_crm.sales_order_items_vor_docflow (
    id character varying NOT NULL,
    tenant_id character varying NOT NULL,
    order_id character varying NOT NULL,
    line_number integer NOT NULL,
    article_number character varying(80) NOT NULL,
    description character varying(255),
    quantity numeric(12,3) NOT NULL,
    unit_price numeric(12,4) NOT NULL,
    discount_percent numeric(7,2) DEFAULT 0 NOT NULL,
    line_total numeric(14,2) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    ek_price numeric(14,4),
    unit character varying(20) DEFAULT 'kg'::character varying,
    CONSTRAINT ck_sales_order_items_discount_range CHECK (((discount_percent >= (0)::numeric) AND (discount_percent <= (100)::numeric))),
    CONSTRAINT ck_sales_order_items_price_nonneg CHECK ((unit_price >= (0)::numeric)),
    CONSTRAINT ck_sales_order_items_qty_nonneg CHECK ((quantity >= (0)::numeric))
);

CREATE TABLE domain_crm.sales_orders_vor_docflow (
    id character varying NOT NULL,
    tenant_id character varying NOT NULL,
    sales_offer_id character varying,
    customer_id character varying NOT NULL,
    order_number character varying NOT NULL,
    subject character varying NOT NULL,
    description character varying NOT NULL,
    total_amount numeric(15,2) NOT NULL,
    currency character varying(3) NOT NULL,
    status character varying NOT NULL,
    contact_person character varying,
    delivery_date timestamp with time zone,
    delivery_address text,
    payment_terms character varying,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    version integer NOT NULL,
    shipping_method character varying(40),
    customer_name character varying,
    printed_at timestamp with time zone,
    print_count integer DEFAULT 0 NOT NULL,
    posted_at timestamp with time zone,
    is_pauschale boolean DEFAULT false
);

COMMENT ON TABLE domain_crm.sales_orders_vor_docflow IS 'Ursprungsdaten der Auftraege vor BELEG-052 (unveraendert, GoBD). Fuehrend ist DocFlow.';

CREATE TABLE domain_einkauf.bestellung_positionen (
    id uuid NOT NULL,
    bestellung_id uuid NOT NULL,
    pos_nr integer NOT NULL,
    article_id character varying,
    artikel_nr character varying(50) NOT NULL,
    artikel_bezeichnung character varying(300) NOT NULL,
    lieferanten_artnr character varying(50),
    menge numeric(14,3) NOT NULL,
    menge_geliefert numeric(14,3) DEFAULT '0'::numeric,
    menge_offen numeric(14,3),
    einheit character varying(20) NOT NULL,
    einzelpreis numeric(14,4),
    preis_einheit character varying(20) DEFAULT '100kg'::character varying,
    rabatt_prozent numeric(5,2) DEFAULT '0'::numeric,
    netto_betrag numeric(14,2),
    mwst_satz numeric(5,2),
    mwst_betrag numeric(14,2),
    brutto_betrag numeric(14,2),
    kontrakt_pos_id uuid,
    lieferdatum date,
    lagerort character varying(100),
    notiz text,
    status character varying(20) DEFAULT 'offen'::character varying,
    gebinde_menge numeric(14,3),
    gebinde_einheit character varying(20),
    gebinde_schluessel character varying(20),
    gewicht_kg numeric(14,3),
    kontrakt_nr character varying(50),
    lagerhalle character varying(50),
    lagerfach character varying(50),
    mindestmenge numeric(14,3),
    maximalmenge numeric(14,3),
    tenant_id character varying DEFAULT public.rls_current_tenant() NOT NULL
);

CREATE TABLE domain_einkauf.bestellungen (
    id uuid NOT NULL,
    tenant_id character varying NOT NULL,
    bestellnummer character varying(50) NOT NULL,
    lieferant_id uuid NOT NULL,
    vorschlag_id uuid,
    niederlassung_id character varying,
    bestelldatum date NOT NULL,
    lieferdatum_wunsch date,
    lieferdatum_zugesagt date,
    lieferdatum_ist date,
    status character varying(30) DEFAULT 'entwurf'::character varying,
    versand_art character varying(20) DEFAULT 'email'::character varying,
    versandt_am timestamp with time zone,
    versandt_von character varying(200),
    netto_summe numeric(14,2),
    mwst_betrag numeric(14,2),
    brutto_summe numeric(14,2),
    waehrung character varying(3) DEFAULT 'EUR'::character varying,
    zahlungsziel_tage integer,
    skonto_prozent numeric(5,2),
    skonto_frist_tage integer,
    unsere_referenz character varying(100),
    ihre_referenz character varying(100),
    kontrakt_id uuid,
    freitext_kopf text,
    freitext_fuss text,
    notiz text,
    anhang_ids jsonb,
    erstellt_von character varying(200),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    bestellfall character varying(32) DEFAULT 'bestand_abgleich'::character varying,
    ansprechpartner character varying(200),
    kreditor_konto character varying(50),
    lieferant_nr character varying(50),
    kostenstelle character varying(50),
    kommission character varying(100),
    ladetermin date,
    ladetermin_ab date,
    lade_datum date,
    incoterms character varying(10),
    lieferadresse text,
    zahlungsbedingung character varying(80),
    skonto1_tage integer,
    skonto1_prozent numeric(5,2),
    skonto2_tage integer,
    skonto2_prozent numeric(5,2),
    netto_tage integer,
    fremdwaehrung character varying(3),
    umrechnungsfaktor numeric(12,6),
    anfrage_nr character varying(50),
    angebot_nr character varying(50),
    auftrag_nr character varying(50),
    abverkauf_horizont character varying(20),
    bedarfsmenge numeric(14,3),
    mindestbestellmenge numeric(14,3),
    maximalbestellmenge numeric(14,3),
    artikelgruppe character varying(80),
    lagerplatz_opt boolean DEFAULT false,
    fracht_opt boolean DEFAULT false,
    opportunitaetskostensatz numeric(14,4),
    palettenstellplatz_kosten numeric(14,4),
    lagerkosten_satz numeric(14,4),
    verkaufsbeleg_id character varying(64),
    kunden_id character varying(64),
    direktlieferung boolean DEFAULT false,
    ueberschlag_lager boolean DEFAULT false,
    neuer_artikel boolean DEFAULT false,
    innovationshinweis text
);

COMMENT ON COLUMN domain_einkauf.bestellungen.bestellfall IS 'bestand_abgleich | direktlieferung | innovation';

CREATE TABLE domain_sales.delivery_note_positions (
    id character varying NOT NULL,
    delivery_note_id character varying NOT NULL,
    pos_nr integer NOT NULL,
    artikel_id character varying,
    artikel_nr character varying(50),
    bezeichnung character varying(255),
    bezeichnung2 character varying(255),
    menge numeric(14,3) NOT NULL,
    einheit character varying(20),
    listenpreis numeric(14,4),
    rabatt numeric(5,2) DEFAULT 0 NOT NULL,
    art character varying(50),
    netto_preis numeric(14,4),
    netto_betrag numeric(14,2),
    niederlassung integer,
    lagerhalle character varying(80),
    lagerfach character varying(80),
    charge character varying(80),
    serien_nr character varying(80),
    erloskonto character varying(20),
    mwst_prozent numeric(5,2) DEFAULT 19 NOT NULL,
    kontrakt_nr character varying(50),
    skontierf boolean DEFAULT false NOT NULL,
    fremdware boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    gef_punkt character varying(80),
    na_bio character varying(80),
    muster_nr character varying(80),
    strecke character varying(80),
    zus_beleg character varying(80),
    anerken character varying(80),
    tenant_id character varying DEFAULT public.rls_current_tenant() NOT NULL
);

COMMENT ON COLUMN domain_sales.delivery_note_positions.gef_punkt IS 'Gefahrpunkt (Danger point / Hazard classification)';

COMMENT ON COLUMN domain_sales.delivery_note_positions.na_bio IS 'Nachhaltigkeits-/Bio-Kennzeichnung (Sustainability/Bio label)';

COMMENT ON COLUMN domain_sales.delivery_note_positions.muster_nr IS 'Muster-Nummer (Sample number)';

COMMENT ON COLUMN domain_sales.delivery_note_positions.strecke IS 'Strecke (Route/Line)';

COMMENT ON COLUMN domain_sales.delivery_note_positions.zus_beleg IS 'Zusatzbeleg (Additional document)';

COMMENT ON COLUMN domain_sales.delivery_note_positions.anerken IS 'Anerkennung (Recognition/Acknowledgment)';

CREATE TABLE domain_sales.delivery_notes (
    id character varying NOT NULL,
    tenant_id character varying NOT NULL,
    delivery_note_number character varying(50) NOT NULL,
    customer_id character varying,
    branch_id character varying,
    sales_rep_id character varying,
    operator_id character varying,
    delivery_date date NOT NULL,
    delivery_time time without time zone,
    cost_center_id character varying,
    truck_number integer,
    is_credit_note boolean DEFAULT false NOT NULL,
    is_self_pickup boolean DEFAULT false NOT NULL,
    is_early_payment boolean DEFAULT false NOT NULL,
    reference_invoice_number character varying(50),
    status character varying(20) DEFAULT 'draft'::character varying NOT NULL,
    is_printed boolean DEFAULT false NOT NULL,
    is_delivered boolean DEFAULT false NOT NULL,
    invoice_number character varying(50),
    totals jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by character varying,
    updated_by character varying,
    sales_order_id uuid,
    storno_grund text,
    CONSTRAINT ck_delivery_notes_status CHECK (((status)::text = ANY ((ARRAY['draft'::character varying, 'printed'::character varying, 'posted'::character varying, 'shipped'::character varying, 'delivered'::character varying, 'invoiced'::character varying, 'BERECHNET'::character varying, 'storniert'::character varying, 'cancelled'::character varying, 'geliefert'::character varying])::text[])))
);

CREATE TABLE domain_sales.sales_credit_note_lines (
    id character varying(36) NOT NULL,
    credit_note_id character varying(36) NOT NULL,
    line_number integer DEFAULT 1 NOT NULL,
    article_number character varying(80),
    description character varying(500),
    quantity numeric(18,4) DEFAULT 0 NOT NULL,
    unit_price numeric(18,4) DEFAULT 0 NOT NULL,
    tax_rate numeric(5,2),
    line_total numeric(18,4) DEFAULT 0 NOT NULL,
    tax_code character varying(50),
    tenant_id character varying DEFAULT public.rls_current_tenant() NOT NULL
);

CREATE TABLE domain_sales.sales_credit_notes (
    id character varying(36) NOT NULL,
    tenant_id character varying(64) NOT NULL,
    credit_note_number character varying(64) NOT NULL,
    customer_id character varying(64) NOT NULL,
    customer_name character varying(200),
    invoice_reference character varying(64),
    reason character varying(500) NOT NULL,
    total_amount numeric(18,4) DEFAULT 0 NOT NULL,
    currency character varying(3) DEFAULT 'EUR'::character varying NOT NULL,
    status character varying(20) DEFAULT 'draft'::character varying NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    net_amount numeric(15,2),
    tax_amount numeric(15,2),
    correction_type character varying(30) DEFAULT 'rechnungskorrektur'::character varying NOT NULL,
    CONSTRAINT ck_sales_credit_notes_correction_type CHECK (((correction_type)::text = ANY ((ARRAY['rechnungskorrektur'::character varying, 'gutschrift_14_ustg'::character varying])::text[])))
);

CREATE TABLE domain_sales.sales_delivery_notes (
    id character varying(36) NOT NULL,
    tenant_id character varying(36) NOT NULL,
    quittiert_am timestamp with time zone,
    quittiert_von character varying(100)
);

CREATE TABLE domain_sales.sales_invoice_lines (
    id character varying NOT NULL,
    tenant_id character varying(120) NOT NULL,
    invoice_id character varying NOT NULL,
    line_no character varying(120) NOT NULL,
    article_id character varying(120),
    article_number character varying(80),
    description character varying(255),
    quantity numeric(18,6) NOT NULL,
    unit character varying(20) NOT NULL,
    unit_price numeric(18,4) DEFAULT 0 NOT NULL,
    net_amount numeric(18,2) DEFAULT 0 NOT NULL,
    vat_rate numeric(5,2),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT ck_sales_invoice_line_qty_positive CHECK ((quantity > (0)::numeric))
);

CREATE TABLE domain_sales.sales_invoices (
    id character varying NOT NULL,
    tenant_id character varying(120) NOT NULL,
    invoice_number character varying(60) NOT NULL,
    customer_id character varying(120) NOT NULL,
    invoice_date date NOT NULL,
    due_date date,
    currency character varying(3) DEFAULT 'EUR'::character varying NOT NULL,
    status character varying(20) DEFAULT 'entwurf'::character varying NOT NULL,
    net_amount numeric(18,2) DEFAULT 0 NOT NULL,
    vat_amount numeric(18,2) DEFAULT 0 NOT NULL,
    gross_amount numeric(18,2) DEFAULT 0 NOT NULL,
    note text,
    created_by character varying(120),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

ALTER TABLE ONLY domain_crm.sales_order_items_vor_docflow
    ADD CONSTRAINT sales_order_items_pkey PRIMARY KEY (id);

ALTER TABLE ONLY domain_crm.sales_orders_vor_docflow
    ADD CONSTRAINT sales_orders_order_number_key UNIQUE (order_number);

ALTER TABLE ONLY domain_crm.sales_orders_vor_docflow
    ADD CONSTRAINT sales_orders_pkey PRIMARY KEY (id);

ALTER TABLE ONLY domain_crm.sales_order_items_vor_docflow
    ADD CONSTRAINT uq_sales_order_items_order_line UNIQUE (order_id, line_number);

ALTER TABLE ONLY domain_crm.sales_orders_vor_docflow
    ADD CONSTRAINT uq_sales_orders_id_tenant UNIQUE (id, tenant_id);

ALTER TABLE ONLY domain_einkauf.bestellung_positionen
    ADD CONSTRAINT bestellung_positionen_pkey PRIMARY KEY (id);

ALTER TABLE ONLY domain_einkauf.bestellungen
    ADD CONSTRAINT bestellungen_pkey PRIMARY KEY (id);

ALTER TABLE ONLY domain_einkauf.bestellungen
    ADD CONSTRAINT uq_bestellungen_id_tenant UNIQUE (id, tenant_id);

ALTER TABLE ONLY domain_sales.delivery_note_positions
    ADD CONSTRAINT delivery_note_positions_pkey PRIMARY KEY (id);

ALTER TABLE ONLY domain_sales.delivery_notes
    ADD CONSTRAINT delivery_notes_pkey PRIMARY KEY (id);

ALTER TABLE ONLY domain_sales.sales_credit_note_lines
    ADD CONSTRAINT sales_credit_note_lines_pkey PRIMARY KEY (id);

ALTER TABLE ONLY domain_sales.sales_credit_notes
    ADD CONSTRAINT sales_credit_notes_pkey PRIMARY KEY (id);

ALTER TABLE ONLY domain_sales.sales_delivery_notes
    ADD CONSTRAINT sales_delivery_notes_pkey PRIMARY KEY (id);

ALTER TABLE ONLY domain_sales.sales_invoice_lines
    ADD CONSTRAINT sales_invoice_lines_pkey PRIMARY KEY (id);

ALTER TABLE ONLY domain_sales.sales_invoices
    ADD CONSTRAINT sales_invoices_pkey PRIMARY KEY (id);

ALTER TABLE ONLY domain_sales.delivery_note_positions
    ADD CONSTRAINT uq_delivery_note_positions_pos_nr UNIQUE (delivery_note_id, pos_nr);

ALTER TABLE ONLY domain_sales.delivery_notes
    ADD CONSTRAINT uq_delivery_notes_id_tenant UNIQUE (id, tenant_id);

ALTER TABLE ONLY domain_sales.delivery_notes
    ADD CONSTRAINT uq_delivery_notes_tenant_number UNIQUE (tenant_id, delivery_note_number);

ALTER TABLE ONLY domain_sales.sales_credit_notes
    ADD CONSTRAINT uq_sales_credit_notes_id_tenant UNIQUE (id, tenant_id);

CREATE INDEX idx_sales_orders_tenant_date ON domain_crm.sales_orders_vor_docflow USING btree (tenant_id, created_at DESC);

CREATE INDEX idx_sales_orders_tenant_status ON domain_crm.sales_orders_vor_docflow USING btree (tenant_id, status);

CREATE INDEX ix_sales_order_items_article_number ON domain_crm.sales_order_items_vor_docflow USING btree (article_number);

CREATE INDEX ix_sales_order_items_order_id ON domain_crm.sales_order_items_vor_docflow USING btree (order_id);

CREATE INDEX ix_sales_order_items_order_tenant ON domain_crm.sales_order_items_vor_docflow USING btree (order_id, tenant_id);

CREATE INDEX ix_sales_orders_tenant_id ON domain_crm.sales_orders_vor_docflow USING btree (tenant_id);

CREATE INDEX ix_bestellung_positionen_bestellung_id ON domain_einkauf.bestellung_positionen USING btree (bestellung_id);

CREATE INDEX ix_bestellungen_tenant_id ON domain_einkauf.bestellungen USING btree (tenant_id);

CREATE INDEX ix_ek_bestellung_lieferant ON domain_einkauf.bestellungen USING btree (lieferant_id);

CREATE INDEX ix_ek_bestellung_tenant_nr ON domain_einkauf.bestellungen USING btree (tenant_id, bestellnummer);

CREATE INDEX ix_ek_bestellung_tenant_status ON domain_einkauf.bestellungen USING btree (tenant_id, status);

CREATE INDEX ix_ek_bp_bestellung ON domain_einkauf.bestellung_positionen USING btree (bestellung_id);

CREATE INDEX idx_scn_customer ON domain_sales.sales_credit_notes USING btree (customer_id);

CREATE INDEX idx_scn_tenant ON domain_sales.sales_credit_notes USING btree (tenant_id);

CREATE INDEX ix_delivery_note_positions_artikel ON domain_sales.delivery_note_positions USING btree (artikel_id);

CREATE INDEX ix_delivery_note_positions_artikel_nr ON domain_sales.delivery_note_positions USING btree (artikel_nr);

CREATE INDEX ix_delivery_note_positions_delivery_note ON domain_sales.delivery_note_positions USING btree (delivery_note_id);

CREATE INDEX ix_delivery_notes_customer ON domain_sales.delivery_notes USING btree (customer_id);

CREATE INDEX ix_delivery_notes_customer_id ON domain_sales.delivery_notes USING btree (customer_id);

CREATE INDEX ix_delivery_notes_delivery_date ON domain_sales.delivery_notes USING btree (delivery_date);

CREATE INDEX ix_delivery_notes_delivery_note_number ON domain_sales.delivery_notes USING btree (delivery_note_number);

CREATE INDEX ix_delivery_notes_sales_order ON domain_sales.delivery_notes USING btree (sales_order_id);

CREATE INDEX ix_delivery_notes_status ON domain_sales.delivery_notes USING btree (status);

CREATE INDEX ix_delivery_notes_tenant_date ON domain_sales.delivery_notes USING btree (tenant_id, delivery_date);

CREATE INDEX ix_delivery_notes_tenant_id ON domain_sales.delivery_notes USING btree (tenant_id);

CREATE INDEX ix_sales_invoice_customer ON domain_sales.sales_invoices USING btree (tenant_id, customer_id);

CREATE INDEX ix_sales_invoice_line_article ON domain_sales.sales_invoice_lines USING btree (tenant_id, article_id);

CREATE UNIQUE INDEX uq_sales_invoice_line_no ON domain_sales.sales_invoice_lines USING btree (tenant_id, invoice_id, line_no);

CREATE UNIQUE INDEX uq_sales_invoice_number ON domain_sales.sales_invoices USING btree (tenant_id, invoice_number);

CREATE TRIGGER sales_order_items_vor_docflow_unveraenderlich BEFORE INSERT OR DELETE OR UPDATE ON domain_crm.sales_order_items_vor_docflow FOR EACH ROW EXECUTE FUNCTION domain_crm.ursprungsdaten_unveraenderlich();

CREATE TRIGGER sales_orders_vor_docflow_unveraenderlich BEFORE INSERT OR DELETE OR UPDATE ON domain_crm.sales_orders_vor_docflow FOR EACH ROW EXECUTE FUNCTION domain_crm.ursprungsdaten_unveraenderlich();

ALTER TABLE ONLY domain_crm.sales_order_items_vor_docflow
    ADD CONSTRAINT fk_sales_order_items_order_id_tenant FOREIGN KEY (order_id, tenant_id) REFERENCES domain_crm.sales_orders_vor_docflow(id, tenant_id) ON DELETE CASCADE;

ALTER TABLE ONLY domain_crm.sales_order_items_vor_docflow
    ADD CONSTRAINT sales_order_items_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES domain_shared.tenants(id);

ALTER TABLE ONLY domain_crm.sales_orders_vor_docflow
    ADD CONSTRAINT sales_orders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES domain_crm.customers(id);

ALTER TABLE ONLY domain_crm.sales_orders_vor_docflow
    ADD CONSTRAINT sales_orders_sales_offer_id_fkey FOREIGN KEY (sales_offer_id) REFERENCES domain_crm.sales_offers(id);

ALTER TABLE ONLY domain_crm.sales_orders_vor_docflow
    ADD CONSTRAINT sales_orders_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES domain_shared.tenants(id);

ALTER TABLE ONLY domain_einkauf.bestellung_positionen
    ADD CONSTRAINT fk_bestellung_positionen_bestellung_id_tenant FOREIGN KEY (bestellung_id, tenant_id) REFERENCES domain_einkauf.bestellungen(id, tenant_id);

ALTER TABLE ONLY domain_einkauf.bestellung_positionen
    ADD CONSTRAINT fk_bestellung_positionen_kontrakt_pos_id_tenant FOREIGN KEY (kontrakt_pos_id, tenant_id) REFERENCES domain_einkauf.kontrakt_positionen(id, tenant_id);

ALTER TABLE ONLY domain_einkauf.bestellungen
    ADD CONSTRAINT fk_bestellungen_kontrakt_id_tenant FOREIGN KEY (kontrakt_id, tenant_id) REFERENCES domain_einkauf.kontrakte(id, tenant_id);

ALTER TABLE ONLY domain_einkauf.bestellungen
    ADD CONSTRAINT fk_bestellungen_lieferant_id_tenant FOREIGN KEY (lieferant_id, tenant_id) REFERENCES domain_einkauf.lieferanten(id, tenant_id);

ALTER TABLE ONLY domain_einkauf.bestellungen
    ADD CONSTRAINT fk_bestellungen_vorschlag_id_tenant FOREIGN KEY (vorschlag_id, tenant_id) REFERENCES domain_einkauf.bestellvorschlaege(id, tenant_id);

ALTER TABLE ONLY domain_sales.delivery_notes
    ADD CONSTRAINT delivery_notes_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES domain_crm.customers(id) ON DELETE SET NULL;

ALTER TABLE ONLY domain_sales.delivery_notes
    ADD CONSTRAINT delivery_notes_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES domain_shared.users(id) ON DELETE SET NULL;

ALTER TABLE ONLY domain_sales.delivery_notes
    ADD CONSTRAINT delivery_notes_sales_rep_id_fkey FOREIGN KEY (sales_rep_id) REFERENCES domain_shared.users(id) ON DELETE SET NULL;

ALTER TABLE ONLY domain_sales.delivery_notes
    ADD CONSTRAINT delivery_notes_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES domain_shared.tenants(id) ON DELETE CASCADE;

ALTER TABLE ONLY domain_sales.delivery_note_positions
    ADD CONSTRAINT fk_delivery_note_positions_artikel_id_tenant FOREIGN KEY (artikel_id, tenant_id) REFERENCES domain_inventory.articles(id, tenant_id) ON DELETE SET NULL (artikel_id);

ALTER TABLE ONLY domain_sales.delivery_note_positions
    ADD CONSTRAINT fk_delivery_note_positions_delivery_note_id_tenant FOREIGN KEY (delivery_note_id, tenant_id) REFERENCES domain_sales.delivery_notes(id, tenant_id) ON DELETE CASCADE;

ALTER TABLE ONLY domain_sales.delivery_notes
    ADD CONSTRAINT fk_delivery_notes_branch_id_tenant FOREIGN KEY (branch_id, tenant_id) REFERENCES domain_shared.branches(id, tenant_id) ON DELETE SET NULL (branch_id);

ALTER TABLE ONLY domain_sales.sales_credit_note_lines
    ADD CONSTRAINT fk_sales_credit_note_lines_credit_note_id_tenant FOREIGN KEY (credit_note_id, tenant_id) REFERENCES domain_sales.sales_credit_notes(id, tenant_id) ON DELETE CASCADE;

ALTER TABLE ONLY domain_sales.sales_invoice_lines
    ADD CONSTRAINT sales_invoice_lines_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES domain_sales.sales_invoices(id) ON DELETE CASCADE;

ALTER TABLE domain_crm.sales_order_items_vor_docflow ENABLE ROW LEVEL SECURITY;

ALTER TABLE domain_crm.sales_orders_vor_docflow ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_delete ON domain_crm.sales_order_items_vor_docflow FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_delete ON domain_crm.sales_orders_vor_docflow FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_insert ON domain_crm.sales_order_items_vor_docflow FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_insert ON domain_crm.sales_orders_vor_docflow FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_select ON domain_crm.sales_order_items_vor_docflow FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_select ON domain_crm.sales_orders_vor_docflow FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_update ON domain_crm.sales_order_items_vor_docflow FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_update ON domain_crm.sales_orders_vor_docflow FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

ALTER TABLE domain_einkauf.bestellung_positionen ENABLE ROW LEVEL SECURITY;

ALTER TABLE domain_einkauf.bestellungen ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_delete ON domain_einkauf.bestellung_positionen FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_delete ON domain_einkauf.bestellungen FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_insert ON domain_einkauf.bestellung_positionen FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_insert ON domain_einkauf.bestellungen FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_select ON domain_einkauf.bestellung_positionen FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_select ON domain_einkauf.bestellungen FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_update ON domain_einkauf.bestellung_positionen FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_update ON domain_einkauf.bestellungen FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

ALTER TABLE domain_sales.delivery_note_positions ENABLE ROW LEVEL SECURITY;

ALTER TABLE domain_sales.delivery_notes ENABLE ROW LEVEL SECURITY;

ALTER TABLE domain_sales.sales_credit_note_lines ENABLE ROW LEVEL SECURITY;

ALTER TABLE domain_sales.sales_credit_notes ENABLE ROW LEVEL SECURITY;

ALTER TABLE domain_sales.sales_delivery_notes ENABLE ROW LEVEL SECURITY;

ALTER TABLE domain_sales.sales_invoice_lines ENABLE ROW LEVEL SECURITY;

ALTER TABLE domain_sales.sales_invoices ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_delete ON domain_sales.delivery_note_positions FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_delete ON domain_sales.delivery_notes FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_delete ON domain_sales.sales_credit_note_lines FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_delete ON domain_sales.sales_credit_notes FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_delete ON domain_sales.sales_delivery_notes FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_delete ON domain_sales.sales_invoice_lines FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_delete ON domain_sales.sales_invoices FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_insert ON domain_sales.delivery_note_positions FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_insert ON domain_sales.delivery_notes FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_insert ON domain_sales.sales_credit_note_lines FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_insert ON domain_sales.sales_credit_notes FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_insert ON domain_sales.sales_delivery_notes FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_insert ON domain_sales.sales_invoice_lines FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_insert ON domain_sales.sales_invoices FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_select ON domain_sales.delivery_note_positions FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_select ON domain_sales.delivery_notes FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_select ON domain_sales.sales_credit_note_lines FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_select ON domain_sales.sales_credit_notes FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_select ON domain_sales.sales_delivery_notes FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_select ON domain_sales.sales_invoice_lines FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_select ON domain_sales.sales_invoices FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_update ON domain_sales.delivery_note_positions FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_update ON domain_sales.delivery_notes FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_update ON domain_sales.sales_credit_note_lines FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_update ON domain_sales.sales_credit_notes FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_update ON domain_sales.sales_delivery_notes FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_update ON domain_sales.sales_invoice_lines FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE POLICY tenant_isolation_update ON domain_sales.sales_invoices FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));

CREATE VIEW domain_crm.sales_order_items WITH (security_invoker='true') AS
 SELECT i.id,
    i.tenant_id,
    i.header_id AS order_id,
    i.line_number,
    i.article_number,
    i.description,
    i.quantity,
    i.unit,
    i.unit_price,
    NULL::numeric AS ek_price,
    i.discount_percent,
    i.line_total_net AS line_total,
    i.created_at,
    i.updated_at,
    GREATEST((i.quantity - GREATEST(COALESCE(( SELECT sum(l.quantity_linked) AS sum
           FROM (domain_docflow.document_links l
             JOIN domain_docflow.document_headers z ON ((((z.id)::text = (l.to_header_id)::text) AND ((z.tenant_id)::text = (l.tenant_id)::text))))
          WHERE (((l.tenant_id)::text = (i.tenant_id)::text) AND ((l.from_header_id)::text = (i.header_id)::text) AND ((l.from_item_id)::text = (i.id)::text) AND ((l.relation_type)::text = 'order_to_delivery'::text) AND (z.deleted_at IS NULL) AND ((z.status)::text <> ALL ((ARRAY['reversed'::character varying, 'cancelled'::character varying])::text[])))), (0)::numeric), COALESCE(( SELECT sum(l.quantity_linked) AS sum
           FROM (domain_docflow.document_links l
             JOIN domain_docflow.document_headers z ON ((((z.id)::text = (l.to_header_id)::text) AND ((z.tenant_id)::text = (l.tenant_id)::text))))
          WHERE (((l.tenant_id)::text = (i.tenant_id)::text) AND ((l.from_header_id)::text = (i.header_id)::text) AND ((l.from_item_id)::text = (i.id)::text) AND ((l.relation_type)::text = 'order_to_invoice'::text) AND (z.deleted_at IS NULL) AND ((z.status)::text <> ALL ((ARRAY['reversed'::character varying, 'cancelled'::character varying])::text[])))), (0)::numeric))), (0)::numeric) AS offene_menge
   FROM (domain_docflow.document_items i
     JOIN domain_docflow.document_headers h ON ((((h.id)::text = (i.header_id)::text) AND ((h.tenant_id)::text = (i.tenant_id)::text))))
  WHERE ((h.doc_type)::text = 'sales_order'::text);

COMMENT ON VIEW domain_crm.sales_order_items IS 'Leseweg: Auftragspositionen aus DocFlow (BELEG-052).';

CREATE VIEW domain_crm.sales_orders WITH (security_invoker='true') AS
 SELECT h.id,
    h.tenant_id,
    ( SELECT l.from_header_id
           FROM domain_docflow.document_links l
          WHERE (((l.to_header_id)::text = (h.id)::text) AND ((l.tenant_id)::text = (h.tenant_id)::text) AND ((l.relation_type)::text = 'offer_to_order'::text))
          ORDER BY l.created_at
         LIMIT 1) AS sales_offer_id,
    h.customer_id,
    ( SELECT c.company_name
           FROM domain_crm.customers c
          WHERE (((c.id)::text = (h.customer_id)::text) AND ((c.tenant_id)::text = (h.tenant_id)::text))
         LIMIT 1) AS customer_name,
    h.doc_number AS order_number,
    (h.bausteine #>> '{texte,betreff}'::text[]) AS subject,
    (h.bausteine #>> '{texte,kopftext}'::text[]) AS description,
    h.total_gross AS total_amount,
    h.currency,
        CASE h.status
            WHEN 'reversed'::text THEN 'cancelled'::character varying
            ELSE h.status
        END AS status,
    (h.bausteine #>> '{kontakt,ansprechpartner}'::text[]) AS contact_person,
        CASE
            WHEN ((h.bausteine #>> '{lieferung,liefertermin}'::text[]) ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'::text) THEN (((h.bausteine #>> '{lieferung,liefertermin}'::text[]))::date)::timestamp with time zone
            ELSE NULL::timestamp with time zone
        END AS delivery_date,
    (h.bausteine #>> '{lieferung,lieferadresse}'::text[]) AS delivery_address,
    (h.bausteine #>> '{lieferung,versandart}'::text[]) AS shipping_method,
    (h.bausteine #>> '{zahlung,zahlungsbedingung}'::text[]) AS payment_terms,
    (h.bausteine #>> '{texte,notiz}'::text[]) AS notes,
    false AS is_pauschale,
    h.created_at,
    h.updated_at,
    h.deleted_at,
    h.version,
    h.printed_at,
    h.print_count,
    NULL::timestamp with time zone AS posted_at
   FROM domain_docflow.document_headers h
  WHERE ((h.doc_type)::text = 'sales_order'::text);

COMMENT ON VIEW domain_crm.sales_orders IS 'Leseweg: Verkaufsauftraege aus DocFlow (BELEG-052). Schreiben nur ueber die Belegmaske.';
