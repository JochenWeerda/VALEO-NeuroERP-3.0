/**
 * Bootstrap for FinanzKonto domain slice generated via CRM toolkit.
 * Exposes a lightweight initializer returning repository/service/router trio.
 */
import type { Router } from 'express';
import { Pool } from 'pg';
import { FinanzKontoPostgresRepository } from '../../infrastructure/repositories/finanzKonto-postgres.repository';
import { FinanzKontoService } from '../services/finanzKonto.service';
export interface FinanzKontoBootstrapDependencies {
    pool: Pool;
}
export interface FinanzKontoModule {
    repository: FinanzKontoPostgresRepository;
    service: FinanzKontoService;
    router: Router;
}
export declare function initFinanzKontoModule({ pool }: FinanzKontoBootstrapDependencies): FinanzKontoModule;
//# sourceMappingURL=finanzKonto.bootstrap.d.ts.map