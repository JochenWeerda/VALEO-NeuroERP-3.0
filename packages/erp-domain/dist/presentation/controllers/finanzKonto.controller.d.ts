/**
 * Express router for FinanzKonto generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */
import { Router } from 'express';
import { FinanzKontoService } from '../../application/services/finanzKonto.service';
export interface FinanzKontoRouterDependencies {
    service: FinanzKontoService;
    baseRoute?: string;
}
export declare function buildFinanzKontoRouter({ service, baseRoute }: FinanzKontoRouterDependencies): Router;
//# sourceMappingURL=finanzKonto.controller.d.ts.map