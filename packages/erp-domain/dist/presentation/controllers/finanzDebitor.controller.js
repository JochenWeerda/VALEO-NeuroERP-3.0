"use strict";
/**
 * Express router for FinanzDebitor generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildFinanzDebitorRouter = buildFinanzDebitorRouter;
const express_1 = require("express");
const HTTP_STATUS = {
    BAD_REQUEST: 400,
    NOT_FOUND: 404,
    CREATED: 201,
    NO_CONTENT: 204,
};
function buildFinanzDebitorRouter({ service, baseRoute = '/finanzDebitor' }) {
    const router = (0, express_1.Router)();
    router.get(baseRoute, async (_req, res) => {
        const result = await service.list();
        res.json(result);
    });
    router.get(`${baseRoute}/:finanzDebitorId`, async (req, res) => {
        const id = req.params.finanzDebitorId;
        if (id === null || id === undefined || id.trim().length === 0) {
            res.status(HTTP_STATUS.BAD_REQUEST).json({ message: 'finanzDebitorId parameter is required' });
            return;
        }
        const entity = await service.findById(id);
        if (entity === undefined || entity === null) {
            res.status(HTTP_STATUS.NOT_FOUND).json({ message: 'FinanzDebitor not found' });
            return;
        }
        res.json(entity);
    });
    router.post(baseRoute, async (req, res) => {
        const created = await service.create(req.body);
        res.status(HTTP_STATUS.CREATED).json(created);
    });
    router.put(`${baseRoute}/:finanzDebitorId`, async (req, res) => {
        const id = req.params.finanzDebitorId;
        if (id === null || id === undefined || id.trim().length === 0) {
            res.status(HTTP_STATUS.BAD_REQUEST).json({ message: 'finanzDebitorId parameter is required' });
            return;
        }
        const updated = await service.update(id, req.body);
        res.json(updated);
    });
    router.delete(`${baseRoute}/:finanzDebitorId`, async (req, res) => {
        const id = req.params.finanzDebitorId;
        if (id === null || id === undefined || id.trim().length === 0) {
            res.status(HTTP_STATUS.BAD_REQUEST).json({ message: 'finanzDebitorId parameter is required' });
            return;
        }
        await service.remove(id);
        res.status(HTTP_STATUS.NO_CONTENT).send();
    });
    return router;
}
//# sourceMappingURL=finanzDebitor.controller.js.map