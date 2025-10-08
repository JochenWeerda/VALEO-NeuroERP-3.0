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
        const entity = await service.findById(req.params.finanzBuchungId);
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
        const updated = await service.update(req.params.finanzBuchungId, req.body);
        res.json(updated);
    });
    router.delete(`${baseRoute}/:finanzBuchungId`, async (req, res) => {
        await service.remove(req.params.finanzBuchungId);
        res.status(HTTP_STATUS.NO_CONTENT).send();
    });
    return router;
}
//# sourceMappingURL=finanzBuchung.controller.js.map