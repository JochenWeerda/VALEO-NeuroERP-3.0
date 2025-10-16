/**
 * Express router for FinanzBankkonto generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */

import { Request, Response, Router } from 'express';
import { FinanzBankkontoService } from '../../application/services/finanzBankkonto.service';

const HTTP_STATUS = {
  BAD_REQUEST: 400,
  NOT_FOUND: 404,
  CREATED: 201,
  NO_CONTENT: 204,
} as const;

export interface FinanzBankkontoRouterDependencies {
  service: FinanzBankkontoService;
  baseRoute?: string;
}

export function buildFinanzBankkontoRouter(
  { service, baseRoute = '/finanzBankkonto' }: FinanzBankkontoRouterDependencies,
): Router {
  const router = Router();

  router.get(baseRoute, async (_req: Request, res: Response) => {
    const result = await service.list();
    res.json(result);
  });

  router.get(`${baseRoute}/:finanzBankkontoId`, async (req: Request, res: Response) => {
    const id = req.params.finanzBankkontoId;
    if (id === undefined || id === null) {
      res.status(HTTP_STATUS.BAD_REQUEST).json({ message: 'Missing finanzBankkontoId' });
      return;
    }
    const entity = await service.findById(id);
    if (entity === undefined || entity === null) {
      res.status(HTTP_STATUS.NOT_FOUND).json({ message: 'FinanzBankkonto not found' });
      return;
    }
    res.json(entity);
  });

  router.post(baseRoute, async (req: Request, res: Response) => {
    const created = await service.create(req.body);
    res.status(HTTP_STATUS.CREATED).json(created);
  });

  router.put(`${baseRoute}/:finanzBankkontoId`, async (req: Request, res: Response) => {
    const id = req.params.finanzBankkontoId;
    if (id === undefined || id === null) {
      res.status(HTTP_STATUS.BAD_REQUEST).json({ message: 'Missing finanzBankkontoId' });
      return;
    }
    const updated = await service.update(id, req.body);
    res.json(updated);
  });

  router.delete(`${baseRoute}/:finanzBankkontoId`, async (req: Request, res: Response) => {
    const id = req.params.finanzBankkontoId;
    if (id === undefined || id === null) {
      res.status(HTTP_STATUS.BAD_REQUEST).json({ message: 'Missing finanzBankkontoId' });
      return;
    }
    await service.remove(id);
    res.status(HTTP_STATUS.NO_CONTENT).send();
  });

  return router;
}


