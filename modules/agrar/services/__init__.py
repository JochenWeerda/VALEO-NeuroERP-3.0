"""
Agrar Services Module.

Services für Ernte-Annahme, Berechnungen, Qualitätsprotokolle, Tagespreise und Self-Billing.
"""

from modules.agrar.services.drying_rule_engine import (
    compute_settlement,
    ComputeSettlementInput,
    ComputeSettlementResult,
    DryingRuleRepository,
)
from modules.agrar.services.harvest_calculator import (
    calculate_harvest_settlement,
    HarvestCalculationInput,
    HarvestCalculationResult,
    HarvestPositionResult,
)
from modules.agrar.services.quality_protocol_service import (
    create_quality_protocol,
    update_quality_protocol,
    finalize_quality_protocol,
    import_from_csv,
    import_from_json,
    get_latest_protocol,
    QualityProtocol,
    QualityProtocolCreate,
    QualityProtocolUpdate,
    QualityProtocolRepository,
)
from modules.agrar.services.daily_price_service import (
    get_price_for_date,
    create_daily_price,
    bulk_import_prices,
    get_price_history,
    DailyPrice,
    DailyPriceCreate,
    DailyPriceFilter,
    DailyPriceRepository,
)
from modules.agrar.services.self_billing_service import (
    create_credit_note,
    issue_invoice,
    generate_einvoice,
    send_einvoice,
    create_dispute,
    resolve_dispute,
    SelfBillingInvoice,
    CreditNoteCreate,
    DisputeCreate,
    DisputeRecord,
    SelfBillingRepository,
)

__all__ = [
    # Drying Rule Engine
    "compute_settlement",
    "ComputeSettlementInput",
    "ComputeSettlementResult",
    "DryingRuleRepository",
    # Harvest Calculator
    "calculate_harvest_settlement",
    "HarvestCalculationInput",
    "HarvestCalculationResult",
    "HarvestPositionResult",
    # Quality Protocol Service
    "create_quality_protocol",
    "update_quality_protocol",
    "finalize_quality_protocol",
    "import_from_csv",
    "import_from_json",
    "get_latest_protocol",
    "QualityProtocol",
    "QualityProtocolCreate",
    "QualityProtocolUpdate",
    "QualityProtocolRepository",
    # Daily Price Service
    "get_price_for_date",
    "create_daily_price",
    "bulk_import_prices",
    "get_price_history",
    "DailyPrice",
    "DailyPriceCreate",
    "DailyPriceFilter",
    "DailyPriceRepository",
    # Self-Billing Service
    "create_credit_note",
    "issue_invoice",
    "generate_einvoice",
    "send_einvoice",
    "create_dispute",
    "resolve_dispute",
    "SelfBillingInvoice",
    "CreditNoteCreate",
    "DisputeCreate",
    "DisputeRecord",
    "SelfBillingRepository",
    # Tax Profile Service
    "get_taxation_type_for_supplier",
    # Partie Service
    "generate_lot_number",
    "create_harvest_acceptance_lines",
    # Price Adjustment Service
    "apply_price_adjustments",
    "calculate_price_adjustment",
    # NUTS-2 Service
    "derive_nuts2_from_postal_code",
    "bulk_import_nuts2_postal_codes",
    # VAT Service
    "determine_ownership_type",
    "can_create_credit_note_for_vat",
    "create_provisional_credit_note",
    "create_advance_payment_credit_note",
    "create_correction_credit_note",
]
