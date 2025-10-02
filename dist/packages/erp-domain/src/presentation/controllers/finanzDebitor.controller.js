"use strict";
/**
 * Express router for FinanzDebitor generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildFinanzDebitorRouter = buildFinanzDebitorRouter;
const express_1 = require("express");
function buildFinanzDebitorRouter({ service, baseRoute = '/finanzDebitor' }) {
    const router = (0, express_1.Router)();
    router.get(baseRoute, async (_req, res) => {
        const result = await service.list();
        res.json(result);
    });
    router.get(`${baseRoute}/:finanzDebitorId`, async (req, res) => {
        const entity = await service.findById(req.params.finanzDebitorId);
        if (!entity) {
            res.status(404).json({ message: 'FinanzDebitor not found' });
            return;
        }
        res.json(entity);
    });
    router.post(baseRoute, async (req, res) => {
        const created = await service.create(req.body);
        res.status(201).json(created);
    });
    router.put(`${baseRoute}/:finanzDebitorId`, async (req, res) => {
        const updated = await service.update(req.params.finanzDebitorId, req.body);
        res.json(updated);
    });
    router.delete(`${baseRoute}/:finanzDebitorId`, async (req, res) => {
        await service.remove(req.params.finanzDebitorId);
        res.status(204).send();
    });
    return router;
}
