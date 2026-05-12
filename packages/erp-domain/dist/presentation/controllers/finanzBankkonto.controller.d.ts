/**
 * Express router for FinanzBankkonto generated via CRM toolkit.
 */
import { Router } from 'express';
import { FinanzBankkontoService } from '../../application/services/finanzBankkonto.service';
export interface FinanzBankkontoRouterDependencies {
    service: FinanzBankkontoService;
    baseRoute?: string;
}
export declare function buildFinanzBankkontoRouter({ service, baseRoute }: FinanzBankkontoRouterDependencies): Router;
//# sourceMappingURL=finanzBankkonto.controller.d.ts.map