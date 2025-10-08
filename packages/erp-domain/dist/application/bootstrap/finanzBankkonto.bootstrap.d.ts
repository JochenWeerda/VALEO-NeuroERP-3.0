/**
 * Bootstrap for FinanzBankkonto domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */
import type { Router } from 'express';
import { Pool } from 'pg';
import { FinanzBankkontoPostgresRepository } from '../../infrastructure/repositories/finanzBankkonto-postgres.repository';
import { FinanzBankkontoService } from '../services/finanzBankkonto.service';
export interface FinanzBankkontoBootstrapDependencies {
    pool: Pool;
}
export interface FinanzBankkontoModule {
    repository: FinanzBankkontoPostgresRepository;
    service: FinanzBankkontoService;
    router: Router;
}
export declare function initFinanzBankkontoModule({ pool }: FinanzBankkontoBootstrapDependencies): FinanzBankkontoModule;
//# sourceMappingURL=finanzBankkonto.bootstrap.d.ts.map