import { db } from '../../infra/db/connection';
import { qualityPlans } from '../../infra/db/schema';
import { CreateQualityPlan, UpdateQualityPlan, QualityPlan } from '../entities/quality-plan';
import { publishEvent } from '../../infra/messaging/publisher';
import { eq, and } from 'drizzle-orm';

/**
 * Create a new quality plan
 */
export async function createQualityPlan(data: CreateQualityPlan, userId: string): Promise<QualityPlan> {
  const [plan] = await db.insert(qualityPlans).values({
    ...data,
    createdBy: userId,
  }).returning();

  if (plan === undefined || plan === null) {
    throw new Error('Failed to create quality plan');
  }

  // Publish event
  await publishEvent('plan.created', {
    tenantId: data.tenantId,
    planId: plan.id,
    name: plan.name,
    commodity: plan.commodity,
    contractId: plan.contractId,
    occurredAt: new Date().toISOString(),
  });

  return plan as any;
}

/**
 * Get quality plan by ID
 */
export async function getQualityPlanById(tenantId: string, planId: string): Promise<QualityPlan | null> {
  const [plan] = await db
    .select()
    .from(qualityPlans)
    .where(and(eq(qualityPlans.id, planId), eq(qualityPlans.tenantId, tenantId)))
    .limit(1);

  return plan as any || null;
}

/**
 * Update quality plan
 */
export async function updateQualityPlan(
  tenantId: string,
  planId: string,
  data: UpdateQualityPlan,
  userId: string
): Promise<QualityPlan> {
  const [updated] = await db
    .update(qualityPlans)
    .set({
      ...data,
      updatedBy: userId,
      updatedAt: new Date(),
    } as any)
    .where(and(eq(qualityPlans.id, planId), eq(qualityPlans.tenantId, tenantId)))
    .returning();

  if (updated === undefined || updated === null) {
    throw new Error('Quality plan not found or update failed');
  }

  // Publish event
  await publishEvent('plan.updated', {
    tenantId,
    planId,
    occurredAt: new Date().toISOString(),
  });

  return updated as any;
}

/**
 * List quality plans with filters
 */
export async function listQualityPlans(
  tenantId: string,
  filters: {
    commodity?: string;
    contractId?: string;
    active?: boolean;
  }
): Promise<QualityPlan[]> {
  let query = db.select().from(qualityPlans).where(eq(qualityPlans.tenantId, tenantId));

  const results = await query;
  
  let filtered = results;
  if (filters.commodity) {
    filtered = filtered.filter(p => p.commodity === filters.commodity);
  }
  if (filters.contractId) {
    filtered = filtered.filter(p => p.contractId === filters.contractId);
  }
  if (filters.active !== undefined) {
    filtered = filtered.filter(p => p.active === filters.active);
  }

  return filtered as any;
}

/**
 * Deactivate quality plan
 */
export async function deactivateQualityPlan(
  tenantId: string,
  planId: string,
  userId: string
): Promise<void> {
  await db
    .update(qualityPlans)
    .set({
      active: false,
      updatedBy: userId,
      updatedAt: new Date(),
    })
    .where(and(eq(qualityPlans.id, planId), eq(qualityPlans.tenantId, tenantId)));

  // Publish event
  await publishEvent('plan.deactivated', {
    tenantId,
    planId,
    occurredAt: new Date().toISOString(),
  });
}

