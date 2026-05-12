/**
 * Express router for FinanzBankkonto generated via CRM toolkit.
 */

import { Request, Response, Router } from 'express';
import { FinanzBankkontoService } from '../../application/services/finanzBankkonto.service';
import {
  parseFinanzListQuery,
  jsonFinanzList,
  jsonFinanzData,
  jsonFinanzError,
} from '../utils/finanz-http';
import { resolveTenantId, respondControllerError } from '../utils/request-context';

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

  router.get(baseRoute, async (req: Request, res: Response) => {
    try {
      const tenantId = resolveTenantId(req);
      const { limit, offset } = parseFinanzListQuery(req);
      const { items, total } = await service.listPaged(tenantId, { limit, offset });
      jsonFinanzList(res, items, total, limit, offset);
    } catch (error) {
      respondControllerError(res, error, 500);
    }
  });

  router.get(`${baseRoute}/:finanzBankkontoId`, async (req: Request, res: Response) => {
    try {
      const tenantId = resolveTenantId(req);
      const id = req.params.finanzBankkontoId;
      if (id === null || id === undefined || id.trim().length === 0) {
        jsonFinanzError(res, HTTP_STATUS.BAD_REQUEST, 'finanzBankkontoId parameter is required');
        return;
      }
      const entity = await service.findById(id, tenantId);
      if (entity === undefined || entity === null) {
        jsonFinanzError(res, HTTP_STATUS.NOT_FOUND, 'FinanzBankkonto not found');
        return;
      }
      jsonFinanzData(res, entity);
    } catch (error) {
      respondControllerError(res, error, 500);
    }
  });

  router.post(baseRoute, async (req: Request, res: Response) => {
    try {
      const tenantId = resolveTenantId(req);
      const created = await service.create(tenantId, req.body);
      jsonFinanzData(res, created, HTTP_STATUS.CREATED);
    } catch (error) {
      respondControllerError(res, error, 400);
    }
  });

  router.put(`${baseRoute}/:finanzBankkontoId`, async (req: Request, res: Response) => {
    const id = req.params.finanzBankkontoId;
    if (id === null || id === undefined || id.trim().length === 0) {
      jsonFinanzError(res, HTTP_STATUS.BAD_REQUEST, 'finanzBankkontoId parameter is required');
      return;
    }
    try {
      const tenantId = resolveTenantId(req);
      const updated = await service.update(id, tenantId, req.body);
      jsonFinanzData(res, updated);
    } catch (error) {
      respondControllerError(res, error, 400);
    }
  });

  router.delete(`${baseRoute}/:finanzBankkontoId`, async (req: Request, res: Response) => {
    const id = req.params.finanzBankkontoId;
    if (id === null || id === undefined || id.trim().length === 0) {
      jsonFinanzError(res, HTTP_STATUS.BAD_REQUEST, 'finanzBankkontoId parameter is required');
      return;
    }
    try {
      const tenantId = resolveTenantId(req);
      await service.remove(id, tenantId);
      res.status(HTTP_STATUS.NO_CONTENT).send();
    } catch (error) {
      respondControllerError(res, error, 400);
    }
  });

  return router;
}
