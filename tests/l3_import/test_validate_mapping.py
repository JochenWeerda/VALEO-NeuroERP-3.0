import pytest

from scripts.validate_mapping import validate_entries


def collect_levels(findings, level):
    return [f for f in findings if f.level == level]


def message_contains(findings, snippet):
    return any(snippet in str(finding) for finding in findings)


@pytest.fixture
def sample_raw_metadata():
    return {
        "RAW_FINANCE": ["CURRENCY_CODE", "FX_RATE", "FX_RATE_TS", "AMOUNT_BASE", "AMOUNT_TXN"],
        "RAW_CRM": ["CANCEL_REASON_ID", "STAGE", "STATUS", "EMAIL"],
        "RAW_INVENTORY": ["UOM_BASE", "LOT_ID", "QUANTITY"],
        "RAW_HR": ["PERSON_ID", "EMPLOYMENT_START", "EMPLOYMENT_END"],
        "RAW_MFG": ["BOM_ID", "ROUTING_ID", "EVENT_TS"],
    }


@pytest.fixture
def valid_mapping(sample_raw_metadata):
    return {
        "RAW_FINANCE": {
            "CURRENCY_CODE": {
                "target": "domain_finance.currency.currency_code",
                "type": "text",
                "nullable": False,
                "notes": "ISO currency codes",
            },
            "FX_RATE": {
                "target": "domain_finance.fx_rates.fx_rate",
                "type": "numeric",
                "nullable": False,
                "notes": "Exchange rate",
            },
            "FX_RATE_TS": {
                "target": "domain_finance.fx_rates.fx_rate_ts",
                "type": "datetime",
                "nullable": False,
                "notes": "Timestamp for FX rate",
            },
            "AMOUNT_BASE": {
                "target": "domain_finance.transactions.amount_base",
                "type": "decimal",
                "nullable": False,
                "notes": "Base currency amount",
            },
            "AMOUNT_TXN": {
                "target": "domain_finance.transactions.amount_txn",
                "type": "decimal",
                "nullable": False,
                "notes": "Transaction currency amount",
            },
        },
        "RAW_CRM": {
            "CANCEL_REASON_ID": {
                "target": "domain_crm.cancellation_reason.cancel_reason_id",
                "type": "integer",
                "nullable": True,
                "notes": "Foreign key to cancel reasons",
            },
            "STAGE": {
                "target": "domain_crm.opportunity.stage",
                "type": "text",
                "nullable": False,
                "transform": "map_enum",
                "notes": "Opportunity stage enum",
            },
            "STATUS": {
                "target": "domain_crm.opportunity.status",
                "type": "text",
                "nullable": False,
                "transform": "map_enum",
                "notes": "Opportunity status enum",
            },
            "EMAIL": {
                "target": "domain_crm.contact.email",
                "type": "text",
                "nullable": True,
                "notes": "Contact email",
            },
        },
        "RAW_INVENTORY": {
            "UOM_BASE": {
                "target": "domain_inventory.article.uom_base",
                "type": "text",
                "nullable": False,
                "notes": "Base unit of measure",
            },
            "LOT_ID": {
                "target": "domain_inventory.lot.lot_id",
                "type": "text",
                "nullable": False,
                "notes": "Lot identifier for traceability",
            },
            "QUANTITY": {
                "target": "domain_inventory.stock_movement.quantity",
                "type": "decimal",
                "nullable": False,
                "notes": "Movement quantity",
            },
        },
        "RAW_HR": {
            "PERSON_ID": {
                "target": "domain_hr.person.person_id",
                "type": "uuid",
                "nullable": False,
                "notes": "Person identifier",
            },
            "EMPLOYMENT_START": {
                "target": "domain_hr.employment.employment_start",
                "type": "date",
                "nullable": False,
                "notes": "Employment start date",
            },
            "EMPLOYMENT_END": {
                "target": "domain_hr.employment.employment_end",
                "type": "date",
                "nullable": True,
                "notes": "Employment end date",
            },
        },
        "RAW_MFG": {
            "BOM_ID": {
                "target": "domain_mfg.bom.bom_id",
                "type": "integer",
                "nullable": False,
                "notes": "Bill of materials ID",
            },
            "ROUTING_ID": {
                "target": "domain_mfg.routing.routing_id",
                "type": "integer",
                "nullable": False,
                "notes": "Routing identifier",
            },
            "EVENT_TS": {
                "target": "domain_mfg.production_event.event_ts",
                "type": "datetime",
                "nullable": False,
                "notes": "Production event timestamp",
            },
        },
    }


def test_finance_fx_rate_requires_nullable_flag(sample_raw_metadata):
    mapping = {
        "RAW_FINANCE": {
            "FX_RATE": {
                "target": "domain_finance.fx_rates.fx_rate",
                "type": "numeric",
            }
        }
    }
    raw = sample_raw_metadata

    findings, _ = validate_entries(mapping, raw)
    assert message_contains(
        collect_levels(findings, "ERROR"),
        "Nullable flag required for this domain column but missing.",
    )

    mapping["RAW_FINANCE"]["FX_RATE"]["nullable"] = False
    findings, _ = validate_entries(mapping, raw)
    assert not collect_levels(findings, "ERROR")


def test_crm_stage_requires_enum_transform(sample_raw_metadata):
    mapping = {
        "RAW_CRM": {
            "STAGE": {
                "target": "domain_crm.opportunity.stage",
                "type": "text",
                "nullable": False,
            }
        }
    }
    raw = sample_raw_metadata

    findings, _ = validate_entries(mapping, raw)
    assert message_contains(
        collect_levels(findings, "ERROR"),
        "Transform required for this domain column but missing",
    )

    mapping["RAW_CRM"]["STAGE"]["transform"] = "map_enum"
    findings, _ = validate_entries(mapping, raw)
    assert not collect_levels(findings, "ERROR")


def test_inventory_lot_requires_notes_and_nullable_flag(sample_raw_metadata):
    mapping = {
        "RAW_INVENTORY": {
            "LOT_ID": {
                "target": "domain_inventory.lot.lot_id",
                "type": "text",
                "nullable": False,
            }
        }
    }
    raw = sample_raw_metadata

    findings, _ = validate_entries(mapping, raw)
    assert message_contains(
        collect_levels(findings, "WARN"),
        "Notes required for this domain column but missing.",
    )

    mapping["RAW_INVENTORY"]["LOT_ID"]["notes"] = "Traceability requirement"
    findings, _ = validate_entries(mapping, raw)
    assert not message_contains(
        collect_levels(findings, "WARN"),
        "Notes required for this domain column but missing.",
    )


def test_finance_currency_code_wrong_type(sample_raw_metadata):
    mapping = {
        "RAW_FINANCE": {
            "CURRENCY_CODE": {
                "target": "domain_finance.currency.currency_code",
                "type": "integer",  # Wrong type
                "nullable": False,
                "notes": "Test",
            }
        }
    }
    raw = sample_raw_metadata

    findings, _ = validate_entries(mapping, raw)
    assert message_contains(
        collect_levels(findings, "WARN"),
        "Type 'integer' does not match expected",
    )


def test_hr_person_id_requires_uuid_type(sample_raw_metadata):
    mapping = {
        "RAW_HR": {
            "PERSON_ID": {
                "target": "domain_hr.person.person_id",
                "type": "text",  # Wrong type
                "nullable": False,
                "notes": "Test",
            }
        }
    }
    raw = sample_raw_metadata

    findings, _ = validate_entries(mapping, raw)
    assert message_contains(
        collect_levels(findings, "WARN"),
        "Type 'text' does not match expected",
    )


def test_mfg_event_ts_nullable_expectation(sample_raw_metadata):
    mapping = {
        "RAW_MFG": {
            "EVENT_TS": {
                "target": "domain_mfg.production_event.event_ts",
                "type": "datetime",
                "nullable": True,  # Should be False
                "notes": "Test",
            }
        }
    }
    raw = sample_raw_metadata

    findings, _ = validate_entries(mapping, raw)
    assert message_contains(
        collect_levels(findings, "WARN"),
        "Expected nullable=False but found True",
    )


def test_crm_email_optional_type(sample_raw_metadata):
    mapping = {
        "RAW_CRM": {
            "EMAIL": {
                "target": "domain_crm.contact.email",
                "nullable": True,
                "notes": "Test",
                # No type specified, should be ok since require_type=False
            }
        }
    }
    raw = sample_raw_metadata

    findings, _ = validate_entries(mapping, raw)
    # Should not have error for missing type since require_type=False
    assert not message_contains(
        collect_levels(findings, "ERROR"),
        "Type is required for this domain column but missing",
    )


def test_valid_mapping_no_errors(valid_mapping, sample_raw_metadata):
    findings, _ = validate_entries(valid_mapping, sample_raw_metadata)
    errors = collect_levels(findings, "ERROR")
    assert len(errors) == 0, f"Unexpected errors: {[str(e) for e in errors]}"


def test_duplicate_targets_error(sample_raw_metadata):
    mapping = {
        "RAW_FINANCE": {
            "CURRENCY_CODE": {
                "target": "domain_finance.currency.currency_code",
                "type": "text",
                "nullable": False,
                "notes": "Test",
            }
        },
        "RAW_CRM": {
            "EMAIL": {
                "target": "domain_finance.currency.currency_code",  # Duplicate
                "type": "text",
                "nullable": True,
                "notes": "Test",
            }
        }
    }
    raw = sample_raw_metadata

    findings, _ = validate_entries(mapping, raw)
    assert message_contains(
        collect_levels(findings, "ERROR"),
        "Target referenced multiple times",
    )


def test_missing_target_error(sample_raw_metadata):
    mapping = {
        "RAW_FINANCE": {
            "CURRENCY_CODE": {
                "type": "text",
                "nullable": False,
                "notes": "Test",
                # Missing target
            }
        }
    }
    raw = sample_raw_metadata

    findings, _ = validate_entries(mapping, raw)
    assert message_contains(
        collect_levels(findings, "ERROR"),
        "Missing required 'target' attribute",
    )


def test_invalid_target_format(sample_raw_metadata):
    mapping = {
        "RAW_FINANCE": {
            "CURRENCY_CODE": {
                "target": "domain_finance.currency_code",  # Missing third part
                "type": "text",
                "nullable": False,
                "notes": "Test",
            }
        }
    }
    raw = sample_raw_metadata

    findings, _ = validate_entries(mapping, raw)
    assert message_contains(
        collect_levels(findings, "ERROR"),
        "Target must follow 'schema.table.column'",
    )
