from app.core.mask_classification import (
    GeneratorAdapterType,
    MobileRenderMode,
    build_mask_registry,
)


def test_mask_registry_exposes_generator_metadata_for_crm_pilot() -> None:
    registry = build_mask_registry()
    crm_pilot = registry.get("crm/customer-360")

    assert crm_pilot is not None
    assert crm_pilot.generator_ready is True
    assert crm_pilot.adapter_type == GeneratorAdapterType.CRM_MASK_JSON
    assert crm_pilot.mobile_mode == MobileRenderMode.MOBILE_STACK
    assert crm_pilot.requires_lazy_tabs is True
    assert crm_pilot.requires_virtual_tables is True
    assert crm_pilot.summary_endpoint == "/api/v1/crm/customers/{customer_id}/screen-summary"


def test_mask_registry_keeps_defaults_for_non_generator_masks() -> None:
    registry = build_mask_registry()
    mask = registry.get("finance/ap-invoice-form")

    assert mask is not None
    assert mask.generator_ready is False
    assert mask.initial_payload_budget_kb == 64
    assert mask.summary_endpoint is None
