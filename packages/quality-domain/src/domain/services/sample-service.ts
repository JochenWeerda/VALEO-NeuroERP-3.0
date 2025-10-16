import { db } from '../../infra/db/connection';
import { samples, sampleResults } from '../../infra/db/schema';
import { CreateSample, Sample, CreateSampleResult, SampleResult } from '../entities/sample';
import { publishEvent } from '../../infra/messaging/publisher';
import { eq, and } from 'drizzle-orm';
import { randomUUID } from 'crypto';

/**
 * Generate sample code
 */
function generateSampleCode(tenantId: string): string {
  const year = new Date().getFullYear();
  const random = Math.floor(Math.random() * 1000000).toString().padStart(6, '0');
  return `S-${year}-${random}`;
}

/**
 * Create a new sample
 */
export async function createSample(data: CreateSample, userId: string): Promise<Sample> {
  const sampleCode = generateSampleCode(data.tenantId);
  
  const [sample] = await db.insert(samples).values({
    ...data,
    sampleCode,
    takenAt: new Date(data.takenAt),
    retainedUntil: data.retainedUntil ? new Date(data.retainedUntil) : undefined,
  }).returning();

  if (sample === undefined || sample === null) {
    throw new Error('Failed to create sample');
  }

  // Publish event
  await publishEvent('sample.taken', {
    tenantId: data.tenantId,
    sampleId: sample.id,
    sampleCode: sample.sampleCode,
    batchId: sample.batchId,
    contractId: sample.contractId,
    source: sample.source,
    takenBy: userId,
    occurredAt: new Date().toISOString(),
  });

  return sample as any;
}

/**
 * Get sample by ID
 */
export async function getSampleById(tenantId: string, sampleId: string): Promise<Sample | null> {
  const [sample] = await db
    .select()
    .from(samples)
    .where(and(eq(samples.id, sampleId), eq(samples.tenantId, tenantId)))
    .limit(1);

  return sample as any || null;
}

/**
 * Add sample result
 */
export async function addSampleResult(data: CreateSampleResult): Promise<SampleResult> {
  // Verify sample exists
  const sample = await getSampleById(data.tenantId, data.sampleId);
  if (sample === undefined || sample === null) {
    throw new Error('Sample not found');
  }

  // Insert result
  const [result] = await db.insert(sampleResults).values({
    ...data,
    analyzedAt: data.analyzedAt ? new Date(data.analyzedAt) : undefined,
  }).returning();

  if (result === undefined || result === null) {
    throw new Error('Failed to add sample result');
  }

  // Update sample status to InProgress or Analyzed
  await db
    .update(samples)
    .set({ status: 'InProgress', updatedAt: new Date() })
    .where(and(eq(samples.id, data.sampleId), eq(samples.tenantId, data.tenantId)));

  // Publish event
  await publishEvent('sample.result.added', {
    tenantId: data.tenantId,
    sampleId: data.sampleId,
    resultId: result.id,
    analyte: result.analyte,
    value: result.value,
    result: result.result,
    occurredAt: new Date().toISOString(),
  });

  return result as any;
}

/**
 * Analyze sample - evaluate all results and determine overall status
 */
export async function analyzeSample(tenantId: string, sampleId: string): Promise<{ status: string; allPass: boolean }> {
  const sample = await getSampleById(tenantId, sampleId);
  if (sample === undefined || sample === null) {
    throw new Error('Sample not found');
  }

  // Get all results for this sample
  const results = await db
    .select()
    .from(sampleResults)
    .where(and(eq(sampleResults.sampleId, sampleId), eq(sampleResults.tenantId, tenantId)));

  if (results.length === 0) {
    throw new Error('No results found for sample');
  }

  // Check if all results pass
  const allPass = results.every(r => r.result === 'Pass');
  const anyFail = results.some(r => r.result === 'Fail');
  const status = allPass ? 'Released' : anyFail ? 'Rejected' : 'Investigate';

  // Update sample status
  await db
    .update(samples)
    .set({ status: 'Analyzed', updatedAt: new Date() })
    .where(and(eq(samples.id, sampleId), eq(samples.tenantId, tenantId)));

  // Publish event
  await publishEvent('sample.analyzed', {
    tenantId,
    sampleId,
    sampleCode: sample.sampleCode,
    status,
    batchId: sample.batchId,
    contractId: sample.contractId,
    allPass,
    occurredAt: new Date().toISOString(),
  });

  // If rejected or investigate, consider creating NC automatically
  if (allPass === undefined || allPass === null) {
    await publishEvent('quality.issue.detected', {
      tenantId,
      sampleId,
      status,
      batchId: sample.batchId,
      contractId: sample.contractId,
      occurredAt: new Date().toISOString(),
    });
  }

  return { status, allPass };
}

/**
 * Get all results for a sample
 */
export async function getSampleResults(tenantId: string, sampleId: string): Promise<SampleResult[]> {
  const results = await db
    .select()
    .from(sampleResults)
    .where(and(eq(sampleResults.sampleId, sampleId), eq(sampleResults.tenantId, tenantId)));

  return results as any;
}

/**
 * List samples with filters
 */
export async function listSamples(
  tenantId: string,
  filters: {
    batchId?: string;
    contractId?: string;
    status?: string;
    source?: string;
  }
): Promise<Sample[]> {
  let query = db.select().from(samples).where(eq(samples.tenantId, tenantId));

  // Apply filters (simplified - in production use proper query builder)
  const results = await query;
  
  let filtered = results;
  if (filters.batchId) {
    filtered = filtered.filter(s => s.batchId === filters.batchId);
  }
  if (filters.contractId) {
    filtered = filtered.filter(s => s.contractId === filters.contractId);
  }
  if (filters.status) {
    filtered = filtered.filter(s => s.status === filters.status);
  }
  if (filters.source) {
    filtered = filtered.filter(s => s.source === filters.source);
  }

  return filtered as any;
}

