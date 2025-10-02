"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createDashboard = createDashboard;
exports.applyDashboardUpdate = applyDashboardUpdate;
const data_models_1 = require("@packages/data-models");
function createDashboard(input) {
    if (!input.tenantId) {
        throw new Error('tenantId is required');
    }
    if (!input.name) {
        throw new Error('name is required');
    }
    const now = new Date();
    return {
        id: (0, data_models_1.createDashboardId)(globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`),
        tenantId: input.tenantId,
        name: input.name.trim(),
        description: input.description?.trim(),
        isPublic: input.isPublic ?? false,
        widgets: sanitizeWidgets(input.widgets ?? []),
        tags: normalizeTags(input.tags),
        createdAt: now,
        updatedAt: now,
    };
}
function applyDashboardUpdate(dashboard, update) {
    return {
        ...dashboard,
        name: update.name ? update.name.trim() : dashboard.name,
        description: update.description?.trim() ?? dashboard.description,
        isPublic: update.isPublic ?? dashboard.isPublic,
        widgets: update.widgets ? sanitizeWidgets(update.widgets) : dashboard.widgets,
        tags: update.tags ? normalizeTags(update.tags) : dashboard.tags,
        updatedAt: new Date(),
    };
}
function sanitizeWidgets(widgets) {
    return widgets.map((widget) => ({
        ...widget,
        id: widget.id || `${Date.now()}-${Math.random().toString(16).slice(2)}`,
        title: widget.title.trim(),
        position: { ...widget.position },
        definition: { ...widget.definition },
    }));
}
function normalizeTags(tags) {
    return tags ? [...new Set(tags.map((tag) => tag.trim()).filter(Boolean))] : [];
}
