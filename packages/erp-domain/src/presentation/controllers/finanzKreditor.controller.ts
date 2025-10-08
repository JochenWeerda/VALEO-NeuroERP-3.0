/**
 * Express router for FinanzKreditor generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */

import { Request, Response, Router } from 'express';
import { FinanzKreditorService } from '../../application/services/finanzKreditor.service';

const HTTP_STATUS = {
  NOT_FOUND: 404,
  CREATED: 201,
  NO_CONTENT: 204,
} as const;

export interface FinanzKreditorRouterDependencies {
  service: FinanzKreditorService;
  baseRoute?: string;
}

export function buildFinanzKreditorRouter(
  { service, baseRoute = '/finanzKreditor' }: FinanzKreditorRouterDependencies,
): Router {
  const router = Router();

  router.get(baseRoute, async (_req: Request, res: Response) => {
    const result = await service.list();
    res.json(result);
  });

  router.get(`${baseRoute}/:finanzKreditorId`, async (req: Request, res: Response) => {
    const entity = await service.findById(req.params.finanzKreditorId);
    if (entity === undefined || entity === null) {
      res.status(HTTP_STATUS.NOT_FOUND).json({ message: 'FinanzKreditor not found' });
      return;
    }
    res.json(entity);
  });

  router.post(baseRoute, async (req: Request, res: Response) => {
    const created = await service.create(req.body);
    res.status(HTTP_STATUS.CREATED).json(created);
  });

  router.put(`${baseRoute}/:finanzKreditorId`, async (req: Request, res: Response) => {
    const updated = await service.update(req.params.finanzKreditorId, req.body);
    res.json(updated);
  });

  router.delete(`${baseRoute}/:finanzKreditorId`, async (req: Request, res: Response) => {
    await service.remove(req.params.finanzKreditorId);
    res.status(HTTP_STATUS.NO_CONTENT).send();
  });

  return router;
}

