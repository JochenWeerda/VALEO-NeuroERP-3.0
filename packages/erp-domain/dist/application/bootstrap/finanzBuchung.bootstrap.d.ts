/**
 * Bootstrap for FinanzBuchung domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */
import type { Router } from 'express';
import { Pool } from 'pg';
import { FinanzBuchungPostgresRepository } from '../../infrastructure/repositories/finanzBuchung-postgres.repository';
import { FinanzBuchungService } from '../services/finanzBuchung.service';
export interface FinanzBuchungBootstrapDependencies {
    pool: Pool;
}
export interface FinanzBuchungModule {
    repository: FinanzBuchungPostgresRepository;
    service: FinanzBuchungService;
    router: Router;
}
export declare function initFinanzBuchungModule({ pool }: FinanzBuchungBootstrapDependencies): FinanzBuchungModule;
//# sourceMappingURL=finanzBuchung.bootstrap.d.ts.map