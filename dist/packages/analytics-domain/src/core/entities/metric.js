"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.recordMetric = recordMetric;
const data_models_1 = require("@packages/data-models");
function recordMetric(input) {
    if (!input.tenantId) {
        throw new Error('tenantId is required');
    }
    if (!input.name) {
        throw new Error('name is required');
    }
    if (!Number.isFinite(input.value)) {
        throw new Error('value must be a finite number');
    }
    return {
        id: (0, data_models_1.createId)('MetricId'),
        tenantId: input.tenantId,
        name: input.name,
        value: input.value,
        type: input.type ?? 'gauge',
        unit: input.unit,
        dimensions: input.dimensions ? { ...input.dimensions } : {},
        recordedAt: input.recordedAt ? new Date(input.recordedAt) : new Date(),
    };
}
