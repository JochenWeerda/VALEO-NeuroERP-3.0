/**
 * Bootstrap for FinanzBankkonto domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */

import { Pool } from 'pg';
import { FinanzBankkontoPostgresRepository } from '../../infrastructure/repositories/finanzBankkonto-postgres.repository';
import { FinanzBankkontoService } from '../services/finanzBankkonto.service';
import { buildFinanzBankkontoRouter } from '../../presentation/controllers/finanzBankkonto.controller';

export interface FinanzBankkontoBootstrapDependencies {
  pool: Pool;
}

export function initFinanzBankkontoModule({ pool }: FinanzBankkontoBootstrapDependencies): any {
  const repository = new FinanzBankkontoPostgresRepository(pool);
  const service = new FinanzBankkontoService(repository);
  const router = buildFinanzBankkontoRouter({ service, baseRoute: '/erp/finance/bank-accounts' });

  return { repository, service, router };
}
