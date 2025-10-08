/**
 * Express router for FinanzDebitor generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */

import { Request, Response, Router } from 'express';
import { FinanzDebitorService } from '../../application/services/finanzDebitor.service';

const HTTP_STATUS = {
  NOT_FOUND: 404,
  CREATED: 201,
  NO_CONTENT: 204,
} as const;

export interface FinanzDebitorRouterDependencies {
  service: FinanzDebitorService;
  baseRoute?: string;
}

export function buildFinanzDebitorRouter(
  { service, baseRoute = '/finanzDebitor' }: FinanzDebitorRouterDependencies,
): Router {
  const router = Router();

  router.get(baseRoute, async (_req: Request, res: Response) => {
    const result = await service.list();
    res.json(result);
  });

  router.get(`${baseRoute}/:finanzDebitorId`, async (req: Request, res: Response) => {
    const entity = await service.findById(req.params.finanzDebitorId);
    if (entity === undefined || entity === null) {
      res.status(HTTP_STATUS.NOT_FOUND).json({ message: 'FinanzDebitor not found' });
      return;
    }
    res.json(entity);
  });

  router.post(baseRoute, async (req: Request, res: Response) => {
    const created = await service.create(req.body);
    res.status(HTTP_STATUS.CREATED).json(created);
  });

  router.put(`${baseRoute}/:finanzDebitorId`, async (req: Request, res: Response) => {
    const updated = await service.update(req.params.finanzDebitorId, req.body);
    res.json(updated);
  });

  router.delete(`${baseRoute}/:finanzDebitorId`, async (req: Request, res: Response) => {
    await service.remove(req.params.finanzDebitorId);
    res.status(HTTP_STATUS.NO_CONTENT).send();
  });

  return router;
}

