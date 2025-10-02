/**
 * Express router for FinanzKonto generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */

import { Router, Request, Response } from 'express';
import { FinanzKontoService } from '../../application/services/finanzKonto.service';

export interface FinanzKontoRouterDependencies {
  service: FinanzKontoService;
  baseRoute?: string;
}

export function buildFinanzKontoRouter({ service, baseRoute = '/finanzKonto' }: FinanzKontoRouterDependencies): any {
  const router = Router();

  router.get(baseRoute, async (_req: Request, res: Response) => {
    const result = await service.list();
    res.json(result);
  });

  router.get(`${baseRoute}/:finanzKontoId`, async (req: Request, res: Response) => {
    const entity = await service.findById(req.params.finanzKontoId);
    if (!entity) {
      res.status(404).json({ message: 'FinanzKonto not found' });
      return;
    }
    res.json(entity);
  });

  router.post(baseRoute, async (req: Request, res: Response) => {
    const created = await service.create(req.body);
    res.status(201).json(created);
  });

  router.put(`${baseRoute}/:finanzKontoId`, async (req: Request, res: Response) => {
    const updated = await service.update(req.params.finanzKontoId, req.body);
    res.json(updated);
  });

  router.delete(`${baseRoute}/:finanzKontoId`, async (req: Request, res: Response) => {
    await service.remove(req.params.finanzKontoId);
    res.status(204).send();
  });

  return router;
}
