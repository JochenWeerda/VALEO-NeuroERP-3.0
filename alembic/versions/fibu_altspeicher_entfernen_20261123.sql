--
-- PostgreSQL database dump
--


-- Dumped from database version 15.14
-- Dumped by pg_dump version 15.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: anlagen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.anlagen (
    id character varying(36) NOT NULL,
    tenant_id character varying(36) NOT NULL,
    anlagennr character varying(20) NOT NULL,
    bezeichnung character varying(200) NOT NULL,
    anschaffung date NOT NULL,
    anschaffungswert numeric(10,2) NOT NULL,
    nutzungsdauer integer NOT NULL,
    afa_satz numeric(5,2) NOT NULL,
    kumulierte_afa numeric(10,2),
    buchwert numeric(10,2) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: buchungen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.buchungen (
    id character varying(36) NOT NULL,
    tenant_id character varying(36) NOT NULL,
    belegnr character varying(50) NOT NULL,
    datum date NOT NULL,
    soll_konto character varying(10) NOT NULL,
    haben_konto character varying(10) NOT NULL,
    betrag numeric(10,2) NOT NULL,
    text character varying(200) NOT NULL,
    belegart character varying(10) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: konten; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.konten (
    id character varying(36) NOT NULL,
    tenant_id character varying(36) NOT NULL,
    kontonummer character varying(10) NOT NULL,
    bezeichnung character varying(100) NOT NULL,
    kontoart character varying(50) NOT NULL,
    typ character varying(20) NOT NULL,
    saldo numeric(10,2),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: offene_posten; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.offene_posten (
    id character varying(36) NOT NULL,
    tenant_id character varying(36) NOT NULL,
    rechnungsnr character varying(50) NOT NULL,
    datum date NOT NULL,
    faelligkeit date NOT NULL,
    betrag numeric(10,2) NOT NULL,
    offen numeric(10,2) NOT NULL,
    kunde_id character varying(36),
    kunde_name character varying(100),
    lieferant_id character varying(36),
    lieferant_name character varying(100),
    skonto_prozent numeric(5,2),
    skonto_bis date,
    mahn_stufe integer,
    zahlbar boolean,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    konto_nr character varying(40),
    konto_name character varying(255),
    konto_typ character varying(20) DEFAULT 'debitoren'::character varying NOT NULL,
    op_status character varying(20) DEFAULT 'offen'::character varying NOT NULL,
    rechnungsdatum date,
    valuta date,
    op_betrag numeric(14,2),
    saldo numeric(14,2),
    op_text character varying(255),
    waehrung character varying(3) DEFAULT 'EUR'::character varying NOT NULL,
    letzte_bewegung_am date,
    kredit_limit numeric(14,2),
    kv_limit numeric(14,2),
    sperre_grund character varying(255),
    CONSTRAINT ck_offene_posten_amounts_nonnegative CHECK (((betrag >= (0)::numeric) AND (offen >= (0)::numeric) AND ((op_betrag IS NULL) OR (op_betrag >= (0)::numeric)))),
    CONSTRAINT ck_offene_posten_konto_typ CHECK (((konto_typ)::text = ANY ((ARRAY['debitoren'::character varying, 'kreditoren'::character varying])::text[]))),
    CONSTRAINT ck_offene_posten_op_status CHECK (((op_status)::text = ANY ((ARRAY['offen'::character varying, 'teilweise'::character varying, 'geschlossen'::character varying, 'storniert'::character varying])::text[])))
);


--
-- Name: anlagen anlagen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anlagen
    ADD CONSTRAINT anlagen_pkey PRIMARY KEY (id);


--
-- Name: buchungen buchungen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.buchungen
    ADD CONSTRAINT buchungen_pkey PRIMARY KEY (id);


--
-- Name: konten konten_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.konten
    ADD CONSTRAINT konten_pkey PRIMARY KEY (id);


--
-- Name: offene_posten offene_posten_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.offene_posten
    ADD CONSTRAINT offene_posten_pkey PRIMARY KEY (id);


--
-- Name: ix_anlagen_anlagennr; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_anlagen_anlagennr ON public.anlagen USING btree (anlagennr);


--
-- Name: ix_anlagen_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_anlagen_tenant_id ON public.anlagen USING btree (tenant_id);


--
-- Name: ix_buchungen_belegnr; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_buchungen_belegnr ON public.buchungen USING btree (belegnr);


--
-- Name: ix_buchungen_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_buchungen_tenant_id ON public.buchungen USING btree (tenant_id);


--
-- Name: ix_konten_kontonummer; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_konten_kontonummer ON public.konten USING btree (kontonummer);


--
-- Name: ix_konten_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_konten_tenant_id ON public.konten USING btree (tenant_id);


--
-- Name: ix_offene_posten_faelligkeit_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_offene_posten_faelligkeit_status ON public.offene_posten USING btree (faelligkeit, op_status);


--
-- Name: ix_offene_posten_konto_nr; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_offene_posten_konto_nr ON public.offene_posten USING btree (konto_nr);


--
-- Name: ix_offene_posten_konto_typ; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_offene_posten_konto_typ ON public.offene_posten USING btree (konto_typ);


--
-- Name: ix_offene_posten_op_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_offene_posten_op_status ON public.offene_posten USING btree (op_status);


--
-- Name: ix_offene_posten_rechnungsnr; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_offene_posten_rechnungsnr ON public.offene_posten USING btree (rechnungsnr);


--
-- Name: ix_offene_posten_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_offene_posten_tenant_id ON public.offene_posten USING btree (tenant_id);


--
-- Name: anlagen; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.anlagen ENABLE ROW LEVEL SECURITY;

--
-- Name: buchungen; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.buchungen ENABLE ROW LEVEL SECURITY;

--
-- Name: konten; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.konten ENABLE ROW LEVEL SECURITY;

--
-- Name: offene_posten; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.offene_posten ENABLE ROW LEVEL SECURITY;

--
-- Name: anlagen tenant_isolation_delete; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_delete ON public.anlagen FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));


--
-- Name: buchungen tenant_isolation_delete; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_delete ON public.buchungen FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));


--
-- Name: konten tenant_isolation_delete; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_delete ON public.konten FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));


--
-- Name: offene_posten tenant_isolation_delete; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_delete ON public.offene_posten FOR DELETE USING (((tenant_id)::text = public.rls_current_tenant()));


--
-- Name: anlagen tenant_isolation_insert; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_insert ON public.anlagen FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));


--
-- Name: buchungen tenant_isolation_insert; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_insert ON public.buchungen FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));


--
-- Name: konten tenant_isolation_insert; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_insert ON public.konten FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));


--
-- Name: offene_posten tenant_isolation_insert; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_insert ON public.offene_posten FOR INSERT WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));


--
-- Name: anlagen tenant_isolation_select; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_select ON public.anlagen FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));


--
-- Name: buchungen tenant_isolation_select; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_select ON public.buchungen FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));


--
-- Name: konten tenant_isolation_select; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_select ON public.konten FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));


--
-- Name: offene_posten tenant_isolation_select; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_select ON public.offene_posten FOR SELECT USING (((tenant_id)::text = public.rls_current_tenant()));


--
-- Name: anlagen tenant_isolation_update; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_update ON public.anlagen FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));


--
-- Name: buchungen tenant_isolation_update; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_update ON public.buchungen FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));


--
-- Name: konten tenant_isolation_update; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_update ON public.konten FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));


--
-- Name: offene_posten tenant_isolation_update; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_update ON public.offene_posten FOR UPDATE USING (((tenant_id)::text = public.rls_current_tenant())) WITH CHECK (((tenant_id)::text = public.rls_current_tenant()));


--
-- PostgreSQL database dump complete
--


