/**
 * Bootstrap for FinanzKonto domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */

import { Pool } from 'pg';
import { FinanzKontoPostgresRepository } from '../../infrastructure/repositories/finanzKonto-postgres.repository';
import { FinanzKontoService } from '../services/finanzKonto.service';
import { buildFinanzKontoRouter } from '../../presentation/controllers/finanzKonto.controller';

export interface FinanzKontoBootstrapDependencies {
  pool: Pool;
}

export function initFinanzKontoModule({ pool }: FinanzKontoBootstrapDependencies): any {
  const repository = new FinanzKontoPostgresRepository(pool);
  const service = new FinanzKontoService(repository);
  const router = buildFinanzKontoRouter({ service, baseRoute: '/erp/finance/accounts' });

  return { repository, service, router };
}
