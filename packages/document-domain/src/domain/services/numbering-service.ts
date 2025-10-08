import { db } from '../../infra/db/connection';
import { numberSeries } from '../../infra/db/schema';
import { sql } from 'drizzle-orm';
import pino from 'pino';

const logger = pino({ name: 'numbering' });

export async function generateDocumentNumber(tenantId: string, seriesId: string): Promise<string> {
  logger.debug({ tenantId, seriesId }, 'Generating document number');

  // Race-safe: SELECT FOR UPDATE
  const result = await db.execute(sql`
    SELECT * FROM ${numberSeries} 
    WHERE id = ${seriesId} AND tenant_id = ${tenantId}
    FOR UPDATE
  `);

  const series = result[0];
  if (series === undefined || series === null) throw new Error('Number series not found');

  const nextSeq = series.next_seq as number;
  const pattern = series.pattern as string;

  // Format number
  const number = formatNumber(pattern, nextSeq);

  // Increment sequence
  await db.execute(sql`
    UPDATE ${numberSeries}
    SET next_seq = next_seq + 1
    WHERE id = ${seriesId}
  `);

  logger.info({ tenantId, seriesId, number }, 'Generated document number');
  return number;
}

function formatNumber(pattern: string, seq: number): string {
  const year = new Date().getFullYear();
  const month = String(new Date().getMonth() + 1).padStart(2, '0');

  return pattern
    .replace('{YYYY}', String(year))
    .replace('{YY}', String(year).slice(-2))
    .replace('{MM}', month)
    .replace('{seq5}', String(seq).padStart(5, '0'))
    .replace('{seq}', String(seq));
}

