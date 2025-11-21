import { Pool, PoolClient, QueryResult, QueryResultRow } from 'pg'

type QueryParams = Array<string | number | boolean | Date | object | null>

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: Number(process.env.GAP_DB_POOL_SIZE ?? 10),
})

export const db = {
  query<T extends QueryResultRow = any>(text: string, params?: QueryParams): Promise<QueryResult<T>> {
    return pool.query<T>(text, params)
  },
  async withClient<T>(fn: (client: PoolClient) => Promise<T>): Promise<T> {
    const client = await pool.connect()
    try {
      return await fn(client)
    } finally {
      client.release()
    }
  },
  async end(): Promise<void> {
    await pool.end()
  },
}

export type Db = typeof db
