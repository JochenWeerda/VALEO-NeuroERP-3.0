"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.checkPSM = checkPSM;
const connection_1 = require("../../infra/db/connection");
const schema_1 = require("../../infra/db/schema");
const publisher_1 = require("../../infra/messaging/publisher");
const bvl_api_1 = require("../../infra/integrations/bvl-api");
const drizzle_orm_1 = require("drizzle-orm");
const pino_1 = __importDefault(require("pino"));
const logger = (0, pino_1.default)({ name: 'psm-check' });
async function checkPSM(tenantId, input) {
    logger.info({ tenantId, itemCount: input.items.length }, 'Checking PSM compliance');
    const results = [];
    const violations = [];
    for (const item of input.items) {
        const checkResult = await checkSinglePSM(tenantId, item);
        results.push(checkResult);
        if (!checkResult.approved) {
            violations.push({
                name: item.name,
                reason: checkResult.issues.join('; '),
                severity: checkResult.status === 'Withdrawn' || checkResult.status === 'Expired' ? 'Critical' : 'Major',
            });
        }
    }
    const compliant = violations.length === 0;
    await (0, publisher_1.publishEvent)('psm.checked', {
        tenantId,
        compliant,
        violationCount: violations.length,
        batchId: input.batchId,
        contractId: input.contractId,
        occurredAt: new Date().toISOString(),
    });
    if (!compliant) {
        await (0, publisher_1.publishEvent)('psm.violation', {
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
    }
    else {
        recommendation = `${violations.length} Verstöße gefunden. Nicht zugelassene PSM dürfen nicht verwendet werden.`;
    }
    return {
        compliant,
        items: results,
        violations,
        recommendation,
    };
}
async function checkSinglePSM(tenantId, item) {
    let psmRef = await getPSMFromCache(tenantId, item.bvlId || item.name);
    if (!psmRef || isCacheStale(psmRef.lastCheckedAt)) {
        logger.debug({ name: item.name, bvlId: item.bvlId }, 'Fetching PSM from BVL');
        const bvlData = await (0, bvl_api_1.fetchFromBVL)(item.bvlId || item.name);
        if (bvlData) {
            psmRef = await upsertPSMRef(tenantId, bvlData);
        }
    }
    if (!psmRef) {
        return {
            name: item.name,
            bvlId: item.bvlId ?? undefined,
            status: 'Unknown',
            approved: false,
            issues: ['PSM nicht in BVL-Datenbank gefunden'],
        };
    }
    const issues = [];
    let approved = true;
    if (psmRef.approvalStatus === 'Expired' || psmRef.approvalStatus === 'Withdrawn') {
        approved = false;
        issues.push(`Zulassung ${psmRef.approvalStatus === 'Expired' ? 'abgelaufen' : 'zurückgezogen'}`);
    }
    if (psmRef.approvalValidTo && new Date(item.useDate) > new Date(psmRef.approvalValidTo)) {
        approved = false;
        issues.push('Verwendung nach Ablauf der Zulassung');
    }
    if (item.cropOrUseCase && psmRef.usageScope && !psmRef.usageScope.includes(item.cropOrUseCase)) {
        approved = false;
        issues.push(`Nicht zugelassen für ${item.cropOrUseCase}`);
    }
    return {
        name: item.name,
        bvlId: psmRef.bvlId || undefined,
        status: psmRef.approvalStatus,
        approved,
        validUntil: psmRef.approvalValidTo?.toISOString(),
        issues,
    };
}
async function getPSMFromCache(tenantId, identifier) {
    const [result] = await connection_1.db
        .select()
        .from(schema_1.psmProductRefs)
        .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.psmProductRefs.tenantId, tenantId), (0, drizzle_orm_1.or)((0, drizzle_orm_1.eq)(schema_1.psmProductRefs.bvlId, identifier), (0, drizzle_orm_1.like)(schema_1.psmProductRefs.name, `%${identifier}%`))))
        .limit(1);
    return result || null;
}
function isCacheStale(lastCheckedAt) {
    if (!lastCheckedAt)
        return true;
    const daysSinceCheck = Math.floor((Date.now() - lastCheckedAt.getTime()) / (1000 * 60 * 60 * 24));
    return daysSinceCheck > 7;
}
async function upsertPSMRef(tenantId, bvlData) {
    const existing = await getPSMFromCache(tenantId, bvlData.bvlId || bvlData.name);
    if (existing) {
        const [updated] = await connection_1.db
            .update(schema_1.psmProductRefs)
            .set({
            ...bvlData,
            lastCheckedAt: new Date(),
            updatedAt: new Date(),
        })
            .where((0, drizzle_orm_1.eq)(schema_1.psmProductRefs.id, existing.id))
            .returning();
        return updated;
    }
    else {
        const [created] = await connection_1.db
            .insert(schema_1.psmProductRefs)
            .values({
            tenantId,
            ...bvlData,
            lastCheckedAt: new Date(),
        })
            .returning();
        return created;
    }
}
//# sourceMappingURL=psm-check-service.js.map