"use strict";
/**
 * Express router for FinanzBuchung generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildFinanzBuchungRouter = buildFinanzBuchungRouter;
const express_1 = require("express");
const HTTP_STATUS = {
    NOT_FOUND: 404,
    CREATED: 201,
    NO_CONTENT: 204,
};
function buildFinanzBuchungRouter({ service, baseRoute = '/finanzBuchung' }) {
    const router = (0, express_1.Router)();
    router.get(baseRoute, async (_req, res) => {
        const result = await service.list();
        res.json(result);
    });
    router.get(`${baseRoute}/:finanzBuchungId`, async (req, res) => {
        const id = req.params.finanzBuchungId;
        if (!id) {
            res.status(400).json({ message: 'finanzBuchungId parameter is required' });
            return;
        }
        const entity = await service.findById(id);
        if (entity === undefined || entity === null) {
            res.status(HTTP_STATUS.NOT_FOUND).json({ message: 'FinanzBuchung not found' });
            return;
        }
        res.json(entity);
    });
    router.post(baseRoute, async (req, res) => {
        const created = await service.create(req.body);
        res.status(HTTP_STATUS.CREATED).json(created);
    });
    router.put(`${baseRoute}/:finanzBuchungId`, async (req, res) => {
        const id = req.params.finanzBuchungId;
        if (!id) {
            res.status(400).json({ message: 'finanzBuchungId parameter is required' });
            return;
        }
        const updated = await service.update(id, req.body);
        res.json(updated);
    });
    router.delete(`${baseRoute}/:finanzBuchungId`, async (req, res) => {
        const id = req.params.finanzBuchungId;
        if (!id) {
            res.status(400).json({ message: 'finanzBuchungId parameter is required' });
            return;
        }
        await service.remove(id);
        res.status(HTTP_STATUS.NO_CONTENT).send();
    });
    return router;
}
//# sourceMappingURL=finanzBuchung.controller.js.map