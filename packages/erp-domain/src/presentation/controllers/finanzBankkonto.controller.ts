/**
 * Express router for FinanzBankkonto generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */

import { Router, Request, Response } from 'express';
import { FinanzBankkontoService } from '../../application/services/finanzBankkonto.service';

export interface FinanzBankkontoRouterDependencies {
  service: FinanzBankkontoService;
  baseRoute?: string;
}

export function buildFinanzBankkontoRouter({ service, baseRoute = '/finanzBankkonto' }: FinanzBankkontoRouterDependencies): any {
  const router = Router();

  router.get(baseRoute, async (_req: Request, res: Response) => {
    const result = await service.list();
    res.json(result);
  });

  router.get(`${baseRoute}/:finanzBankkontoId`, async (req: Request, res: Response) => {
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

  router.post(baseRoute, async (req: Request, res: Response) => {
    const created = await service.create(req.body);
    res.status(201).json(created);
  });

  router.put(`${baseRoute}/:finanzBankkontoId`, async (req: Request, res: Response) => {
    const id = req.params.finanzBankkontoId;
    if (!id) {
      res.status(400).json({ message: 'Missing finanzBankkontoId' });
      return;
    }
    const updated = await service.update(id, req.body);
    res.json(updated);
  });

  router.delete(`${baseRoute}/:finanzBankkontoId`, async (req: Request, res: Response) => {
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
