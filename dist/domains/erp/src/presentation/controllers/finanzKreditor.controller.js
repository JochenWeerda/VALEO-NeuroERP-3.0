"use strict";
/**
 * Express router for FinanzKreditor generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildFinanzKreditorRouter = buildFinanzKreditorRouter;
const express_1 = require("express");
function buildFinanzKreditorRouter({ service, baseRoute = '/finanzKreditor' }) {
    const router = (0, express_1.Router)();
    router.get(baseRoute, async (_req, res) => {
        const result = await service.list();
        res.json(result);
    });
    router.get(`${baseRoute}/:finanzKreditorId`, async (req, res) => {
        const entity = await service.findById(req.params.finanzKreditorId);
        if (!entity) {
            res.status(404).json({ message: 'FinanzKreditor not found' });
            return;
        }
        res.json(entity);
    });
    router.post(baseRoute, async (req, res) => {
        const created = await service.create(req.body);
        res.status(201).json(created);
    });
    router.put(`${baseRoute}/:finanzKreditorId`, async (req, res) => {
        const updated = await service.update(req.params.finanzKreditorId, req.body);
        res.json(updated);
    });
    router.delete(`${baseRoute}/:finanzKreditorId`, async (req, res) => {
        await service.remove(req.params.finanzKreditorId);
        res.status(204).send();
    });
    return router;
}
