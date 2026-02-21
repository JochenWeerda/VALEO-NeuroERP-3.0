"""
L3-Connect Gap Closure Models
Database models for inventory extensions, logistics, messaging, webhooks,
and master-data tables required for L3-Connect API parity.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Text, ForeignKey, DECIMAL, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from ...core.database import Base
from ...core.uuid7 import uuid7


# ── Inventory Count Lines ────────────────────────────────────────

class InventoryCountLine(Base):
    """Individual line item within an inventory count."""
    __tablename__ = "inventory_count_lines"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    inventory_count_id = Column(String, ForeignKey("domain_inventory.inventory_counts.id"), nullable=False)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    expected_qty = Column(DECIMAL(12, 3), default=0)
    counted_qty = Column(DECIMAL(12, 3), default=0)
    difference = Column(DECIMAL(12, 3), default=0)
    warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=True)
    bin_location_id = Column(String, nullable=True)
    batch_number = Column(String(50), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ── Weighing Tickets ─────────────────────────────────────────────

class WeighingTicket(Base):
    """Wiegeschein header."""
    __tablename__ = "weighing_tickets"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    ticket_number = Column(String(50), nullable=False)
    scale_id = Column(String(50), nullable=True)
    vehicle_plate = Column(String(20), nullable=True)
    gross_weight = Column(DECIMAL(12, 3), nullable=True)
    tare_weight = Column(DECIMAL(12, 3), nullable=True)
    net_weight = Column(DECIMAL(12, 3), nullable=True)
    first_weighing_at = Column(DateTime(timezone=True), nullable=True)
    second_weighing_at = Column(DateTime(timezone=True), nullable=True)
    moisture_pct = Column(DECIMAL(5, 2), nullable=True)
    protein_pct = Column(DECIMAL(5, 2), nullable=True)
    impurities_pct = Column(DECIMAL(5, 2), nullable=True)
    hl_weight = Column(DECIMAL(6, 2), nullable=True)
    billing_weight = Column(DECIMAL(12, 3), nullable=True)
    quality_data = Column(JSONB, nullable=True)
    contract_id = Column(String, ForeignKey("domain_inventory.agrar_contracts.id"), nullable=True)
    allocated_quantity_kg = Column(DECIMAL(12, 3), nullable=True)
    allocation_status = Column(String(20), nullable=False, default="unallocated")  # unallocated / allocated / posted
    weighing_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="open")
    direction = Column(String(10), default="in")  # in / out
    reference_doc = Column(String(100), nullable=True)
    article_group = Column(String(80), nullable=True, comment="Warengruppe/Artikelgruppe")
    article_id = Column(String, ForeignKey("domain_inventory.articles.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True, comment="Notizen/Bemerkungen")
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WeighingTicketLine(Base):
    """Wiegeschein position."""
    __tablename__ = "weighing_ticket_lines"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    ticket_id = Column(String, ForeignKey("domain_inventory.weighing_tickets.id"), nullable=False)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    quantity = Column(DECIMAL(12, 3), nullable=False)
    unit = Column(String(10), default="kg")
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WeighingMeasurement(Base):
    """Wiegeschein quality measurement entries."""
    __tablename__ = "weighing_measurements"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    ticket_id = Column(String, ForeignKey("domain_inventory.weighing_tickets.id"), nullable=False)
    metric_key = Column(String(50), nullable=False)
    metric_value = Column(DECIMAL(10, 3), nullable=False)
    unit = Column(String(20), nullable=True)
    measured_at = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AgrarContract(Base):
    """Agrar contract (buy/sell) with quantity tracking."""
    __tablename__ = "agrar_contracts"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    contract_number = Column(String(50), nullable=False)
    contract_type = Column(String(10), nullable=False)  # buy / sell
    harvest_year = Column(Integer, nullable=False)
    partner_id = Column(String(64), nullable=False)
    article_id = Column(String(64), nullable=False)
    pricing_model = Column(String(10), nullable=False)  # fixed / follow / pool
    pool_group_id = Column(String(64), nullable=True)
    fixed_price = Column(DECIMAL(12, 2), nullable=True)
    currency = Column(String(3), nullable=False, default="EUR")
    total_quantity_kg = Column(DECIMAL(12, 3), nullable=False)
    remaining_quantity_kg = Column(DECIMAL(12, 3), nullable=False)
    status = Column(String(20), nullable=False, default="open")  # open / partially_allocated / fulfilled / cancelled
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AgrarContractAllocation(Base):
    """Allocation entries against an agrar contract."""
    __tablename__ = "agrar_contract_allocations"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    contract_id = Column(String, ForeignKey("domain_inventory.agrar_contracts.id"), nullable=False)
    ticket_id = Column(String, ForeignKey("domain_inventory.weighing_tickets.id"), nullable=True)
    allocation_quantity_kg = Column(DECIMAL(12, 3), nullable=False)
    allocated_at = Column(DateTime(timezone=True), server_default=func.now())
    note = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AgrarSettlement(Base):
    """Self-billing settlement header."""
    __tablename__ = "agrar_settlements"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    settlement_number = Column(String(50), nullable=False)
    contract_id = Column(String, ForeignKey("domain_inventory.agrar_contracts.id"), nullable=True)
    ticket_id = Column(String, ForeignKey("domain_inventory.weighing_tickets.id"), nullable=True)
    supplier_id = Column(String(64), nullable=False)
    article_id = Column(String(64), nullable=True)
    gross_quantity_kg = Column(DECIMAL(12, 3), nullable=False)
    billing_quantity_kg = Column(DECIMAL(12, 3), nullable=False)
    unit_price_eur_per_ton = Column(DECIMAL(12, 4), nullable=False)
    gross_amount_eur = Column(DECIMAL(14, 2), nullable=False)
    total_deductions_eur = Column(DECIMAL(14, 2), nullable=False, default=0)
    net_amount_eur = Column(DECIMAL(14, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")
    status = Column(String(20), nullable=False, default="draft")  # draft / posted / cancelled
    posted_journal_ref = Column(String(80), nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    note = Column(Text, nullable=True)
    # Drying/audit snapshot (computed invoice weight/loss/fee + used rule references)
    drying_result = Column(JSONB, nullable=False, default=dict)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DryingRuleSet(Base):
    """
    Configurable drying rules for invoice weight/loss/fee by crop/site and validity.
    
    Fester Vertragsteil jedes Ankaufskontrakts:
    - Allgemeingültige Tabellen: contract_id=NULL, customer_id=NULL, is_customer_specific=False
    - Kundenspezifische Sonderregelungen: customer_id gesetzt, is_customer_specific=True, justification erforderlich
    - Vertragsverknüpfung: contract_id gesetzt (für automatische Zuordnung)
    - DMS-Referenz: document_id für Tabelle/Formel-Dokument (Papierform oder Portal-Download)
    - Versionsverwaltung: version, created_at/created_by, updated_at/updated_by
    - Schreibrechte: Nur Admin (Rollenprüfung in API)
    """
    __tablename__ = "drying_rule_sets"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    crop_code = Column(String(40), nullable=False)
    site_id = Column(String(64), nullable=True)
    valid_from = Column(Date, nullable=True)
    valid_to = Column(Date, nullable=True)
    version = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, nullable=False, default=True)

    method = Column(String(40), nullable=False)  # LOOKUP_TABLE | FACTOR_FROM_BASE | DRY_MATTER_NORMALIZATION
    base_moisture_pct = Column(DECIMAL(5, 2), nullable=False)
    rounding_mode = Column(String(20), nullable=False, default="ROUND_NEAREST")  # ROUND_NEAREST|ROUND_UP|ROUND_DOWN
    clamp_mode = Column(String(20), nullable=False, default="HARD_ERROR")  # CLAMP_TO_MAX|HARD_ERROR
    min_moisture_pct = Column(DECIMAL(5, 2), nullable=False, default=0)
    max_moisture_pct = Column(DECIMAL(5, 2), nullable=False, default=60)
    start_threshold_moisture_pct = Column(DECIMAL(5, 2), nullable=True)  # for FACTOR_FROM_BASE
    fee_basis = Column(String(20), nullable=False, default="INVOICE_WEIGHT")  # INVOICE_WEIGHT|NET_WEIGHT

    # Audit fields (Versionsverwaltung)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(64), nullable=True, comment="User-ID der Person, die die Regel angelegt hat")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String(64), nullable=True, comment="User-ID der Person, die die Regel zuletzt geändert hat")

    # Vertragsverknüpfung (fester Vertragsteil)
    contract_id = Column(String, ForeignKey("domain_inventory.agrar_contracts.id"), nullable=True, comment="Verknüpfung zu Ankaufskontrakt (optional)")

    # Kundenspezifische Sonderregelungen
    customer_id = Column(String, ForeignKey("domain_crm.customers.id"), nullable=True, comment="Kunde für Sonderregelung (optional)")
    is_customer_specific = Column(Boolean, nullable=False, default=False, comment="True = kundenspezifische Sonderregelung (justification erforderlich)")
    justification = Column(Text, nullable=True, comment="Begründung für kundenspezifische Sonderregelungen (z.B. 'Freigrenze ab 15,5% Feuchte')")

    # DMS-Referenz (Tabelle/Formel-Dokument)
    document_id = Column(String(64), nullable=True, comment="DMS-Referenz für Tabelle/Formel-Dokument (Papierform oder Portal-Download)")


class DryingRuleLookupRow(Base):
    """Lookup table row: moisture -> entzug points, loss %, optional fee."""
    __tablename__ = "drying_rule_lookup_rows"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    rule_set_id = Column(String, ForeignKey("domain_inventory.drying_rule_sets.id"), nullable=False)
    moisture_pct = Column(DECIMAL(5, 1), nullable=False)  # 0.1 steps
    entzug_pct_points = Column(DECIMAL(5, 1), nullable=False)
    loss_pct = Column(DECIMAL(8, 4), nullable=False)
    fee_value = Column(DECIMAL(12, 4), nullable=True)
    fee_unit = Column(String(20), nullable=True)  # EUR_PER_T|EUR_PER_DT|EUR_FIXED
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DryingRuleFactorRange(Base):
    """Factor ranges for FACTOR_FROM_BASE: moisture range -> factor."""
    __tablename__ = "drying_rule_factor_ranges"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    rule_set_id = Column(String, ForeignKey("domain_inventory.drying_rule_sets.id"), nullable=False)
    from_moisture_incl = Column(DECIMAL(5, 1), nullable=False)
    to_moisture_incl = Column(DECIMAL(5, 1), nullable=False)
    factor = Column(DECIMAL(8, 4), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AgrarSettlementDeduction(Base):
    """Settlement deduction lines (drying/cleaning/freight/etc)."""
    __tablename__ = "agrar_settlement_deductions"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    settlement_id = Column(String, ForeignKey("domain_inventory.agrar_settlements.id"), nullable=False)
    deduction_type = Column(String(30), nullable=False)  # drying / cleaning / freight / other
    mode = Column(String(20), nullable=False)  # per_ton / fixed
    rate_per_ton_eur = Column(DECIMAL(12, 4), nullable=True)
    fixed_amount_eur = Column(DECIMAL(14, 2), nullable=True)
    basis_quantity_tons = Column(DECIMAL(12, 3), nullable=True)
    amount_eur = Column(DECIMAL(14, 2), nullable=False)
    note = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Harvest Acceptance (Ernte-Annahme) ────────────────────────────────────────

class HarvestAcceptance(Base):
    """
    Ernte-Annahme (Harvest Acceptance) - Hauptbeleg für Anlieferung, Verwiegung, Qualitätsprüfung, Abrechnung.
    
    NUTS-2-Code:
    - Bedeutung: "Herkunft/Region der Erzeugung" (nicht Standort des Lagers)
    - Hauptzweck: Nachhaltigkeitsnachweise / Biomasse-Zertifizierung (RED-II, ISCC, REDcert, SURE)
    - Speicherung: Am Delivery-Event (Anlieferung), als Snapshot mit Version
    - Ableitung: Aus Herkunftsadresse (PLZ/Ort → NUTS-2 über offizielle Tabellen)
    - Mischladung: Pro Position origin_nuts2_code (siehe HarvestAcceptancePosition)
    """
    __tablename__ = "harvest_acceptances"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    acceptance_number = Column(String(50), nullable=False, comment="Annahmeschein-Nummer (fortlaufend)")
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)

    # Header-Bereich
    branch_id = Column(String, ForeignKey("domain_shared.branches.id"), nullable=True, comment="Niederlassung")
    warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=True, comment="Lagerhalle")
    delivery_date = Column(Date, nullable=False, comment="Liefer-Datum")
    delivery_time = Column(String(8), nullable=True, comment="Uhrzeit (HH:MM)")
    sales_rep_id = Column(String(64), nullable=True, comment="VB (Vertreter)")
    operator_id = Column(String(64), nullable=False, comment="Bediener (aktueller Benutzer)")
    weighing_ticket_id = Column(String, ForeignKey("domain_inventory.weighing_tickets.id"), nullable=True, comment="Wiegesch.-Nr.")
    cost_center_id = Column(String(64), nullable=True, comment="Kostenstelle")

    # Kunden-Bereich
    customer_id = Column(String, ForeignKey("domain_crm.customers.id"), nullable=False, comment="Debitor-Kto.")
    contract_id = Column(String, ForeignKey("domain_inventory.agrar_contracts.id"), nullable=True, comment="Kontrakt-Nr.")
    forwarder_id = Column(String, ForeignKey("domain_crm.business_partners.id"), nullable=True, comment="Spediteur-Kto.")
    intermediate_dealer_id = Column(String, ForeignKey("domain_crm.business_partners.id"), nullable=True, comment="Zw-Händler-Kto.")
    deviating_vat_id = Column(String(20), nullable=True, comment="Abweichende USTID")

    # ANLIEFERUNG Tab
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=True, comment="Artikel-Nr.")
    variety_id = Column(String(64), nullable=True, comment="Sorte")
    vehicle_plate = Column(String(20), nullable=True, comment="Fahrzeug-Kennzeichen")

    # NUTS-2 (Herkunft/Region der Erzeugung) - Header-Level (für einfache Anlieferungen)
    origin_nuts2_code = Column(String(10), nullable=True, comment="NUTS-2-Code der Herkunft (Region der Erzeugung/Anbau)")
    nuts_version = Column(String(20), nullable=True, default="NUTS 2024", comment="NUTS-Version (z.B. 'NUTS 2024') für Audit")
    origin_postal_code = Column(String(10), nullable=True, comment="PLZ der Herkunft (für Ableitung/Validierung)")
    origin_city = Column(String(100), nullable=True, comment="Ort der Herkunft (für Ableitung/Validierung)")
    origin_country_code = Column(String(2), nullable=True, default="DE", comment="Ländercode der Herkunft (ISO 3166-1 alpha-2)")

    # Nachhaltigkeit
    is_sustainable_biomass = Column(Boolean, nullable=False, default=False, comment="Nachhaltige Biomasse (für RED-II/ISCC/REDcert)")

    # Status (erweitert nach praxisnahen Default-Entscheidungen)
    release_status = Column(String(20), nullable=False, default="draft", comment="Freigabe: draft / provisional / final / credit_note_created / paid / disputed / cancelled")
    provisional_invoice_number = Column(String(50), nullable=True, comment="vorl. Rechn.-Nr.")
    invoice_id = Column(String(64), nullable=True, comment="FK zu invoice (Gutschrift)")
    invoice_number = Column(String(50), nullable=True, comment="Rechnungs-Nr. (nach Gutschrift)")
    
    # Preisermittlung (nach praxisnahen Default-Entscheidungen)
    pricing_mode = Column(String(20), nullable=False, default="spot_daily", comment="Preismodell: fixed_contract / spot_daily / exchange_fix_later")
    price_source_id = Column(String(64), nullable=True, comment="Referenz zu Preisquelle (daily_price_id, exchange_index_id, etc.)")
    
    # Belegkette-Referenzen
    stock_movement_id = Column(String, ForeignKey("domain_inventory.inventory_stock_movements.id"), nullable=True, comment="Referenz zu Wareneingang (wird bei Freigabe erstellt)")
    quality_protocol_id = Column(String(64), nullable=True, comment="Referenz zu Qualitätsprotokoll")

    # Bemerkungen
    remarks = Column(Text, nullable=True, comment="Bemerkungen")
    print_remarks_on_acceptance_note = Column(Boolean, nullable=False, default=False)
    print_remarks_on_settlement = Column(Boolean, nullable=False, default=False)

    # Summen
    total_net_amount_eur = Column(DECIMAL(15, 2), nullable=True, comment="Netto-Betrag")
    total_vat_amount_eur = Column(DECIMAL(15, 2), nullable=True, comment="MWSt-Betrag")
    total_gross_amount_eur = Column(DECIMAL(15, 2), nullable=True, comment="Brutto-Betrag")
    vat_rate_percent = Column(DECIMAL(5, 2), nullable=True, comment="MWSt %")
    
    # VAT/Steuer-Modi (für Vorsteuerabzug und Geschäftsmodell)
    acceptance_mode = Column(String(30), nullable=True, default="PURCHASE_AT_DELIVERY_PTBF", comment="Geschäftsmodell: STORAGE_ONLY (Fremdware, keine Vorsteuer) / PURCHASE_AT_DELIVERY_PTBF (Ankauf jetzt, Preis später, Vorsteuer möglich) / ADVANCE_ON_STORAGE (Einlagerung + Abschlag/Anzahlung)")
    ownership_type = Column(String(20), nullable=True, default="OWN_STOCK", comment="Eigentumsverhältnis: THIRD_PARTY_STOCK (Fremdware) / OWN_STOCK (Eigene Ware)")
    vat_event = Column(String(40), nullable=True, default="NO_INVOICE", comment="VAT-Ereignis: NO_INVOICE (Storage) / PROVISIONAL_CREDIT_NOTE_CREATED / FINAL_CREDIT_NOTE_CREATED / CORRECTION_ISSUED")
    
    # Anzahlung (für ADVANCE_ON_STORAGE)
    advance_payment_amount_eur = Column(DECIMAL(14, 2), nullable=True, comment="Anzahlungsbetrag (EUR) - für ADVANCE_ON_STORAGE Modus")
    advance_payment_date = Column(Date, nullable=True, comment="Anzahlungsdatum - für ADVANCE_ON_STORAGE Modus")
    advance_invoice_id = Column(String, ForeignKey("domain_inventory.self_billing_invoices.id", ondelete="SET NULL"), nullable=True, comment="Referenz auf Anzahlungsrechnung/-gutschrift")

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(64), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String(64), nullable=True)


class HarvestAcceptancePosition(Base):
    """
    Ernte-Annahme Position (für Mischladungen: mehrere Herkunftsorte/Artikel).
    
    NUTS-2 pro Position:
    - Bei Mischladungen: Jede Position kann eigene Herkunft (origin_nuts2_code) haben
    - Summe der Positionen = Gesamtmenge der Anlieferung
    """
    __tablename__ = "harvest_acceptance_positions"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    harvest_acceptance_id = Column(String, ForeignKey("domain_inventory.harvest_acceptances.id"), nullable=False)
    position_number = Column(Integer, nullable=False, comment="Positionsnummer (10, 15, 20, ...)")
    description = Column(String(200), nullable=False, comment="Bezeichnung (z.B. 'Angelieferte Menge', 'Windabgang', ...)")

    # Berechnungslogik
    is_printable = Column(Boolean, nullable=False, default=True, comment="Soll auf Druckausgabe?")
    is_calculable = Column(Boolean, nullable=False, default=True, comment="Soll berechnet werden?")
    lab_value_pct = Column(DECIMAL(5, 2), nullable=True, comment="Laborwert (Prozent)")
    quantity_kg = Column(DECIMAL(12, 3), nullable=True, comment="Menge (kg)")
    unit = Column(String(20), nullable=True, comment="Einheit (kg, %, Mon., Euro/St)")
    price_per_unit_eur = Column(DECIMAL(10, 2), nullable=True, comment="Preis EUR pro Einheit")
    amount_eur = Column(DECIMAL(15, 2), nullable=True, comment="Betrag EUR")
    calculation_formula = Column(Text, nullable=True, comment="Berechnungsformel (für Audit/Nachvollziehbarkeit)")

    # NUTS-2 pro Position (für Mischladungen)
    origin_nuts2_code = Column(String(10), nullable=True, comment="NUTS-2-Code der Herkunft (Region der Erzeugung/Anbau) für diese Position")
    nuts_version = Column(String(20), nullable=True, default="NUTS 2024", comment="NUTS-Version (z.B. 'NUTS 2024') für Audit")
    origin_postal_code = Column(String(10), nullable=True, comment="PLZ der Herkunft (für Ableitung/Validierung)")
    origin_city = Column(String(100), nullable=True, comment="Ort der Herkunft (für Ableitung/Validierung)")
    origin_country_code = Column(String(2), nullable=True, default="DE", comment="Ländercode der Herkunft (ISO 3166-1 alpha-2)")

    # Artikel/Sorte (falls Position-spezifisch)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=True, comment="Artikel-Nr. (falls abweichend vom Header)")
    variety_id = Column(String(64), nullable=True, comment="Sorte (falls abweichend vom Header)")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HarvestAcceptanceLine(Base):
    """
    Ernte-Annahme Zeilen für Verteilungen (Silo/Partie-Splits).
    
    Default: 1 Wiegeschein = 1 Ernte-Annahme, aber mit Zeilen für Verteilungen.
    Constraint: Sum(line.qty) = Wiegeschein.netto (± Rundungstoleranz).
    """
    __tablename__ = "harvest_acceptance_lines"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    harvest_acceptance_id = Column(String, ForeignKey("domain_inventory.harvest_acceptances.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False, comment="Zeilennummer (1, 2, 3, ...)")
    silo_id = Column(String(64), nullable=True, comment="Silo-Nr./Lagerort")
    lot_id = Column(String(64), nullable=True, comment="Partie/Charge")
    qty_kg_allocated = Column(DECIMAL(12, 3), nullable=False, comment="Zugeordnete Menge (kg)")
    notes = Column(Text, nullable=True, comment="Bemerkungen zur Verteilung")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SupplierTaxProfile(Base):
    """
    Steuerprofil am Lieferanten (mit Gültigkeit).
    
    Default: eigene Tabelle für taxation_type mit Gültigkeit.
    Priorität: Lieferant-Profil > Artikel/Warengruppe > Standard
    """
    __tablename__ = "supplier_tax_profiles"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    supplier_id = Column(String, ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, comment="Lieferant (Business Partner)")
    taxation_type = Column(String(20), nullable=False, comment="Besteuerungsart: regular / ustg24_flat_rate / small_business")
    vat_id = Column(String(30), nullable=True, comment="USt-ID (optional)")
    valid_from = Column(Date, nullable=False, comment="Gültig ab")
    valid_to = Column(Date, nullable=True, comment="Gültig bis (NULL = unbegrenzt)")
    notes = Column(Text, nullable=True, comment="Hinweise/Texts")
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(64), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String(64), nullable=True)


class PriceAdjustmentRule(Base):
    """
    Rule-Tabellen für Zu-/Abschläge (produkt- & gültigkeitsbezogen).
    
    Default: Rules konfigurierbar, nicht hart codieren.
    Beispiele: HL-Gewicht, Besatz-Staffel, Mykotoxin, etc.
    """
    __tablename__ = "price_adjustment_rules"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=True, comment="Artikel (optional, wenn warengruppe-basiert)")
    warengruppe = Column(String(80), nullable=True, comment="Warengruppe (optional, wenn artikel-basiert)")
    adjustment_type = Column(String(30), nullable=False, comment="Typ: hl_weight / impurity / mycotoxin / other")
    parameter_name = Column(String(50), nullable=False, comment="Parameter (z.B. 'hl_weight_kg_per_hl', 'impurity_pct')")
    method = Column(String(20), nullable=False, comment="Methode: table / factor / percentage")
    steps = Column(JSONB(astext_type=Text()), nullable=True, comment="Staffeln/Tabelle (JSONB)")
    effective_from = Column(Date, nullable=False, comment="Gültig ab")
    effective_to = Column(Date, nullable=True, comment="Gültig bis (NULL = unbegrenzt)")
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(64), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String(64), nullable=True)


class NawaroPrintNotification(Base):
    """NaWaRo print message request header."""
    __tablename__ = "nawaro_print_notifications"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    document_name = Column(String(255), nullable=False)
    harvest_year = Column(Integer, nullable=False)
    article_number = Column(String(80), nullable=True)


# ── Quality Protocols ─────────────────────────────────────────────────────────────

class QualityProtocol(Base):
    """
    Qualitätsprotokoll für Laborwerte mit Versionierung.
    
    Verwaltet Laborwerte für Ernte-Annahmen mit Import-Funktionalität und Audit-Trail.
    """
    __tablename__ = "quality_protocols"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    harvest_acceptance_id = Column(String, ForeignKey("domain_inventory.harvest_acceptances.id", ondelete="SET NULL"), nullable=True)
    protocol_number = Column(String(50), nullable=False)
    version = Column(Integer, nullable=False, server_default="1")
    
    # Laborwerte
    moisture_pct = Column(DECIMAL(5, 2), nullable=True, comment="Feuchte (%)")
    impurities_pct = Column(DECIMAL(5, 2), nullable=True, comment="Besatz (%)")
    hl_weight_kg_per_hl = Column(DECIMAL(6, 2), nullable=True, comment="Hektolitergewicht (kg/hl)")
    protein_pct = Column(DECIMAL(5, 2), nullable=True, comment="Protein (%)")
    mycotoxin_ppb = Column(DECIMAL(10, 2), nullable=True, comment="Mykotoxin (ppb)")
    other_values = Column(JSONB(astext_type=Text()), nullable=True, comment="Weitere Laborwerte (JSONB)")
    
    # Quelle
    source_type = Column(String(20), nullable=True, comment="Quelle: manual / import / lims / device")
    source_device_id = Column(String(64), nullable=True)
    source_file_name = Column(String(255), nullable=True)
    source_file_content = Column(Text(), nullable=True, comment="Original-Dateiinhalt (für Audit)")
    
    # Status
    is_final = Column(Boolean, nullable=False, server_default="false")
    approved_by = Column(String(64), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(64), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String(64), nullable=True)


# ── Daily Prices ──────────────────────────────────────────────────────────────────

class DailyPrice(Base):
    """
    Tagespreise für dynamische Preisermittlung.
    
    Verwaltet Tagespreise für Artikel, Warengruppen oder Crop Codes mit Gültigkeitszeitraum.
    """
    __tablename__ = "daily_prices"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id", ondelete="SET NULL"), nullable=True)
    warengruppe = Column(String(80), nullable=True, comment="Warengruppe (falls artikel_id NULL)")
    crop_code = Column(String(20), nullable=True, comment="Crop Code (MAIZE, WHEAT, BARLEY, etc.)")
    
    # Preis
    price_eur_per_ton = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, server_default="EUR")
    
    # Gültigkeit
    price_date = Column(Date, nullable=False)
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_to = Column(DateTime(timezone=True), nullable=True)
    
    # Quelle
    source_type = Column(String(20), nullable=True, comment="Quelle: manual / exchange / api")
    source_id = Column(String(64), nullable=True)
    source_name = Column(String(255), nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(64), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String(64), nullable=True)


# ── Self-Billing Invoices ─────────────────────────────────────────────────────────

class SelfBillingInvoice(Base):
    """
    Self-Billing Gutschrift für Ernte-Annahmen.
    
    Verwaltet Self-Billing Gutschriften mit E-Rechnung-Erstellung und Dispute-Handling.
    """
    __tablename__ = "self_billing_invoices"
    __table_args__ = {"schema": "domain_finance", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    harvest_acceptance_id = Column(String, ForeignKey("domain_inventory.harvest_acceptances.id", ondelete="SET NULL"), nullable=True)
    
    # Rechnungsnummern
    invoice_number = Column(String(50), nullable=False)
    provisional_invoice_number = Column(String(50), nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, server_default="draft", comment="draft / issued / paid / disputed / cancelled")
    dispute_status = Column(String(20), nullable=True, comment="none / raised / resolved / rejected")
    dispute_reason = Column(Text(), nullable=True)
    dispute_date = Column(DateTime(timezone=True), nullable=True)
    dispute_user_id = Column(String(64), nullable=True)
    
    # Beträge
    total_net_amount_eur = Column(DECIMAL(15, 2), nullable=False)
    total_vat_amount_eur = Column(DECIMAL(15, 2), nullable=False)
    total_gross_amount_eur = Column(DECIMAL(15, 2), nullable=False)
    vat_rate_percent = Column(DECIMAL(5, 2), nullable=False)
    
    # E-Rechnung
    einvoice_xml = Column(Text(), nullable=True, comment="XRechnung/ZUGFeRD XML")
    einvoice_pdf = Column(postgresql.BYTEA(), nullable=True, comment="PDF (optional)")
    einvoice_sent_at = Column(DateTime(timezone=True), nullable=True)
    einvoice_received_at = Column(DateTime(timezone=True), nullable=True)
    
    # Pflichttexte
    mandatory_texts = Column(JSONB(astext_type=Text()), nullable=True, comment="Array von Pflichttexten (JSONB)")
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(64), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String(64), nullable=True)


# ── Dispute Records ──────────────────────────────────────────────────────────────

class DisputeRecord(Base):
    """
    Dispute-Records für Self-Billing Gutschriften.
    
    Verwaltet Widersprüche gegen Gutschriften mit Status-Tracking und Auflösung.
    """
    __tablename__ = "dispute_records"
    __table_args__ = {"schema": "domain_finance", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    invoice_id = Column(String, ForeignKey("domain_finance.self_billing_invoices.id", ondelete="CASCADE"), nullable=False)
    
    # Dispute-Details
    dispute_type = Column(String(30), nullable=True, comment="amount / quality / quantity / other")
    dispute_reason = Column(Text(), nullable=False)
    disputed_amount_eur = Column(DECIMAL(15, 2), nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, server_default="raised", comment="raised / resolved / rejected")
    resolution_notes = Column(Text(), nullable=True)
    resolved_by = Column(String(64), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(64), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String(64), nullable=True)
    debtor_from = Column(String(80), nullable=True)
    debtor_to = Column(String(80), nullable=True)
    delivery_option = Column(String(40), nullable=False, default="vollstaendige_ablieferung")
    form_code = Column(String(40), nullable=False, default="W12151")
    copies = Column(Integer, nullable=False, default=1)
    printer_name = Column(String(255), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NawaroContractSheet(Base):
    """NaWaRo contracts sheet header."""
    __tablename__ = "nawaro_contract_sheets"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    harvest_year = Column(Integer, nullable=False)
    article_number = Column(String(80), nullable=True)
    is_summer = Column(Boolean, nullable=False, default=True)
    is_winter = Column(Boolean, nullable=False, default=False)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NawaroContractSheetRow(Base):
    """NaWaRo contracts sheet row."""
    __tablename__ = "nawaro_contract_sheet_rows"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    sheet_id = Column(String, ForeignKey("domain_inventory.nawaro_contract_sheets.id", ondelete="CASCADE"), nullable=False)
    contract_number = Column(String(80), nullable=True)
    customer_name = Column(String(255), nullable=True)
    name_1 = Column(String(255), nullable=True)
    total_area = Column(DECIMAL(12, 3), nullable=True)
    standard_quantity = Column(DECIMAL(12, 3), nullable=True)
    delivery_count = Column(Integer, nullable=True)
    delivery_resource = Column(String(120), nullable=True)
    quantity_b = Column(DECIMAL(12, 3), nullable=True)
    harvest_declaration = Column(String(255), nullable=True)
    row_order = Column(Integer, nullable=False, default=0)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NawaroAreaSheet(Base):
    """NaWaRo cultivation area sheet header."""
    __tablename__ = "nawaro_area_sheets"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    harvest_year_from = Column(Integer, nullable=False)
    harvest_year_to = Column(Integer, nullable=False)
    article_number = Column(String(80), nullable=True)
    is_summer = Column(Boolean, nullable=False, default=True)
    is_winter = Column(Boolean, nullable=False, default=False)
    form_code = Column(String(40), nullable=False, default="W12071")
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NawaroAreaSheetRow(Base):
    """NaWaRo cultivation area sheet row."""
    __tablename__ = "nawaro_area_sheet_rows"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    sheet_id = Column(String, ForeignKey("domain_inventory.nawaro_area_sheets.id", ondelete="CASCADE"), nullable=False)
    customer_name = Column(String(255), nullable=True)
    name_1 = Column(String(255), nullable=True)
    name_2 = Column(String(255), nullable=True)
    postal_code = Column(String(20), nullable=True)
    city = Column(String(120), nullable=True)
    phone = Column(String(80), nullable=True)
    fax = Column(String(80), nullable=True)
    area_2022 = Column(DECIMAL(12, 3), nullable=True)
    area_2023 = Column(DECIMAL(12, 3), nullable=True)
    area_2024 = Column(DECIMAL(12, 3), nullable=True)
    area_2025 = Column(DECIMAL(12, 3), nullable=True)
    area_2026 = Column(DECIMAL(12, 3), nullable=True)
    row_order = Column(Integer, nullable=False, default=0)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NawaroRapsProfile(Base):
    """Raps NaWaRo profile for usage split, sustainability metrics, and bookkeeping basis."""
    __tablename__ = "nawaro_raps_profiles"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=True)
    article_number = Column(String(80), nullable=True)
    article_name = Column(String(255), nullable=False, default="Raps")
    harvest_year = Column(Integer, nullable=False)
    usage_food_pct = Column(DECIMAL(5, 2), nullable=False, default=0)
    usage_feed_pct = Column(DECIMAL(5, 2), nullable=False, default=0)
    usage_energy_pct = Column(DECIMAL(5, 2), nullable=False, default=0)
    usage_material_pct = Column(DECIMAL(5, 2), nullable=False, default=0)
    thg_gco2eq_mj = Column(DECIMAL(10, 3), nullable=True)
    yield_dt_per_ha = Column(DECIMAL(10, 3), nullable=True)
    notes = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NawaroRapsCertificate(Base):
    """Sustainability certificate chain entries for a Raps NaWaRo profile."""
    __tablename__ = "nawaro_raps_certificates"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    profile_id = Column(String, ForeignKey("domain_inventory.nawaro_raps_profiles.id", ondelete="CASCADE"), nullable=False)
    scheme = Column(String(80), nullable=False)  # REDcert, ISCC, etc.
    certificate_number = Column(String(120), nullable=False)
    chain_stage = Column(String(80), nullable=True)  # farm, trade, mill
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)
    issuer = Column(String(120), nullable=True)
    status = Column(String(40), nullable=False, default="valid")
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NawaroRapsBalance(Base):
    """Input/output and cost allocation for Raps processing coproducts."""
    __tablename__ = "nawaro_raps_balances"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    profile_id = Column(String, ForeignKey("domain_inventory.nawaro_raps_profiles.id", ondelete="CASCADE"), nullable=False)
    booking_period = Column(String(20), nullable=True)  # YYYY-MM
    input_seed_tons = Column(DECIMAL(12, 3), nullable=False, default=0)
    output_oil_tons = Column(DECIMAL(12, 3), nullable=False, default=0)
    output_meal_tons = Column(DECIMAL(12, 3), nullable=False, default=0)
    output_other_tons = Column(DECIMAL(12, 3), nullable=False, default=0)
    allocation_oil_pct = Column(DECIMAL(5, 2), nullable=True)
    allocation_meal_pct = Column(DECIMAL(5, 2), nullable=True)
    heap_location = Column(String(255), nullable=True)  # Erntegutmiete / logistic place
    logistics_note = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Silo(Base):
    """Silo master data."""
    __tablename__ = "silos"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    silo_number = Column(String(50), nullable=False)
    name = Column(String(120), nullable=True)
    article_id = Column(String(64), nullable=True)
    capacity_tons = Column(DECIMAL(12, 3), nullable=False)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SiloLot(Base):
    """Virtual lot entries inside silos."""
    __tablename__ = "silo_lots"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    silo_id = Column(String, ForeignKey("domain_inventory.silos.id"), nullable=False)
    virtual_lot_number = Column(String(64), nullable=False)
    source_ticket_id = Column(String, ForeignKey("domain_inventory.weighing_tickets.id"), nullable=True)
    source_partner_id = Column(String(64), nullable=True)
    article_id = Column(String(64), nullable=True)
    quantity_tons = Column(DECIMAL(12, 3), nullable=False)
    moisture_pct = Column(DECIMAL(5, 2), nullable=True)
    protein_pct = Column(DECIMAL(5, 2), nullable=True)
    impurities_pct = Column(DECIMAL(5, 2), nullable=True)
    hl_weight = Column(DECIMAL(6, 2), nullable=True)
    status = Column(String(20), nullable=False, default="active")
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SiloLotMovement(Base):
    """Movement history for virtual lots."""
    __tablename__ = "silo_lot_movements"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    silo_lot_id = Column(String, ForeignKey("domain_inventory.silo_lots.id"), nullable=False)
    movement_type = Column(String(20), nullable=False)  # in, out, treatment
    quantity_tons = Column(DECIMAL(12, 3), nullable=False)
    note = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SiloQualitySnapshot(Base):
    """Weighted quality snapshot per silo."""
    __tablename__ = "silo_quality_snapshots"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    silo_id = Column(String, ForeignKey("domain_inventory.silos.id"), nullable=False)
    total_quantity_tons = Column(DECIMAL(12, 3), nullable=False, default=0)
    moisture_avg_pct = Column(DECIMAL(5, 2), nullable=True)
    protein_avg_pct = Column(DECIMAL(5, 2), nullable=True)
    impurities_avg_pct = Column(DECIMAL(5, 2), nullable=True)
    hl_weight_avg = Column(DECIMAL(6, 2), nullable=True)
    lot_count = Column(Integer, nullable=False, default=0)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Warehouse Transfers ──────────────────────────────────────────

class WarehouseTransfer(Base):
    """Lager-zu-Lager Buchung header."""
    __tablename__ = "warehouse_transfers"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    transfer_number = Column(String(50), nullable=False)
    from_warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=False)
    to_warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=False)
    status = Column(String(20), default="draft")
    notes = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WarehouseTransferLine(Base):
    """Lager-zu-Lager Buchung position."""
    __tablename__ = "warehouse_transfer_lines"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    transfer_id = Column(String, ForeignKey("domain_inventory.warehouse_transfers.id"), nullable=False)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    quantity = Column(DECIMAL(12, 3), nullable=False)
    batch_number = Column(String(50), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Stock Corrections ────────────────────────────────────────────

class StockCorrection(Base):
    """Bestandskorrektur header."""
    __tablename__ = "stock_corrections"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    correction_number = Column(String(50), nullable=False)
    warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=False)
    reason = Column(String(100), nullable=True)
    status = Column(String(20), default="draft")
    notes = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StockCorrectionLine(Base):
    """Bestandskorrektur position."""
    __tablename__ = "stock_correction_lines"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    correction_id = Column(String, ForeignKey("domain_inventory.stock_corrections.id"), nullable=False)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    old_quantity = Column(DECIMAL(12, 3), nullable=False)
    new_quantity = Column(DECIMAL(12, 3), nullable=False)
    difference = Column(DECIMAL(12, 3), nullable=False)
    batch_number = Column(String(50), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Bin Locations ────────────────────────────────────────────────

class BinLocation(Base):
    """Lagerfach."""
    __tablename__ = "bin_locations"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    code = Column(String(50), nullable=False)
    warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=False)
    zone = Column(String(20), nullable=True)
    rack = Column(String(20), nullable=True)
    shelf = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Preparation Lists ───────────────────────────────────────────

class PreparationList(Base):
    """Rüstliste header."""
    __tablename__ = "preparation_lists"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    list_number = Column(String(50), nullable=False)
    status = Column(String(20), default="open")
    notes = Column(Text, nullable=True)
    warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PreparationListLine(Base):
    """Rüstliste position."""
    __tablename__ = "preparation_list_lines"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    list_id = Column(String, ForeignKey("domain_inventory.preparation_lists.id"), nullable=False)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    required_qty = Column(DECIMAL(12, 3), nullable=False)
    picked_qty = Column(DECIMAL(12, 3), default=0)
    bin_location_id = Column(String, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Pick Lists ───────────────────────────────────────────────────

class PickList(Base):
    """Pickliste header."""
    __tablename__ = "pick_lists"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    pick_list_number = Column(Integer, nullable=False)
    status = Column(String(20), default="open")
    tour_id = Column(String, nullable=True)
    order_id = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PickListLine(Base):
    """Pickliste position."""
    __tablename__ = "pick_list_lines"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    pick_list_id = Column(String, ForeignKey("domain_inventory.pick_lists.id"), nullable=False)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    required_qty = Column(DECIMAL(12, 3), nullable=False)
    picked_qty = Column(DECIMAL(12, 3), default=0)
    bin_location_id = Column(String, nullable=True)
    batch_number = Column(String(50), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Shipping Units (NVE/SSCC) ────────────────────────────────────

class ShippingUnit(Base):
    """NVE / SSCC Versandeinheit."""
    __tablename__ = "shipping_units"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    sscc = Column(String(18), nullable=False, unique=True)
    status = Column(String(20), default="created")
    order_id = Column(String, nullable=True)
    delivery_note_id = Column(String, nullable=True)
    weight = Column(DECIMAL(12, 3), nullable=True)
    contents = Column(JSONB, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ── Webhook Registrations ────────────────────────────────────────

class WebhookRegistration(Base):
    """Webhook-Registrierung."""
    __tablename__ = "webhook_registrations"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    url = Column(String(500), nullable=False)
    event_area = Column(String(50), nullable=False)
    secret = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ── Article Batches ──────────────────────────────────────────────

class ArticleBatch(Base):
    """Chargen-Bestand für Artikel."""
    __tablename__ = "article_batches"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    batch_number = Column(String(50), nullable=False)
    warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=False)
    quantity = Column(DECIMAL(12, 3), default=0)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Internal Messages ────────────────────────────────────────────

class InternalMessage(Base):
    """Interne Nachricht."""
    __tablename__ = "internal_messages"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    sender_id = Column(String, ForeignKey("domain_shared.users.id"), nullable=False)
    recipient_id = Column(String, ForeignKey("domain_shared.users.id"), nullable=False)
    subject = Column(String(200), nullable=False)
    body = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Master Data Entries ──────────────────────────────────────────

class MasterDataEntry(Base):
    """Generic lookup / master-data table."""
    __tablename__ = "master_data_entries"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    category = Column(String(50), nullable=False)  # e.g. 'branch', 'country', 'shipping_method'
    code = Column(String(50), nullable=False)
    label = Column(String(200), nullable=False)
    extra = Column(JSONB, nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ── System Properties (Subledger / Jahresabschluss) ───────────────

class SystemProperty(Base):
    """
    Systemeigenschaften für Subledger-Workflow, Konten-Mapping, Stichtags-Umgliederung.
    Tenant-spezifische Overrides für SKR-Konten und Feature-Flags.
    """
    __tablename__ = "system_properties"
    __table_args__ = (
        UniqueConstraint("tenant_id", "property_key", name="uq_system_properties_tenant_key"),
        {"schema": "domain_shared", "extend_existing": True},
    )

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    property_key = Column(String(100), nullable=False, comment="z.B. SUBLEDGER_AR_ACCOUNT")
    property_value = Column(Text, nullable=True)
    property_type = Column(String(20), default="string", comment="string / number / boolean / json")
    category = Column(String(50), default="subledger", comment="subledger / year_end / harvest")
    description = Column(Text, nullable=True)


# ── Dispatchers ──────────────────────────────────────────────────

class Dispatcher(Base):
    """Disponent."""
    __tablename__ = "dispatchers"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(30), nullable=True)
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ── Article Selections ───────────────────────────────────────────

class ArticleSelection(Base):
    """Artikel-Selektion (Zuordnung)."""
    __tablename__ = "article_selections"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    selection_code = Column(String(50), nullable=False)
    label = Column(String(200), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

