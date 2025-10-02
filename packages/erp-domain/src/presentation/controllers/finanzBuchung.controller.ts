/**
 * Express router for FinanzBuchung generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */

import { Router, Request, Response } from 'express';
import { FinanzBuchungService } from '../../application/services/finanzBuchung.service';

export interface FinanzBuchungRouterDependencies {
  service: FinanzBuchungService;
  baseRoute?: string;
}

export function buildFinanzBuchungRouter({ service, baseRoute = '/finanzBuchung' }: FinanzBuchungRouterDependencies): any {
  const router = Router();

  router.get(baseRoute, async (_req: Request, res: Response) => {
    const result = await service.list();
    res.json(result);
  });

  router.get(`${baseRoute}/:finanzBuchungId`, async (req: Request, res: Response) => {
    const entity = await service.findById(req.params.finanzBuchungId);
    if (!entity) {
      res.status(404).json({ message: 'FinanzBuchung not found' });
      return;
    }
    res.json(entity);
  });

  router.post(baseRoute, async (req: Request, res: Response) => {
    const created = await service.create(req.body);
    res.status(201).json(created);
  });

  router.put(`${baseRoute}/:finanzBuchungId`, async (req: Request, res: Response) => {
    const updated = await service.update(req.params.finanzBuchungId, req.body);
    res.json(updated);
  });

  router.delete(`${baseRoute}/:finanzBuchungId`, async (req: Request, res: Response) => {
    await service.remove(req.params.finanzBuchungId);
    res.status(204).send();
  });

  return router;
}
