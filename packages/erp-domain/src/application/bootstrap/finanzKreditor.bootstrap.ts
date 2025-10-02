/**
 * Bootstrap for FinanzKreditor domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */

import { Pool } from 'pg';
import { FinanzKreditorPostgresRepository } from '../../infrastructure/repositories/finanzKreditor-postgres.repository';
import { FinanzKreditorService } from '../services/finanzKreditor.service';
import { buildFinanzKreditorRouter } from '../../presentation/controllers/finanzKreditor.controller';

export interface FinanzKreditorBootstrapDependencies {
  pool: Pool;
}

export function initFinanzKreditorModule({ pool }: FinanzKreditorBootstrapDependencies): any {
  const repository = new FinanzKreditorPostgresRepository(pool);
  const service = new FinanzKreditorService(repository);
  const router = buildFinanzKreditorRouter({ service, baseRoute: '/erp/finance/creditors' });

  return { repository, service, router };
}
