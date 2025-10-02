"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AnalyticsApiController = void 0;
const data_models_1 = require("@packages/data-models");
class AnalyticsApiController {
    service;
    constructor(service) {
        this.service = service;
    }
    register(router) {
        router.get('/analytics/reports', (request) => this.handleListReports(request));
        router.post('/analytics/reports', (request) => this.handleCreateReport(request));
        router.put('/analytics/reports/:id', (request) => this.handleUpdateReport(request));
        router.get('/analytics/dashboards', (request) => this.handleListDashboards(request));
        router.get('/analytics/dashboards/public', (request) => this.handleListPublicDashboards(request));
        router.post('/analytics/dashboards', (request) => this.handleCreateDashboard(request));
        router.put('/analytics/dashboards/:id', (request) => this.handleUpdateDashboard(request));
    }
    async handleListReports(request) {
        const tenantId = asString(request.query.tenantId);
        if (!tenantId) {
            return { status: 400, body: { message: 'tenantId query parameter is required' } };
        }
        const reports = await this.service.listReports(tenantId);
        return { status: 200, body: reports };
    }
    async handleCreateReport(request) {
        const body = request.body;
        if (!body) {
            return { status: 400, body: { message: 'Request body is required' } };
        }
        try {
            const created = await this.service.createReport(body);
            return { status: 201, body: created };
        }
        catch (error) {
            return toHttpError(error);
        }
    }
    async handleUpdateReport(request) {
        const id = request.params.id;
        if (!id) {
            return { status: 400, body: { message: 'Report id missing' } };
        }
        const body = request.body;
        if (!body) {
            return { status: 400, body: { message: 'Request body is required' } };
        }
        try {
            const updated = await this.service.updateReport((0, data_models_1.createReportId)(id), body);
            return { status: 200, body: updated };
        }
        catch (error) {
            return toHttpError(error);
        }
    }
    async handleListDashboards(request) {
        const tenantId = asString(request.query.tenantId);
        if (!tenantId) {
            return { status: 400, body: { message: 'tenantId query parameter is required' } };
        }
        const dashboards = await this.service.listDashboards(tenantId);
        return { status: 200, body: dashboards };
    }
    async handleListPublicDashboards(request) {
        const tenantId = asString(request.query.tenantId);
        if (!tenantId) {
            return { status: 400, body: { message: 'tenantId query parameter is required' } };
        }
        const dashboards = await this.service.listPublicDashboards(tenantId);
        return { status: 200, body: dashboards };
    }
    async handleCreateDashboard(request) {
        const body = request.body;
        if (!body) {
            return { status: 400, body: { message: 'Request body is required' } };
        }
        try {
            const created = await this.service.createDashboard(body);
            return { status: 201, body: created };
        }
        catch (error) {
            return toHttpError(error);
        }
    }
    async handleUpdateDashboard(request) {
        const id = request.params.id;
        if (!id) {
            return { status: 400, body: { message: 'Dashboard id missing' } };
        }
        const body = request.body;
        if (!body) {
            return { status: 400, body: { message: 'Request body is required' } };
        }
        try {
            const updated = await this.service.updateDashboard((0, data_models_1.createDashboardId)(id), body);
            return { status: 200, body: updated };
        }
        catch (error) {
            return toHttpError(error);
        }
    }
}
exports.AnalyticsApiController = AnalyticsApiController;
function asString(value) {
    if (Array.isArray(value)) {
        return value[0];
    }
    return value;
}
function toHttpError(error) {
    if (error instanceof Error) {
        const message = error.message;
        if (message.toLowerCase().includes('not found')) {
            return { status: 404, body: { message } };
        }
        return { status: 400, body: { message } };
    }
    return { status: 500, body: { message: 'Unknown error' } };
}
