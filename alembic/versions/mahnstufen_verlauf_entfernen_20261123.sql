CREATE TABLE domain_finance.finance_mahnstufen_audit (
    id character varying(36) NOT NULL,
    tenant_id character varying(36) NOT NULL,
    rechnungsnr character varying(60) NOT NULL,
    stufe character varying(20) NOT NULL,
    operator character varying(100),
    bearbeitungsgebuehr_eur numeric(10,2),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);
ALTER TABLE ONLY domain_finance.finance_mahnstufen_audit
    ADD CONSTRAINT finance_mahnstufen_audit_pkey PRIMARY KEY (id);
CREATE INDEX ix_mahnstufen_audit_rechnung ON domain_finance.finance_mahnstufen_audit USING btree (rechnungsnr, tenant_id);
ALTER TABLE domain_finance.finance_mahnstufen_audit ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_delete ON domain_finance.finance_mahnstufen_audit FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));
CREATE POLICY tenant_isolation_insert ON domain_finance.finance_mahnstufen_audit FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));
CREATE POLICY tenant_isolation_select ON domain_finance.finance_mahnstufen_audit FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));
CREATE POLICY tenant_isolation_update ON domain_finance.finance_mahnstufen_audit FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));
