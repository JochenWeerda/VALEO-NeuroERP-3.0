-- Customer analytics hydrate job
UPDATE customers AS c
SET
  analytics_gap_ref_year = s.ref_year,
  analytics_gap_direct_total_eur = s.gap_direct_total_eur,
  analytics_gap_estimated_area_ha = s.gap_estimated_area_ha,
  analytics_potential_seed_eur = s.potential_seed_eur,
  analytics_potential_fertilizer_eur = s.potential_fertilizer_eur,
  analytics_potential_psm_eur = s.potential_psm_eur,
  analytics_potential_total_eur = s.potential_total_eur,
  analytics_turnover_total_last_year_eur = s.turnover_total_last_year_eur,
  analytics_share_of_wallet_total_pct = s.share_of_wallet_total_pct,
  analytics_segment = s.segment,
  analytics_potential_notes = s.potential_notes,
  analytics_gap_last_sync_at = NOW(),
  analytics_gap_last_sync_status = 'ok'
FROM customer_potential_snapshot AS s
WHERE
  s.ref_year = :year
  AND s.customer_id = c.id
  AND COALESCE(c.analytics_block_auto_potential_update, FALSE) = FALSE;
