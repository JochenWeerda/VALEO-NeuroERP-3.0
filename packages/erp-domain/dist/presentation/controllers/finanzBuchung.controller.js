"use strict";
/**
 * Express router for FinanzBuchung generated via CRM toolkit.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildFinanzBuchungRouter = buildFinanzBuchungRouter;
const express_1 = require("express");
const finanz_http_1 = require("../utils/finanz-http");
const request_context_1 = require("../utils/request-context");
const HTTP_STATUS = {
    BAD_REQUEST: 400,
    NOT_FOUND: 404,
    CREATED: 201,
    NO_CONTENT: 204,
};
function buildFinanzBuchungRouter({ service, baseRoute = '/finanzBuchung' }) {
    const router = (0, express_1.Router)();
    router.get(baseRoute, async (req, res) => {
        try {
            const tenantId = (0, request_context_1.resolveTenantId)(req);
            const { limit, offset } = (0, finanz_http_1.parseFinanzListQuery)(req);
            const { items, total } = await service.listPaged(tenantId, { limit, offset });
            (0, finanz_http_1.jsonFinanzList)(res, items, total, limit, offset);
        }
        catch (error) {
            (0, request_context_1.respondControllerError)(res, error, 500);
        }
    });
    router.get(`${baseRoute}/:finanzBuchungId`, async (req, res) => {
        try {
            const tenantId = (0, request_context_1.resolveTenantId)(req);
            const id = req.params.finanzBuchungId;
            if (id === null || id === undefined || id.trim().length === 0) {
                (0, finanz_http_1.jsonFinanzError)(res, HTTP_STATUS.BAD_REQUEST, 'finanzBuchungId parameter is required');
                return;
            }
            const entity = await service.findById(id, tenantId);
            if (entity === undefined || entity === null) {
                (0, finanz_http_1.jsonFinanzError)(res, HTTP_STATUS.NOT_FOUND, 'FinanzBuchung not found');
                return;
            }
            (0, finanz_http_1.jsonFinanzData)(res, entity);
        }
        catch (error) {
            (0, request_context_1.respondControllerError)(res, error, 500);
        }
    });
    router.post(baseRoute, async (req, res) => {
        try {
            const tenantId = (0, request_context_1.resolveTenantId)(req);
            const created = await service.create(tenantId, req.body);
            (0, finanz_http_1.jsonFinanzData)(res, created, HTTP_STATUS.CREATED);
        }
        catch (error) {
            (0, request_context_1.respondControllerError)(res, error, 400);
        }
    });
    router.put(`${baseRoute}/:finanzBuchungId`, async (req, res) => {
        const id = req.params.finanzBuchungId;
        if (id === null || id === undefined || id.trim().length === 0) {
            (0, finanz_http_1.jsonFinanzError)(res, HTTP_STATUS.BAD_REQUEST, 'finanzBuchungId parameter is required');
            return;
        }
        try {
            const tenantId = (0, request_context_1.resolveTenantId)(req);
            const updated = await service.update(id, tenantId, req.body);
            (0, finanz_http_1.jsonFinanzData)(res, updated);
        }
        catch (error) {
            (0, request_context_1.respondControllerError)(res, error, 400);
        }
    });
    router.delete(`${baseRoute}/:finanzBuchungId`, async (req, res) => {
        const id = req.params.finanzBuchungId;
        if (id === null || id === undefined || id.trim().length === 0) {
            (0, finanz_http_1.jsonFinanzError)(res, HTTP_STATUS.BAD_REQUEST, 'finanzBuchungId parameter is required');
            return;
        }
        try {
            const tenantId = (0, request_context_1.resolveTenantId)(req);
            await service.remove(id, tenantId);
            res.status(HTTP_STATUS.NO_CONTENT).send();
        }
        catch (error) {
            (0, request_context_1.respondControllerError)(res, error, 400);
        }
    });
    return router;
}
//# sourceMappingURL=finanzBuchung.controller.js.map