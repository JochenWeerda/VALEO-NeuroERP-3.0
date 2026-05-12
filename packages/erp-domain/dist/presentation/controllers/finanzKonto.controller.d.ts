/**
 * Express router for FinanzKonto generated via CRM toolkit.
 */
import { Router } from 'express';
import { FinanzKontoService } from '../../application/services/finanzKonto.service';
export interface FinanzKontoRouterDependencies {
    service: FinanzKontoService;
    baseRoute?: string;
}
export declare function buildFinanzKontoRouter({ service, baseRoute }: FinanzKontoRouterDependencies): Router;
//# sourceMappingURL=finanzKonto.controller.d.ts.map