# CRM native runtime and local privacy processing (2026-10-31)

The campaign, consent, segment and privacy-request details use native ScreenDefinitions and the shared resource action adapter. Segment membership is tenant-bound and persisted; dynamic rules accept only explicitly supported business-partner fields and bounded operations. Unsupported legacy rules cannot be silently evaluated.

Privacy requests require the subject type and `LOCAL_CRM_SUBJECT` scope. A successful local export or anonymization is `PARTIALLY_COMPLETED`, not a claim that the entire legal request has been fulfilled. The receipt records examined sources and retained financial, audit, external CRM and unlinked sources. Human review and separate processing remain necessary for those sources. Historical requests without a type must specify it explicitly; a matching display name is not evidence of identity. Existing audit history is retained. Export only becomes downloadable after a real payload is stored, and prior matching downloads are invalidated by anonymization.

Migration `gdpr_request_process_20261031` follows `sales_offer_number_tenant_20261031`; it preserves unknown historical subject types. No persistent migration was applied during validation. Probe tests use synthetic tenant records in transactions that roll back.
