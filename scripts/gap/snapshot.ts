import { db } from './db'
import { assertYear } from './utils'

interface SnapshotOptions {
  year: number
  eurPerHa?: number
}

export async function runSnapshot(opts: SnapshotOptions): Promise<void> {
  const year = Number(opts.year)
  assertYear(year)
  const eurPerHa = opts.eurPerHa ?? Number(process.env.GAP_EUR_PER_HA ?? 270)

  console.log(`Computing customer potential snapshot for year ${year} (EUR/ha=${eurPerHa})...`)

  const matches = await db.query<{
    customer_id: string
    gap_direct_total_eur: string | null
    turnover_total_last_year_eur: string | null
  }>(
    `
    SELECT
      m.customer_id,
      m.gap_direct_total_eur::text,
      c.analytics_turnover_total_last_year_eur::text
    FROM gap_customer_match m
    JOIN customers c ON c.id = m.customer_id
    WHERE
      m.ref_year = $1
      AND m.is_confident = TRUE
      AND m.status IN ('auto-match','manual-accepted')
    `,
    [year],
  )

  await db.query('DELETE FROM customer_potential_snapshot WHERE ref_year = $1', [year])

  for (const row of matches.rows) {
    const gapDirect = Number(row.gap_direct_total_eur ?? 0)
    const estimatedAreaHa = gapDirect > 0 ? gapDirect / eurPerHa : 0

    const potentialSeed = estimatedAreaHa * 50
    const potentialFertilizer = estimatedAreaHa * 150
    const potentialPsm = estimatedAreaHa * 80
    const potentialTotal = potentialSeed + potentialFertilizer + potentialPsm

    const turnoverLastYear = Number(row.turnover_total_last_year_eur ?? 0)
    const sow = potentialTotal > 0 ? (turnoverLastYear / potentialTotal) * 100 : null
    const segment =
      sow == null ? null : sow >= 80 ? 'A' : sow >= 40 ? 'B' : sow >= 0 ? 'C' : null

    await db.query(
      `
      INSERT INTO customer_potential_snapshot (
        ref_year,
        customer_id,
        gap_direct_total_eur,
        gap_estimated_area_ha,
        potential_seed_eur,
        potential_fertilizer_eur,
        potential_psm_eur,
        potential_total_eur,
        turnover_total_last_year_eur,
        share_of_wallet_total_pct,
        segment,
        potential_notes
      )
      VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
      `,
      [
        year,
        row.customer_id,
        gapDirect,
        estimatedAreaHa,
        potentialSeed,
        potentialFertilizer,
        potentialPsm,
        potentialTotal,
        turnoverLastYear,
        sow,
        segment,
        null,
      ],
    )
  }

  console.log(`Snapshot stored for year ${year}: processed ${matches.rows.length} customers.`)
}
