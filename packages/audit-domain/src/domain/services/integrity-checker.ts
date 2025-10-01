import { db } from '../../infra/db/connection';
import { auditEvents } from '../../infra/db/schema';
import { createHash } from 'crypto';
import { eq, gte, lte, and } from 'drizzle-orm';
import pino from 'pino';

const logger = pino({ name: 'integrity-checker' });

export async function verifyIntegrity(
  tenantId: string,
  from?: string,
  to?: string
): Promise<{
  valid: boolean;
  checkedCount: number;
  firstInvalidId?: string;
  error?: string;
}> {
  logger.info({ tenantId, from, to }, 'Verifying audit chain integrity');

  try {
    const conditions = [eq(auditEvents.tenantId, tenantId)];

    if (from) {
      conditions.push(gte(auditEvents.timestamp, new Date(from)));
    }
    if (to) {
      conditions.push(lte(auditEvents.timestamp, new Date(to)));
    }

    const events = await db
      .select()
      .from(auditEvents)
      .where(and(...conditions))
      .orderBy(auditEvents.timestamp);

    let checkedCount = 0;

    for (const event of events) {
      const eventData = {
        tenantId: event.tenantId,
        timestamp: event.timestamp.toISOString(),
        actor: event.actor,
        action: event.action,
        target: event.target,
        payload: event.payload,
        ip: event.ip,
        userAgent: event.userAgent,
        prevHash: event.prevHash,
      };

      const calculatedHash = createHash('sha256')
        .update(JSON.stringify(eventData) + event.prevHash)
        .digest('hex');

      if (calculatedHash !== event.hash) {
        logger.error(
          { eventId: event.id, calculatedHash, storedHash: event.hash },
          'Hash mismatch detected!'
        );
        return {
          valid: false,
          checkedCount,
          firstInvalidId: event.id,
          error: 'Hash chain broken - potential tampering detected!',
        };
      }

      checkedCount++;
    }

    logger.info({ checkedCount }, 'Integrity check passed');
    return { valid: true, checkedCount };
  } catch (error) {
    logger.error({ error }, 'Integrity check failed');
    return { valid: false, checkedCount: 0, error: String(error) };
  }
}
