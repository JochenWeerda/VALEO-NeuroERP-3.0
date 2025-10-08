/**
 * Bootstrap for FinanzKreditor domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */

import type { Router } from 'express';
import { Pool } from 'pg';
import { FinanzKreditorPostgresRepository } from '../../infrastructure/repositories/finanzKreditor-postgres.repository';
import { FinanzKreditorService } from '../services/finanzKreditor.service';
import { buildFinanzKreditorRouter } from '../../presentation/controllers/finanzKreditor.controller';

export interface FinanzKreditorBootstrapDependencies {
  pool: Pool;
}

export interface FinanzKreditorModule {
  repository: FinanzKreditorPostgresRepository;
  service: FinanzKreditorService;
  router: Router;
}

export function initFinanzKreditorModule({ pool }: FinanzKreditorBootstrapDependencies): FinanzKreditorModule {
  const repository = new FinanzKreditorPostgresRepository(pool);
  const service = new FinanzKreditorService(repository);
  const router = buildFinanzKreditorRouter({ service, baseRoute: '/erp/finance/creditors' });

  return { repository, service, router };
}
