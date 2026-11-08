"""Privacy access controls: real signed identities and rollback-isolated probe SQL.

No placeholder encryption/retention certification and no 5xx-as-success checks.
Reuse the canonical contracts so standalone compliance and full CI cannot drift.
"""
from test_gdpr_subject_boundary import (  # noqa: F401
    keys, probe, subject_data,
    test_self_export_uses_provider_mapping_and_only_own_tenant_audit,
    test_other_local_subject_is_denied_and_admin_is_still_tenant_bound,
    test_anonymization_requires_admin_and_never_rewrites_retained_audit,
    test_forged_tenant_or_user_headers_and_missing_identity_cannot_authorize,
)
