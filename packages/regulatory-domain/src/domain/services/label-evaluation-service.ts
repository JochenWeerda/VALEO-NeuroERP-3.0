import { db } from '../../infra/db/connection';
import { regulatoryPolicies, labels, evidences } from '../../infra/db/schema';
import { LabelEvaluateInput, LabelEvaluationResult, LabelStatus } from '../entities/label';
import { PolicyRule, VLOG_DEFAULT_RULES, QS_DEFAULT_RULES } from '../entities/regulatory-policy';
import { publishEvent } from '../../infra/messaging/publisher';
import { eq, and } from 'drizzle-orm';
import pino from 'pino';
import { sql } from 'drizzle-orm';

const logger = pino({ name: 'label-evaluation' });

/**
 * Label Eligibility Engine
 * Bewertet ob ein Target (Batch/Contract/Site) die Anforderungen eines Labels erfüllt
 */
export async function evaluateLabel(
  tenantId: string,
  input: LabelEvaluateInput
): Promise<LabelEvaluationResult> {
  logger.info({ tenantId, input }, 'Evaluating label eligibility');

  // 1. Lade relevante Policy
  const policy = await getRelevantPolicy(tenantId, input.labelCode, input.targetRef.type);
  
  if (policy === undefined || policy === null) {
    return {
      eligible: false,
      status: 'Ineligible',
      missingEvidences: [],
      violations: [{
        ruleId: 'policy-missing',
        description: `Keine aktive Policy für Label ${input.labelCode} gefunden`,
        severity: 'Critical',
      }],
      recommendation: `Policy für ${input.labelCode} muss erst erstellt werden.`,
    };
  }

  // 2. Lade verfügbare Evidenzen für dieses Target
  const availableEvidences = await getEvidencesByTarget(tenantId, input.targetRef);

  // 3. Prüfe jede Regel
  const missingEvidences: string[] = [];
  const violations: Array<{ ruleId: string; description: string; severity: 'Minor' | 'Major' | 'Critical' }> = [];

  for (const rule of (policy.rules as PolicyRule[])) {
    const ruleResult = await evaluateRule(rule, availableEvidences, input.context);
    
    if (ruleResult.passed === undefined || ruleResult.passed === null) {
      if (rule.evidenceRequired && ruleResult.evidenceMissing) {
        missingEvidences.push(`${rule.evidenceType}: ${rule.description}`);
      } else {
        violations.push({
          ruleId: rule.ruleId,
          description: ruleResult.reason || rule.description,
          severity: rule.violationSeverity,
        });
      }
    }
  }

  // 4. Bewertung
  const hasCriticalViolations = violations.some(v => v.severity === 'Critical');
  const hasMajorViolations = violations.some(v => v.severity === 'Major');

  let status: LabelStatus = 'Eligible';
  let eligible = true;
  let recommendation = `Label ${input.labelCode} kann vergeben werden.`;

  if (hasCriticalViolations) {
    status = 'Ineligible';
    eligible = false;
    recommendation = `KRITISCH: Label kann nicht vergeben werden. Kritische Verstöße vorhanden.`;
  } else if (hasMajorViolations) {
    status = 'Ineligible';
    eligible = false;
    recommendation = `Label kann nicht vergeben werden. Major-Verstöße müssen behoben werden.`;
  } else if (missingEvidences.length > 0) {
    status = 'Conditional';
    eligible = false;
    recommendation = `Label kann vergeben werden sobald fehlende Nachweise eingereicht sind.`;
  }

  // 5. Confidence-Score (KI-basiert, vereinfacht)
  const confidence = calculateConfidence(availableEvidences.length, (policy.rules as PolicyRule[]).length);

  return {
    eligible,
    status,
    missingEvidences,
    violations,
    recommendation,
    confidence,
  };
}

/**
 * Get relevant policy for label
 */
async function getRelevantPolicy(
  tenantId: string,
  labelCode: string,
  targetType: string
): Promise<any | null> {
  // Map Label-Code to Policy-Key
  const policyKeyMap: Record<string, string> = {
    'VLOG_OGT': 'VLOG',
    'QS': 'QS',
    'REDII_COMPLIANT': 'REDII',
    'GMP_PLUS': 'GMP_PLUS',
    'NON_GMO': 'NON_GMO',
    'ORGANIC_EU': 'ORGANIC',
  };

  const policyKey = policyKeyMap[labelCode] || labelCode;

  const [policy] = await db
    .select()
    .from(regulatoryPolicies)
    .where(
      and(
        eq(regulatoryPolicies.tenantId, tenantId),
        eq(regulatoryPolicies.key, policyKey),
        eq(regulatoryPolicies.active, true)
      )
    )
    .limit(1);

  return policy ?? null;
}

/**
 * Get evidences by target
 */
async function getEvidencesByTarget(
  tenantId: string,
  targetRef: { type: string; id: string }
): Promise<any[]> {
  const results = await db
    .select()
    .from(evidences)
    .where(
      and(
        eq(evidences.tenantId, tenantId),
        eq(evidences.status, 'Valid'),
        sql`${evidences.relatedRef}->>'type' = ${targetRef.type}`,
        sql`${evidences.relatedRef}->>'id' = ${targetRef.id}`
      )
    );

  return results;
}

/**
 * Evaluate single rule
 */
async function evaluateRule(
  rule: PolicyRule,
  availableEvidences: any[],
  context?: Record<string, any>
): Promise<{ passed: boolean; evidenceMissing: boolean; reason?: string }> {
  // Prüfe ob erforderliche Evidenz vorhanden
  if (rule.evidenceRequired) {
    const hasEvidence = availableEvidences.some(ev => ev.type === rule.evidenceType);
    
    if (hasEvidence === undefined || hasEvidence === null) {
      return {
        passed: false,
        evidenceMissing: true,
        reason: `Erforderliche Evidenz fehlt: ${rule.evidenceType}`,
      };
    }
  }

  // Kontextbasierte Prüfungen (vereinfacht)
  if (rule.criteriaValue !== undefined && context) {
    const actualValue = context[rule.criteriaKey];
    
    if (actualValue !== rule.criteriaValue) {
      return {
        passed: false,
        evidenceMissing: false,
        reason: `Kriterium ${rule.criteriaKey} nicht erfüllt: erwartet ${rule.criteriaValue}, tatsächlich ${actualValue}`,
      };
    }
  }

  return { passed: true, evidenceMissing: false };
}

/**
 * Calculate confidence score based on data completeness
 */
function calculateConfidence(evidenceCount: number, ruleCount: number): number {
  // Vereinfachte Confidence-Berechnung
  const minRequired = ruleCount * 0.8; // Mind. 80% der Regeln sollten Evidenzen haben
  const ratio = Math.min(1, evidenceCount / minRequired);
  return Math.round(ratio * 100) / 100;
}

/**
 * Create or update label for target
 */
export async function createOrUpdateLabel(
  tenantId: string,
  input: LabelEvaluateInput,
  evaluation: LabelEvaluationResult,
  userId: string
): Promise<any> {
  // Check if label already exists
  const [existing] = await db
    .select()
    .from(labels)
    .where(
      and(
        eq(labels.tenantId, tenantId),
        eq(labels.code, input.labelCode),
        eq(labels.targetType, input.targetRef.type),
        eq(labels.targetId, input.targetRef.id)
      )
    )
    .limit(1);

  const labelData = {
    code: input.labelCode,
    name: input.labelCode,
    targetType: input.targetRef.type,
    targetId: input.targetRef.id,
    status: evaluation.status,
    missingEvidences: evaluation.missingEvidences,
    issuedAt: evaluation.eligible ? new Date() : undefined,
    issuedBy: evaluation.eligible ? userId : undefined,
  };

  if (existing) {
    // Update
    const [updated] = await db
      .update(labels)
      .set({
        ...(labelData as any),
        updatedAt: new Date(),
      })
      .where(eq(labels.id, existing.id))
      .returning();

    // Publish event
    if (updated) {
      await publishEvent('label.updated', {
        tenantId,
        labelId: updated.id,
        code: updated.code,
        status: updated.status,
        occurredAt: new Date().toISOString(),
      });
    }

    return updated!;
  } else {
    // Create
    const [created] = await db
      .insert(labels)
      .values({
        tenantId,
        ...(labelData as any),
      } as any)
      .returning();

    // Publish event
    if (created) {
      await publishEvent(`label.${evaluation.status.toLowerCase()}`, {
        tenantId,
        labelId: created.id,
        code: created.code,
        targetType: created.targetType,
        targetId: created.targetId,
        occurredAt: new Date().toISOString(),
      });
    }

    return created;
  }
}


