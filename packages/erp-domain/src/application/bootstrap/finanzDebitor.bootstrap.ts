/**
 * Bootstrap for FinanzDebitor domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */

import { Pool } from 'pg';
import { FinanzDebitorPostgresRepository } from '../../infrastructure/repositories/finanzDebitor-postgres.repository';
import { FinanzDebitorService } from '../services/finanzDebitor.service';
import { buildFinanzDebitorRouter } from '../../presentation/controllers/finanzDebitor.controller';

export interface FinanzDebitorBootstrapDependencies {
  pool: Pool;
}

export function initFinanzDebitorModule({ pool }: FinanzDebitorBootstrapDependencies): any {
  const repository = new FinanzDebitorPostgresRepository(pool);
  const service = new FinanzDebitorService(repository);
  const router = buildFinanzDebitorRouter({ service, baseRoute: '/erp/finance/debtors' });

  return { repository, service, router };
}
