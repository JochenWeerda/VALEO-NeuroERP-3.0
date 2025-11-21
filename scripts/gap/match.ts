import { db } from './db'
import { assertYear, normalizeName } from './utils'

interface MatchOptions {
  year: number
}

type GapRow = {
  beneficiary_name_norm: string
  postal_code: string | null
  city: string | null
  direct_total_eur: number | null
}

export async function runMatch(opts: MatchOptions): Promise<void> {
  const year = Number(opts.year)
  assertYear(year)
  console.log(`Running GAP-customer matching for year ${year}...`)

  const customers = await db.query<{
    id: string
    name1: string
    postal_code: string | null
    city: string | null
  }>(`
    SELECT id, name1, postal_code, city
    FROM customers
    WHERE is_active = TRUE
  `)

  const gaps = await db.query<GapRow>(
    `
    SELECT beneficiary_name_norm, postal_code, city, direct_total_eur
    FROM gap_payments_direct_agg
    WHERE ref_year = $1
    `,
    [year],
  )

  const gapIndex = new Map<string, GapRow[]>()
  for (const row of gaps.rows) {
    const key = buildKey(row.beneficiary_name_norm, row.postal_code, row.city)
    const list = gapIndex.get(key)
    if (list) {
      list.push(row)
    } else {
      gapIndex.set(key, [row])
    }
  }

  let matchCount = 0

  for (const customer of customers.rows) {
    const cNameNorm = normalizeName(customer.name1)
    if (!cNameNorm) continue
    const key = buildKey(cNameNorm, customer.postal_code, customer.city)
    const candidates = gapIndex.get(key)
    if (!candidates || candidates.length === 0) continue

    const candidate = candidates[0]
    await db.query(
      `
      INSERT INTO gap_customer_match (
        ref_year,
        customer_id,
        customer_name_norm,
        beneficiary_name_norm,
        postal_code,
        city,
        match_score,
        match_method,
        is_confident,
        status,
        gap_direct_total_eur
      )
      VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
      ON CONFLICT (ref_year, customer_id) DO UPDATE
      SET
        beneficiary_name_norm = EXCLUDED.beneficiary_name_norm,
        postal_code = EXCLUDED.postal_code,
        city = EXCLUDED.city,
        match_score = EXCLUDED.match_score,
        match_method = EXCLUDED.match_method,
        is_confident = EXCLUDED.is_confident,
        status = EXCLUDED.status,
        gap_direct_total_eur = EXCLUDED.gap_direct_total_eur,
        updated_at = NOW()
      `,
      [
        year,
        customer.id,
        cNameNorm,
        candidate.beneficiary_name_norm,
        candidate.postal_code,
        candidate.city,
        1.0,
        'exact_name_plz_city',
        true,
        'auto-match',
        candidate.direct_total_eur ?? null,
      ],
    )
    matchCount += 1
  }

  console.log(`Matching finished for year ${year}. Stored ${matchCount} matches.`)
}

function buildKey(name: string, postalCode: string | null, city: string | null): string {
  const plz = postalCode?.trim() ?? ''
  const ort = city?.trim()?.toUpperCase() ?? ''
  return `${name}|${plz}|${ort}`
}
