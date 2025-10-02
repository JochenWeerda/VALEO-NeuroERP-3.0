/**
 * Bootstrap for FinanzBuchung domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */

import { Pool } from 'pg';
import { FinanzBuchungPostgresRepository } from '../../infrastructure/repositories/finanzBuchung-postgres.repository';
import { FinanzBuchungService } from '../services/finanzBuchung.service';
import { buildFinanzBuchungRouter } from '../../presentation/controllers/finanzBuchung.controller';

export interface FinanzBuchungBootstrapDependencies {
  pool: Pool;
}

export function initFinanzBuchungModule({ pool }: FinanzBuchungBootstrapDependencies): any {
  const repository = new FinanzBuchungPostgresRepository(pool);
  const service = new FinanzBuchungService(repository);
  const router = buildFinanzBuchungRouter({ service, baseRoute: '/erp/finance/bookings' });

  return { repository, service, router };
}
