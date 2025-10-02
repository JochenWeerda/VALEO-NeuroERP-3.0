"use strict";
/**
 * Express router for FinanzKonto generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildFinanzKontoRouter = buildFinanzKontoRouter;
const express_1 = require("express");
function buildFinanzKontoRouter({ service, baseRoute = '/finanzKonto' }) {
    const router = (0, express_1.Router)();
    router.get(baseRoute, async (_req, res) => {
        const result = await service.list();
        res.json(result);
    });
    router.get(`${baseRoute}/:finanzKontoId`, async (req, res) => {
        const entity = await service.findById(req.params.finanzKontoId);
        if (!entity) {
            res.status(404).json({ message: 'FinanzKonto not found' });
            return;
        }
        res.json(entity);
    });
    router.post(baseRoute, async (req, res) => {
        const created = await service.create(req.body);
        res.status(201).json(created);
    });
    router.put(`${baseRoute}/:finanzKontoId`, async (req, res) => {
        const updated = await service.update(req.params.finanzKontoId, req.body);
        res.json(updated);
    });
    router.delete(`${baseRoute}/:finanzKontoId`, async (req, res) => {
        await service.remove(req.params.finanzKontoId);
        res.status(204).send();
    });
    return router;
}
