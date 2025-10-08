/**
 * Bootstrap for FinanzDebitor domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */

import type { Router } from 'express';
import { Pool } from 'pg';
import { FinanzDebitorPostgresRepository } from '../../infrastructure/repositories/finanzDebitor-postgres.repository';
import { FinanzDebitorService } from '../services/finanzDebitor.service';
import { buildFinanzDebitorRouter } from '../../presentation/controllers/finanzDebitor.controller';

export interface FinanzDebitorBootstrapDependencies {
  pool: Pool;
}

export interface FinanzDebitorModule {
  repository: FinanzDebitorPostgresRepository;
  service: FinanzDebitorService;
  router: Router;
}

export function initFinanzDebitorModule({ pool }: FinanzDebitorBootstrapDependencies): FinanzDebitorModule {
  const repository = new FinanzDebitorPostgresRepository(pool);
  const service = new FinanzDebitorService(repository);
  const router = buildFinanzDebitorRouter({ service, baseRoute: '/erp/finance/debtors' });

  return { repository, service, router };
}
