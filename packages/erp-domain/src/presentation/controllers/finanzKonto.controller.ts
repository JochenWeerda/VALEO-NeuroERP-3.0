/**
 * Express router for FinanzKonto generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */

import { Request, Response, Router } from 'express';
import { FinanzKontoService } from '../../application/services/finanzKonto.service';

const HTTP_STATUS = {
  NOT_FOUND: 404,
  CREATED: 201,
  NO_CONTENT: 204,
} as const;

export interface FinanzKontoRouterDependencies {
  service: FinanzKontoService;
  baseRoute?: string;
}

export function buildFinanzKontoRouter(
  { service, baseRoute = '/finanzKonto' }: FinanzKontoRouterDependencies,
): Router {
  const router = Router();

  router.get(baseRoute, async (_req: Request, res: Response) => {
    const result = await service.list();
    res.json(result);
  });

  router.get(`${baseRoute}/:finanzKontoId`, async (req: Request, res: Response) => {
    const entity = await service.findById(req.params.finanzKontoId);
    if (entity === undefined || entity === null) {
      res.status(HTTP_STATUS.NOT_FOUND).json({ message: 'FinanzKonto not found' });
      return;
    }
    res.json(entity);
  });

  router.post(baseRoute, async (req: Request, res: Response) => {
    const created = await service.create(req.body);
    res.status(HTTP_STATUS.CREATED).json(created);
  });

  router.put(`${baseRoute}/:finanzKontoId`, async (req: Request, res: Response) => {
    const updated = await service.update(req.params.finanzKontoId, req.body);
    res.json(updated);
  });

  router.delete(`${baseRoute}/:finanzKontoId`, async (req: Request, res: Response) => {
    await service.remove(req.params.finanzKontoId);
    res.status(HTTP_STATUS.NO_CONTENT).send();
  });

  return router;
}

