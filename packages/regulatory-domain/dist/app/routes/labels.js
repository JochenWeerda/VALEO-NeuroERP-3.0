"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerLabelRoutes = registerLabelRoutes;
const label_1 = require("../../domain/entities/label");
const label_evaluation_service_1 = require("../../domain/services/label-evaluation-service");
const connection_1 = require("../../infra/db/connection");
const schema_1 = require("../../infra/db/schema");
const drizzle_orm_1 = require("drizzle-orm");
async function registerLabelRoutes(server) {
    server.post('/labels/evaluate', async (request, reply) => {
        const tenantId = request.headers['x-tenant-id'];
        const userId = request.authContext?.userId || 'system';
        const input = label_1.LabelEvaluateInputSchema.parse({ ...request.body, tenantId });
        const evaluation = await (0, label_evaluation_service_1.evaluateLabel)(tenantId, input);
        if (request.query && request.query.persist === 'true') {
            const label = await (0, label_evaluation_service_1.createOrUpdateLabel)(tenantId, input, evaluation, userId);
            reply.send({ evaluation, label });
        }
        else {
            reply.send(evaluation);
        }
    });
    server.get('/labels/:id', async (request, reply) => {
        const tenantId = request.headers['x-tenant-id'];
        const { id } = request.params;
        const [label] = await connection_1.db
            .select()
            .from(schema_1.labels)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.labels.id, id), (0, drizzle_orm_1.eq)(schema_1.labels.tenantId, tenantId)))
            .limit(1);
        if (!label) {
            reply.code(404).send({ error: 'NotFound', message: 'Label not found' });
            return;
        }
        reply.send(label);
    });
    server.get('/labels', async (request, reply) => {
        const tenantId = request.headers['x-tenant-id'];
        const query = request.query;
        let dbQuery = connection_1.db.select().from(schema_1.labels).where((0, drizzle_orm_1.eq)(schema_1.labels.tenantId, tenantId));
        const results = await dbQuery;
        let filtered = results;
        if (query.targetType && query.targetId) {
            filtered = filtered.filter((l) => l.targetType === query.targetType && l.targetId === query.targetId);
        }
        if (query.code) {
            filtered = filtered.filter((l) => l.code === query.code);
        }
        if (query.status) {
            filtered = filtered.filter((l) => l.status === query.status);
        }
        reply.send({ data: filtered, count: filtered.length });
    });
    server.post('/labels/:id/revoke', async (request, reply) => {
        const tenantId = request.headers['x-tenant-id'];
        const userId = request.authContext?.userId || 'system';
        const { id } = request.params;
        const { reason } = request.body;
        const [revoked] = await connection_1.db
            .update(schema_1.labels)
            .set({
            status: 'Ineligible',
            revokedAt: new Date(),
            revokedBy: userId,
            revokedReason: reason,
            updatedAt: new Date(),
        })
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.labels.id, id), (0, drizzle_orm_1.eq)(schema_1.labels.tenantId, tenantId)))
            .returning();
        if (!revoked) {
            reply.code(404).send({ error: 'NotFound', message: 'Label not found' });
            return;
        }
        reply.send(revoked);
    });
}
//# sourceMappingURL=labels.js.map