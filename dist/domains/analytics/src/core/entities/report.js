"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createReport = createReport;
exports.applyReportUpdate = applyReportUpdate;
const data_models_1 = require("@packages/data-models");
function createReport(input) {
    if (!input.tenantId) {
        throw new Error('tenantId is required');
    }
    if (!input.name) {
        throw new Error('name is required');
    }
    if (!input.definition.metrics || input.definition.metrics.length === 0) {
        throw new Error('definition.metrics must contain at least one metric');
    }
    const now = new Date();
    return {
        id: (0, data_models_1.createReportId)(globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`),
        tenantId: input.tenantId,
        name: input.name.trim(),
        status: 'draft',
        definition: normalizeDefinition(input.definition),
        createdAt: now,
        updatedAt: now,
    };
}
function applyReportUpdate(report, update) {
    const definition = update.definition
        ? normalizeDefinition({ ...report.definition, ...update.definition })
        : report.definition;
    const next = {
        ...report,
        name: update.name ? update.name.trim() : report.name,
        status: update.status ?? report.status,
        definition,
        lastRunAt: update.lastRunAt ?? report.lastRunAt,
        lastDurationMs: update.lastDurationMs ?? report.lastDurationMs,
        updatedAt: new Date(),
    };
    return next;
}
function normalizeDefinition(definition) {
    return {
        metrics: [...new Set(definition.metrics.map((metric) => metric.trim()))],
        filters: definition.filters ? { ...definition.filters } : undefined,
        groupBy: definition.groupBy ? [...new Set(definition.groupBy)] : undefined,
        timeframe: definition.timeframe
            ? {
                start: new Date(definition.timeframe.start),
                end: new Date(definition.timeframe.end),
            }
            : undefined,
    };
}
