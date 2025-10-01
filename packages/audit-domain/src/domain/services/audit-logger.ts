import { db } from '../../infra/db/connection';
import { auditEvents } from '../../infra/db/schema';
import { CreateAuditEvent, AuditEvent } from '../entities/audit-event';
import { createHash } from 'crypto';
import { eq, desc, and, gte, lte } from 'drizzle-orm';
import pino from 'pino';

const logger = pino({ name: 'audit-logger' });

export async function logAuditEvent(
  tenantId: string,
  input: CreateAuditEvent
): Promise<AuditEvent> {
  logger.info({ tenantId, action: input.action, target: input.target }, 'Logging audit event');

  // 1. Get previous hash (for chain)
  const [prev] = await db
    .select()
    .from(auditEvents)
    .where(eq(auditEvents.tenantId, tenantId))
    .orderBy(desc(auditEvents.createdAt))
    .limit(1);

  const prevHash = prev?.hash ?? '';

  // 2. Create event entry
  const timestamp = new Date().toISOString();
  const eventData = {
    tenantId,
    timestamp,
    actor: input.actor,
    action: input.action,
    target: input.target,
    payload: input.payload,
    ip: input.ip,
    userAgent: input.userAgent,
    prevHash,
  };

  // 3. Calculate hash (SHA-256 of event + prevHash)
  const hash = createHash('sha256')
    .update(JSON.stringify(eventData) + prevHash)
    .digest('hex');

  // 4. Insert (append-only, no updates!)
  const [event] = await db
    .insert(auditEvents)
    .values({
      tenantId,
      timestamp: new Date(timestamp),
      actor: eventData.actor,
      action: eventData.action,
      target: eventData.target,
      payload: eventData.payload ?? null,
      ip: eventData.ip ?? null,
      userAgent: eventData.userAgent ?? null,
      prevHash,
      hash,
    })
    .returning();

  if (!event) throw new Error('Failed to log audit event');

  logger.info({ eventId: event.id, hash }, 'Audit event logged');

  return {
    ...event,
    timestamp: event.timestamp.toISOString(),
    createdAt: event.createdAt.toISOString(),
  } as AuditEvent;
}

export async function getAuditEvents(
  tenantId: string,
  filters: {
    from?: string;
    to?: string;
    actor?: string;
    action?: string;
    targetType?: string;
  }
): Promise<AuditEvent[]> {
  const conditions = [eq(auditEvents.tenantId, tenantId)];

  if (filters.from) {
    conditions.push(gte(auditEvents.timestamp, new Date(filters.from)));
  }
  if (filters.to) {
    conditions.push(lte(auditEvents.timestamp, new Date(filters.to)));
  }
  if (filters.action) {
    conditions.push(eq(auditEvents.action, filters.action));
  }

  const events = await db
    .select()
    .from(auditEvents)
    .where(and(...conditions))
    .orderBy(desc(auditEvents.timestamp))
    .limit(1000);

  return events.map(e => ({
    ...e,
    timestamp: e.timestamp.toISOString(),
    createdAt: e.createdAt.toISOString(),
  })) as AuditEvent[];
}

export async function getAuditEventById(
  tenantId: string,
  eventId: string
): Promise<AuditEvent | null> {
  const [event] = await db
    .select()
    .from(auditEvents)
    .where(and(eq(auditEvents.id, eventId), eq(auditEvents.tenantId, tenantId)))
    .limit(1);

  if (!event) return null;

  return {
    ...event,
    timestamp: event.timestamp.toISOString(),
    createdAt: event.createdAt.toISOString(),
  } as AuditEvent;
}
