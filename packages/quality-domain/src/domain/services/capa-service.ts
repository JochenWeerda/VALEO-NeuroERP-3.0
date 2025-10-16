import { db } from '../../infra/db/connection';
import { capas } from '../../infra/db/schema';
import { CreateCapa, UpdateCapa, Capa } from '../entities/capa';
import { publishEvent } from '../../infra/messaging/publisher';
import { eq, and, desc, or, like, sql, lt } from 'drizzle-orm';

/**
 * Generate CAPA number
 */
function generateCapaNumber(tenantId: string): string {
  const year = new Date().getFullYear();
  const random = Math.floor(Math.random() * 100000).toString().padStart(5, '0');
  return `CAPA-${year}-${random}`;
}

/**
 * Create a new CAPA
 */
export async function createCapa(data: CreateCapa, userId: string): Promise<Capa> {
  const capaNumber = generateCapaNumber(data.tenantId);
  
  const [capa] = await db.insert(capas).values({
    ...data,
    capaNumber,
    createdBy: userId,
    dueDate: new Date(data.dueDate),
  }).returning();

  if (capa === undefined || capa === null) {
    throw new Error('Failed to create CAPA');
  }

  // Publish event
  await publishEvent('capa.created', {
    tenantId: data.tenantId,
    capaId: capa.id,
    capaNumber: capa.capaNumber,
    type: capa.type,
    linkedNcIds: data.linkedNcIds ?? [],
    occurredAt: new Date().toISOString(),
  });

  return capa as any;
}

/**
 * Get CAPA by ID
 */
export async function getCapaById(tenantId: string, capaId: string): Promise<Capa | null> {
  const [capa] = await db
    .select()
    .from(capas)
    .where(and(eq(capas.id, capaId), eq(capas.tenantId, tenantId)))
    .limit(1);

  return capa as any || null;
}

/**
 * Update CAPA
 */
export async function updateCapa(
  tenantId: string,
  capaId: string,
  data: UpdateCapa,
  userId: string
): Promise<Capa> {
  const updateData: any = {
    ...data,
    updatedBy: userId,
    updatedAt: new Date(),
  };

  // Convert date strings to Date objects
  if (data.dueDate) {
    updateData.dueDate = new Date(data.dueDate);
  }
  if (data.implementedAt) {
    updateData.implementedAt = new Date(data.implementedAt);
  }
  if (data.verifiedAt) {
    updateData.verifiedAt = new Date(data.verifiedAt);
  }

  const [updated] = await db
    .update(capas)
    .set(updateData)
    .where(and(eq(capas.id, capaId), eq(capas.tenantId, tenantId)))
    .returning();

  if (updated === undefined || updated === null) {
    throw new Error('CAPA not found or update failed');
  }

  return updated as any;
}

/**
 * Implement CAPA
 */
export async function implementCapa(
  tenantId: string,
  capaId: string,
  userId: string
): Promise<Capa> {
  const [updated] = await db
    .update(capas)
    .set({
      status: 'Implemented',
      implementedAt: new Date(),
      updatedBy: userId,
      updatedAt: new Date(),
    })
    .where(and(eq(capas.id, capaId), eq(capas.tenantId, tenantId)))
    .returning();

  if (updated === undefined || updated === null) {
    throw new Error('CAPA not found');
  }

  // Publish event
  await publishEvent('capa.implemented', {
    tenantId,
    capaId,
    occurredAt: new Date().toISOString(),
  });

  return updated as any;
}

/**
 * Verify CAPA
 */
export async function verifyCapa(
  tenantId: string,
  capaId: string,
  userId: string,
  effectivenessCheck: boolean,
  effectivenessComment?: string
): Promise<Capa> {
  const [updated] = await db
    .update(capas)
    .set({
      status: effectivenessCheck ? 'Verified' : 'Rejected',
      verifiedAt: new Date(),
      verifiedBy: userId,
      effectivenessCheck,
      effectivenessComment,
      updatedBy: userId,
      updatedAt: new Date(),
    } as any)
    .where(and(eq(capas.id, capaId), eq(capas.tenantId, tenantId)))
    .returning();

  if (updated === undefined || updated === null) {
    throw new Error('CAPA not found');
  }

  // Publish event
  await publishEvent('capa.verified', {
    tenantId,
    capaId,
    verifiedBy: userId,
    effectivenessCheck,
    occurredAt: new Date().toISOString(),
  });

  return updated as any;
}

/**
 * Close CAPA
 */
export async function closeCapa(
  tenantId: string,
  capaId: string,
  userId: string,
  closureComment?: string
): Promise<Capa> {
  const [updated] = await db
    .update(capas)
    .set({
      status: 'Closed',
      closedAt: new Date(),
      closedBy: userId,
      closureComment,
      updatedBy: userId,
      updatedAt: new Date(),
    } as any)
    .where(and(eq(capas.id, capaId), eq(capas.tenantId, tenantId)))
    .returning();

  if (updated === undefined || updated === null) {
    throw new Error('CAPA not found');
  }

  return updated as any;
}

/**
 * Escalate CAPA
 */
export async function escalateCapa(
  tenantId: string,
  capaId: string,
  escalatedTo: string,
  reason: string
): Promise<Capa> {
  const [updated] = await db
    .update(capas)
    .set({
      escalated: true,
      escalatedTo,
      escalatedAt: new Date(),
      escalationReason: reason,
      updatedAt: new Date(),
    })
    .where(and(eq(capas.id, capaId), eq(capas.tenantId, tenantId)))
    .returning();

  if (updated === undefined || updated === null) {
    throw new Error('CAPA not found');
  }

  // Publish event
  await publishEvent('capa.escalated', {
    tenantId,
    capaId,
    escalatedTo,
    reason,
    occurredAt: new Date().toISOString(),
  });

  return updated as any;
}

/**
 * List CAPAs with filters and pagination
 */
export async function listCapas(
  tenantId: string,
  filters: {
    status?: string;
    type?: string;
    responsibleUserId?: string;
    overdue?: boolean;
    search?: string;
  },
  pagination: {
    page?: number;
    limit?: number;
  } = {}
): Promise<{ data: Capa[]; total: number; page: number; limit: number }> {
  const page = pagination.page || 1;
  const limit = pagination.limit || 50;
  const offset = (page - 1) * limit;

  // Build where clause
  const conditions = [eq(capas.tenantId, tenantId)];

  if (filters.status) {
    conditions.push(eq(capas.status, filters.status));
  }
  if (filters.type) {
    conditions.push(eq(capas.type, filters.type));
  }
  if (filters.responsibleUserId) {
    conditions.push(eq(capas.responsibleUserId, filters.responsibleUserId));
  }
  if (filters.overdue) {
    conditions.push(lt(capas.dueDate, new Date()));
    conditions.push(or(
      eq(capas.status, 'Open'),
      eq(capas.status, 'InProgress')
    )!);
  }
  if (filters.search) {
    conditions.push(
      or(
        like(capas.title, `%${filters.search}%`),
        like(capas.description, `%${filters.search}%`),
        like(capas.capaNumber, `%${filters.search}%`)
      )!
    );
  }

  // Get total count
  const [countResult] = await db
    .select({ count: sql<number>`count(*)` })
    .from(capas)
    .where(and(...conditions));

  const total = Number(countResult?.count || 0);

  // Get paginated results
  const results = await db
    .select()
    .from(capas)
    .where(and(...conditions))
    .orderBy(desc(capas.createdAt))
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
 * Get overdue CAPAs
 */
export async function getOverdueCapas(tenantId: string): Promise<Capa[]> {
  const results = await db
    .select()
    .from(capas)
    .where(
      and(
        eq(capas.tenantId, tenantId),
        lt(capas.dueDate, new Date()),
        or(eq(capas.status, 'Open'), eq(capas.status, 'InProgress'))!
      )
    )
    .orderBy(capas.dueDate);

  return results as any;
}

/**
 * Get CAPA statistics
 */
export async function getCapaStatistics(
  tenantId: string,
  filters?: {
    startDate?: string;
    endDate?: string;
  }
): Promise<{
  total: number;
  byStatus: Record<string, number>;
  byType: Record<string, number>;
  overdue: number;
  averageTimeToClose: number; // in days
}> {
  const conditions = [eq(capas.tenantId, tenantId)];

  if (filters?.startDate) {
    conditions.push(sql`${capas.createdAt} >= ${filters.startDate}`);
  }
  if (filters?.endDate) {
    conditions.push(sql`${capas.createdAt} <= ${filters.endDate}`);
  }

  const capaList = await db
    .select()
    .from(capas)
    .where(and(...conditions));

  const total = capaList.length;
  const byStatus: Record<string, number> = {};
  const byType: Record<string, number> = {};
  let overdue = 0;
  let totalDaysToClose = 0;
  let closedCount = 0;

  for (const capa of capaList) {
    byStatus[capa.status] = (byStatus[capa.status] || 0) + 1;
    byType[capa.type] = (byType[capa.type] || 0) + 1;

    if (capa.dueDate < new Date() && (capa.status === 'Open' || capa.status === 'InProgress')) {
      overdue++;
    }

    if (capa.closedAt && capa.createdAt) {
      const days = Math.floor((capa.closedAt.getTime() - capa.createdAt.getTime()) / (1000 * 60 * 60 * 24));
      totalDaysToClose += days;
      closedCount++;
    }
  }

  const averageTimeToClose = closedCount > 0 ? Math.round(totalDaysToClose / closedCount) : 0;

  return { total, byStatus, byType, overdue, averageTimeToClose };
}

