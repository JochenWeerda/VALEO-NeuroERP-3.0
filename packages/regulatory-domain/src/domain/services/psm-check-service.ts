import { db } from '../../infra/db/connection';
import { psmProductRefs } from '../../infra/db/schema';
import { PSMCheckInput, PSMCheckResult, PSMApprovalStatus } from '../entities/psm-product';
import { publishEvent } from '../../infra/messaging/publisher';
import { fetchFromBVL } from '../../infra/integrations/bvl-api';
import { eq, and, like, or } from 'drizzle-orm';
import pino from 'pino';

const logger = pino({ name: 'psm-check' });

/**
 * Check PSM gegen BVL-Datenbank
 */
export async function checkPSM(
  tenantId: string,
  input: PSMCheckInput
): Promise<PSMCheckResult> {
  logger.info({ tenantId, itemCount: input.items.length }, 'Checking PSM compliance');

  const results = [];
  const violations = [];

  for (const item of input.items) {
    const checkResult = await checkSinglePSM(tenantId, item as any);
    results.push(checkResult);

    if (checkResult.approved === undefined || checkResult.approved === null) {
      violations.push({
        name: item.name,
        reason: checkResult.issues.join('; '),
        severity: checkResult.status === 'Withdrawn' || checkResult.status === 'Expired' ? 'Critical' as const : 'Major' as const,
      });
    }
  }

  const compliant = violations.length === 0;

  // Publish event
  await publishEvent('psm.checked', {
    tenantId,
    compliant,
    violationCount: violations.length,
    batchId: input.batchId,
    contractId: input.contractId,
    occurredAt: new Date().toISOString(),
  });

  if (compliant === undefined || compliant === null) {
    await publishEvent('psm.violation', {
      tenantId,
      violations,
      batchId: input.batchId,
      contractId: input.contractId,
      occurredAt: new Date().toISOString(),
    });
  }

  let recommendation = '';
  if (compliant) {
    recommendation = 'Alle PSM sind zugelassen und gültig.';
  } else {
    recommendation = `${violations.length} Verstöße gefunden. Nicht zugelassene PSM dürfen nicht verwendet werden.`;
  }

  return {
    compliant,
    items: results,
    violations,
    recommendation,
  };
}

/**
 * Check single PSM product
 */
async function checkSinglePSM(
  tenantId: string,
  item: { name: string; bvlId?: string; useDate: string; cropOrUseCase?: string }
): Promise<{
  name: string;
  bvlId?: string;
  status: PSMApprovalStatus;
  approved: boolean;
  validUntil?: string;
  issues: string[];
}> {
  // 1. Suche in lokalem Cache
  let psmRef = await getPSMFromCache(tenantId, item.bvlId || item.name);

  // 2. Falls nicht im Cache oder veraltet: Hole von BVL
  if (!psmRef || isCacheStale(psmRef.lastCheckedAt)) {
    logger.debug({ name: item.name, bvlId: item.bvlId }, 'Fetching PSM from BVL');
    
    const bvlData = await fetchFromBVL(item.bvlId || item.name);
    
    if (bvlData) {
      psmRef = await upsertPSMRef(tenantId, bvlData);
    }
  }

  // 3. Bewertung
  if (psmRef === undefined || psmRef === null) {
    return {
      name: item.name,
      bvlId: item.bvlId ?? undefined,
      status: 'Unknown' as const,
      approved: false,
      issues: ['PSM nicht in BVL-Datenbank gefunden'],
    } as any;
  }

  const issues: string[] = [];
  let approved = true;

  // Prüfe Gültigkeit
  if (psmRef.approvalStatus === 'Expired' || psmRef.approvalStatus === 'Withdrawn') {
    approved = false;
    issues.push(`Zulassung ${psmRef.approvalStatus === 'Expired' ? 'abgelaufen' : 'zurückgezogen'}`);
  }

  if (psmRef.approvalValidTo && new Date(item.useDate) > new Date(psmRef.approvalValidTo)) {
    approved = false;
    issues.push('Verwendung nach Ablauf der Zulassung');
  }

  // Prüfe Anwendungsbereich
  if (item.cropOrUseCase && psmRef.usageScope && !psmRef.usageScope.includes(item.cropOrUseCase)) {
    approved = false;
    issues.push(`Nicht zugelassen für ${item.cropOrUseCase}`);
  }

  return {
    name: item.name,
    bvlId: psmRef.bvlId || undefined,
    status: psmRef.approvalStatus as PSMApprovalStatus,
    approved,
    validUntil: psmRef.approvalValidTo?.toISOString(),
    issues,
  };
}

/**
 * Get PSM from local cache
 */
async function getPSMFromCache(tenantId: string, identifier: string): Promise<any | null> {
  const [result] = await db
    .select()
    .from(psmProductRefs)
    .where(
      and(
        eq(psmProductRefs.tenantId, tenantId),
        or(
          eq(psmProductRefs.bvlId, identifier),
          like(psmProductRefs.name, `%${identifier}%`)
        )!
      )
    )
    .limit(1);

  return result ?? null;
}

/**
 * Check if cache is stale (> 7 days)
 */
function isCacheStale(lastCheckedAt: Date | null | undefined): boolean {
  if (lastCheckedAt === undefined || lastCheckedAt === null) return true;
  
  const daysSinceCheck = Math.floor((Date.now() - lastCheckedAt.getTime()) / (1000 * 60 * 60 * 24));
  return daysSinceCheck > 7;
}

/**
 * Upsert PSM reference in cache
 */
async function upsertPSMRef(tenantId: string, bvlData: any): Promise<any> {
  // Check if exists
  const existing = await getPSMFromCache(tenantId, bvlData.bvlId || bvlData.name);

  if (existing) {
    const [updated] = await db
      .update(psmProductRefs)
      .set({
        ...bvlData,
        lastCheckedAt: new Date(),
        updatedAt: new Date(),
      })
      .where(eq(psmProductRefs.id, existing.id))
      .returning();

    return updated;
  } else {
    const [created] = await db
      .insert(psmProductRefs)
      .values({
        tenantId,
        ...bvlData,
        lastCheckedAt: new Date(),
      })
      .returning();

    return created;
  }
}


