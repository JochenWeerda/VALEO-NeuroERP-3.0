"""Canonical signed, tenant-bound reprint contracts; no dev-token/system fallback."""
from test_audit_identity_integrity import (  # noqa: F401
    keys, probe, subject_data, attestation_case,
    test_attestation_keeps_provider_identity_and_local_fk,
    test_missing_or_foreign_mapping_cannot_become_system,
    test_ambiguous_provider_mapping_is_denied,
    test_sql_failure_is_not_converted_to_fallback_or_partial_print,
    test_reason_and_verified_identity_are_required,
)
