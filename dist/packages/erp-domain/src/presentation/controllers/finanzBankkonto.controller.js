"use strict";
/**
 * Express router for FinanzBankkonto generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildFinanzBankkontoRouter = buildFinanzBankkontoRouter;
const express_1 = require("express");
function buildFinanzBankkontoRouter({ service, baseRoute = '/finanzBankkonto' }) {
    const router = (0, express_1.Router)();
    router.get(baseRoute, async (_req, res) => {
        const result = await service.list();
        res.json(result);
    });
    router.get(`${baseRoute}/:finanzBankkontoId`, async (req, res) => {
        const id = req.params.finanzBankkontoId;
        if (!id) {
            res.status(400).json({ message: 'Missing finanzBankkontoId' });
            return;
        }
        const entity = await service.findById(id);
        if (!entity) {
            res.status(404).json({ message: 'FinanzBankkonto not found' });
            return;
        }
        res.json(entity);
    });
    router.post(baseRoute, async (req, res) => {
        const created = await service.create(req.body);
        res.status(201).json(created);
    });
    router.put(`${baseRoute}/:finanzBankkontoId`, async (req, res) => {
        const id = req.params.finanzBankkontoId;
        if (!id) {
            res.status(400).json({ message: 'Missing finanzBankkontoId' });
            return;
        }
        const updated = await service.update(id, req.body);
        res.json(updated);
    });
    router.delete(`${baseRoute}/:finanzBankkontoId`, async (req, res) => {
        const id = req.params.finanzBankkontoId;
        if (!id) {
            res.status(400).json({ message: 'Missing finanzBankkontoId' });
            return;
        }
        await service.remove(id);
        res.status(204).send();
    });
    return router;
}
