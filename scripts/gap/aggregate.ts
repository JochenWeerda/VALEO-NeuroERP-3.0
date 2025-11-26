import { db } from './db'
import { assertYear } from './utils'

interface AggregateOptions {
  year: number
}

export async function runAggregate(opts: AggregateOptions): Promise<void> {
  const year = Number(opts.year)
  assertYear(year)
  console.log(`Aggregating GAP direct payments for year ${year} (via gap_payments_direct_agg view)...`)

  const { rows } = await db.query<{ cnt: string; sum: string | null }>(
    `
    SELECT
      COUNT(*)::text AS cnt,
      COALESCE(SUM(direct_total_eur), 0)::text AS sum
    FROM gap_payments_direct_agg
    WHERE ref_year = $1
    `,
    [year],
  )

  const count = Number(rows[0]?.cnt ?? 0)
  const total = Number(rows[0]?.sum ?? 0)
  console.log(`Year ${year}: ${count} aggregated beneficiaries, total direct EUR ${total.toFixed(2)}`)
}
