/**
 * Express router for FinanzKreditor generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */

import { Router, Request, Response } from 'express';
import { FinanzKreditorService } from '../../application/services/finanzKreditor.service';

export interface FinanzKreditorRouterDependencies {
  service: FinanzKreditorService;
  baseRoute?: string;
}

export function buildFinanzKreditorRouter({ service, baseRoute = '/finanzKreditor' }: FinanzKreditorRouterDependencies): any {
  const router = Router();

  router.get(baseRoute, async (_req: Request, res: Response) => {
    const result = await service.list();
    res.json(result);
  });

  router.get(`${baseRoute}/:finanzKreditorId`, async (req: Request, res: Response) => {
    const entity = await service.findById(req.params.finanzKreditorId);
    if (!entity) {
      res.status(404).json({ message: 'FinanzKreditor not found' });
      return;
    }
    res.json(entity);
  });

  router.post(baseRoute, async (req: Request, res: Response) => {
    const created = await service.create(req.body);
    res.status(201).json(created);
  });

  router.put(`${baseRoute}/:finanzKreditorId`, async (req: Request, res: Response) => {
    const updated = await service.update(req.params.finanzKreditorId, req.body);
    res.json(updated);
  });

  router.delete(`${baseRoute}/:finanzKreditorId`, async (req: Request, res: Response) => {
    await service.remove(req.params.finanzKreditorId);
    res.status(204).send();
  });

  return router;
}
