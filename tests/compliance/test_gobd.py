"""Real journal-chain contracts; no placeholder compliance certification."""
from test_journal_stamp_integrity import (  # noqa: F401
    isolate_period_contract,
    store,
    case,
    test_first_and_successor_use_actual_previous_hash,
    test_incomplete_existing_chain_rejects_without_partial_stamp,
    test_duplicate_sequence_is_rejected,
    test_broken_middle_link_is_rejected,
    test_other_tenant_does_not_supply_predecessor,
    test_concurrent_writers_wait_and_use_committed_predecessor,
    test_stamp_read_failure_prevents_create_and_reverse_writes,
    test_hash_failure_leaves_no_partial_stamp,
    test_foreign_tenant_and_replacing_existing_stamp_are_rejected,
    test_repeatable_read_is_rejected_instead_of_allocating_from_old_snapshot,
)
