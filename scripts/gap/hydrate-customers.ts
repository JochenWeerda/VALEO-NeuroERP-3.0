import { readFileSync } from 'fs'
import { resolve } from 'path'
import { db } from './db'
import { assertYear } from './utils'

interface HydrateOptions {
  year: number
}

const HYDRATE_SQL_PATH = resolve(__dirname, '../../database/analytics-hydrate-customers.sql')
const HYDRATE_SQL_TEMPLATE = readFileSync(HYDRATE_SQL_PATH, 'utf8')

export async function runHydrateCustomers(opts: HydrateOptions): Promise<void> {
  const year = Number(opts.year)
  assertYear(year)
  console.log(`Hydrating customer analytics fields from snapshot for year ${year}...`)

  const sql = HYDRATE_SQL_TEMPLATE.replace(/:year/g, '$1')
  const result = await db.query(
    sql,
    [year],
  )

  console.log(`Hydration complete for year ${year}. Rows updated: ${result.rowCount}`)
}
