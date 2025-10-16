import { db } from '../../infra/db/connection';
import { nonConformities } from '../../infra/db/schema';
import { CreateNonConformity, UpdateNonConformity, NonConformity } from '../entities/non-conformity';
import { publishEvent } from '../../infra/messaging/publisher';
import { eq, and, desc, or, like, sql } from 'drizzle-orm';

/**
 * Generate NC number
 */
function generateNcNumber(tenantId: string): string {
  const year = new Date().getFullYear();
  const random = Math.floor(Math.random() * 100000).toString().padStart(5, '0');
  return `NC-${year}-${random}`;
}

/**
 * Create a new non-conformity
 */
export async function createNonConformity(data: CreateNonConformity, userId: string): Promise<NonConformity> {
  const ncNumber = generateNcNumber(data.tenantId);
  
  const [nc] = await db.insert(nonConformities).values({
    ...data,
    ncNumber,
    detectedAt: new Date(data.detectedAt),
  } as any).returning();

  if (nc === undefined || nc === null) {
    throw new Error('Failed to create non-conformity');
  }

  // Publish event
  await publishEvent('nc.created', {
    tenantId: data.tenantId,
    ncId: nc.id,
    ncNumber: nc.ncNumber,
    type: nc.type,
    severity: nc.severity,
    batchId: nc.batchId,
    contractId: nc.contractId,
    occurredAt: new Date().toISOString(),
  });

  // If critical, publish alert
  if (nc.severity === 'Critical') {
    await publishEvent('nc.critical.alert', {
      tenantId: data.tenantId,
      ncId: nc.id,
      ncNumber: nc.ncNumber,
      title: nc.title,
      occurredAt: new Date().toISOString(),
    });
  }

  return nc as any;
}

/**
 * Get NC by ID
 */
export async function getNonConformityById(tenantId: string, ncId: string): Promise<NonConformity | null> {
  const [nc] = await db
    .select()
    .from(nonConformities)
    .where(and(eq(nonConformities.id, ncId), eq(nonConformities.tenantId, tenantId)))
    .limit(1);

  return nc as any || null;
}

/**
 * Update NC
 */
export async function updateNonConformity(
  tenantId: string,
  ncId: string,
  data: UpdateNonConformity,
  userId: string
): Promise<NonConformity> {
  const [updated] = await db
    .update(nonConformities)
    .set({
      ...data,
      updatedAt: new Date(),
    } as any)
    .where(and(eq(nonConformities.id, ncId), eq(nonConformities.tenantId, tenantId)))
    .returning();

  if (updated === undefined || updated === null) {
    throw new Error('Non-conformity not found or update failed');
  }

  // Publish event
  await publishEvent('nc.updated', {
    tenantId,
    ncId,
    status: updated.status,
    occurredAt: new Date().toISOString(),
  });

  return updated as any;
}

/**
 * Close NC
 */
export async function closeNonConformity(
  tenantId: string,
  ncId: string,
  userId: string,
  comment?: string
): Promise<NonConformity> {
  const [updated] = await db
    .update(nonConformities)
    .set({
      status: 'Closed',
      closedAt: new Date(),
      closedBy: userId,
      updatedAt: new Date(),
    })
    .where(and(eq(nonConformities.id, ncId), eq(nonConformities.tenantId, tenantId)))
    .returning();

  if (updated === undefined || updated === null) {
    throw new Error('Non-conformity not found');
  }

  // Publish event
  await publishEvent('nc.closed', {
    tenantId,
    ncId,
    closedBy: userId,
    occurredAt: new Date().toISOString(),
  });

  return updated as any;
}

/**
 * Assign NC to user
 */
export async function assignNonConformity(
  tenantId: string,
  ncId: string,
  assignedTo: string
): Promise<NonConformity> {
  const [updated] = await db
    .update(nonConformities)
    .set({
      assignedTo,
      updatedAt: new Date(),
    })
    .where(and(eq(nonConformities.id, ncId), eq(nonConformities.tenantId, tenantId)))
    .returning();

  if (updated === undefined || updated === null) {
    throw new Error('Non-conformity not found');
  }

  return updated as any;
}

/**
 * Link NC to CAPA
 */
export async function linkNcToCapa(
  tenantId: string,
  ncId: string,
  capaId: string
): Promise<NonConformity> {
  const [updated] = await db
    .update(nonConformities)
    .set({
      capaId,
      updatedAt: new Date(),
    })
    .where(and(eq(nonConformities.id, ncId), eq(nonConformities.tenantId, tenantId)))
    .returning();

  if (updated === undefined || updated === null) {
    throw new Error('Non-conformity not found');
  }

  return updated as any;
}

/**
 * List NCs with filters and pagination
 */
export async function listNonConformities(
  tenantId: string,
  filters: {
    batchId?: string;
    contractId?: string;
    status?: string;
    severity?: string;
    type?: string;
    supplierId?: string;
    assignedTo?: string;
    search?: string;
  },
  pagination: {
    page?: number;
    limit?: number;
  } = {}
): Promise<{ data: NonConformity[]; total: number; page: number; limit: number }> {
  const page = pagination.page || 1;
  const limit = pagination.limit || 50;
  const offset = (page - 1) * limit;

  // Build where clause
  const conditions = [eq(nonConformities.tenantId, tenantId)];

  if (filters.batchId) {
    conditions.push(eq(nonConformities.batchId, filters.batchId));
  }
  if (filters.contractId) {
    conditions.push(eq(nonConformities.contractId, filters.contractId));
  }
  if (filters.status) {
    conditions.push(eq(nonConformities.status, filters.status));
  }
  if (filters.severity) {
    conditions.push(eq(nonConformities.severity, filters.severity));
  }
  if (filters.type) {
    conditions.push(eq(nonConformities.type, filters.type));
  }
  if (filters.supplierId) {
    conditions.push(eq(nonConformities.supplierId, filters.supplierId));
  }
  if (filters.assignedTo) {
    conditions.push(eq(nonConformities.assignedTo, filters.assignedTo));
  }
  if (filters.search) {
    conditions.push(
      or(
        like(nonConformities.title, `%${filters.search}%`),
        like(nonConformities.description, `%${filters.search}%`),
        like(nonConformities.ncNumber, `%${filters.search}%`)
      )!
    );
  }

  // Get total count
  const [countResult] = await db
    .select({ count: sql<number>`count(*)` })
    .from(nonConformities)
    .where(and(...conditions));

  const total = Number(countResult?.count || 0);

  // Get paginated results
  const results = await db
    .select()
    .from(nonConformities)
    .where(and(...conditions))
    .orderBy(desc(nonConformities.detectedAt))
    .limit(limit)
    .offset(offset);

  return {
    data: results as any,
    total,
    page,
    limit,
  };
}

/**
 * Get NC statistics
 */
export async function getNcStatistics(
  tenantId: string,
  filters?: {
    startDate?: string;
    endDate?: string;
  }
): Promise<{
  total: number;
  byStatus: Record<string, number>;
  bySeverity: Record<string, number>;
  byType: Record<string, number>;
}> {
  const conditions = [eq(nonConformities.tenantId, tenantId)];

  if (filters?.startDate) {
    conditions.push(sql`${nonConformities.detectedAt} >= ${filters.startDate}`);
  }
  if (filters?.endDate) {
    conditions.push(sql`${nonConformities.detectedAt} <= ${filters.endDate}`);
  }

  const ncs = await db
    .select()
    .from(nonConformities)
    .where(and(...conditions));

  const total = ncs.length;
  const byStatus: Record<string, number> = {};
  const bySeverity: Record<string, number> = {};
  const byType: Record<string, number> = {};

  for (const nc of ncs) {
    byStatus[nc.status] = (byStatus[nc.status] || 0) + 1;
    bySeverity[nc.severity] = (bySeverity[nc.severity] || 0) + 1;
    byType[nc.type] = (byType[nc.type] || 0) + 1;
  }

  return { total, byStatus, bySeverity, byType };
}

