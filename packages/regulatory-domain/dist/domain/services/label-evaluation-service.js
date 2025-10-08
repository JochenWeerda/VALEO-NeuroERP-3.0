"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.evaluateLabel = evaluateLabel;
exports.createOrUpdateLabel = createOrUpdateLabel;
const connection_1 = require("../../infra/db/connection");
const schema_1 = require("../../infra/db/schema");
const publisher_1 = require("../../infra/messaging/publisher");
const drizzle_orm_1 = require("drizzle-orm");
const pino_1 = __importDefault(require("pino"));
const drizzle_orm_2 = require("drizzle-orm");
const logger = (0, pino_1.default)({ name: 'label-evaluation' });
async function evaluateLabel(tenantId, input) {
    logger.info({ tenantId, input }, 'Evaluating label eligibility');
    const policy = await getRelevantPolicy(tenantId, input.labelCode, input.targetRef.type);
    if (!policy) {
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
    const availableEvidences = await getEvidencesByTarget(tenantId, input.targetRef);
    const missingEvidences = [];
    const violations = [];
    for (const rule of policy.rules) {
        const ruleResult = await evaluateRule(rule, availableEvidences, input.context);
        if (!ruleResult.passed) {
            if (rule.evidenceRequired && ruleResult.evidenceMissing) {
                missingEvidences.push(`${rule.evidenceType}: ${rule.description}`);
            }
            else {
                violations.push({
                    ruleId: rule.ruleId,
                    description: ruleResult.reason || rule.description,
                    severity: rule.violationSeverity,
                });
            }
        }
    }
    const hasCriticalViolations = violations.some(v => v.severity === 'Critical');
    const hasMajorViolations = violations.some(v => v.severity === 'Major');
    let status = 'Eligible';
    let eligible = true;
    let recommendation = `Label ${input.labelCode} kann vergeben werden.`;
    if (hasCriticalViolations) {
        status = 'Ineligible';
        eligible = false;
        recommendation = `KRITISCH: Label kann nicht vergeben werden. Kritische Verstöße vorhanden.`;
    }
    else if (hasMajorViolations) {
        status = 'Ineligible';
        eligible = false;
        recommendation = `Label kann nicht vergeben werden. Major-Verstöße müssen behoben werden.`;
    }
    else if (missingEvidences.length > 0) {
        status = 'Conditional';
        eligible = false;
        recommendation = `Label kann vergeben werden sobald fehlende Nachweise eingereicht sind.`;
    }
    const confidence = calculateConfidence(availableEvidences.length, policy.rules.length);
    return {
        eligible,
        status,
        missingEvidences,
        violations,
        recommendation,
        confidence,
    };
}
async function getRelevantPolicy(tenantId, labelCode, targetType) {
    const policyKeyMap = {
        'VLOG_OGT': 'VLOG',
        'QS': 'QS',
        'REDII_COMPLIANT': 'REDII',
        'GMP_PLUS': 'GMP_PLUS',
        'NON_GMO': 'NON_GMO',
        'ORGANIC_EU': 'ORGANIC',
    };
    const policyKey = policyKeyMap[labelCode] || labelCode;
    const [policy] = await connection_1.db
        .select()
        .from(schema_1.regulatoryPolicies)
        .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.regulatoryPolicies.tenantId, tenantId), (0, drizzle_orm_1.eq)(schema_1.regulatoryPolicies.key, policyKey), (0, drizzle_orm_1.eq)(schema_1.regulatoryPolicies.active, true)))
        .limit(1);
    return policy || null;
}
async function getEvidencesByTarget(tenantId, targetRef) {
    const results = await connection_1.db
        .select()
        .from(schema_1.evidences)
        .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.evidences.tenantId, tenantId), (0, drizzle_orm_1.eq)(schema_1.evidences.status, 'Valid'), (0, drizzle_orm_2.sql) `${schema_1.evidences.relatedRef}->>'type' = ${targetRef.type}`, (0, drizzle_orm_2.sql) `${schema_1.evidences.relatedRef}->>'id' = ${targetRef.id}`));
    return results;
}
async function evaluateRule(rule, availableEvidences, context) {
    if (rule.evidenceRequired) {
        const hasEvidence = availableEvidences.some(ev => ev.type === rule.evidenceType);
        if (!hasEvidence) {
            return {
                passed: false,
                evidenceMissing: true,
                reason: `Erforderliche Evidenz fehlt: ${rule.evidenceType}`,
            };
        }
    }
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
function calculateConfidence(evidenceCount, ruleCount) {
    const minRequired = ruleCount * 0.8;
    const ratio = Math.min(1, evidenceCount / minRequired);
    return Math.round(ratio * 100) / 100;
}
async function createOrUpdateLabel(tenantId, input, evaluation, userId) {
    const [existing] = await connection_1.db
        .select()
        .from(schema_1.labels)
        .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.labels.tenantId, tenantId), (0, drizzle_orm_1.eq)(schema_1.labels.code, input.labelCode), (0, drizzle_orm_1.eq)(schema_1.labels.targetType, input.targetRef.type), (0, drizzle_orm_1.eq)(schema_1.labels.targetId, input.targetRef.id)))
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
        const [updated] = await connection_1.db
            .update(schema_1.labels)
            .set({
            ...labelData,
            updatedAt: new Date(),
        })
            .where((0, drizzle_orm_1.eq)(schema_1.labels.id, existing.id))
            .returning();
        await (0, publisher_1.publishEvent)('label.updated', {
            tenantId,
            labelId: updated.id,
            code: updated.code,
            status: updated.status,
            occurredAt: new Date().toISOString(),
        });
        return updated;
    }
    else {
        const [created] = await connection_1.db
            .insert(schema_1.labels)
            .values({
            tenantId,
            ...labelData,
        })
            .returning();
        await (0, publisher_1.publishEvent)(`label.${evaluation.status.toLowerCase()}`, {
            tenantId,
            labelId: created.id,
            code: created.code,
            targetType: created.targetType,
            targetId: created.targetId,
            occurredAt: new Date().toISOString(),
        });
        return created;
    }
}
//# sourceMappingURL=label-evaluation-service.js.map