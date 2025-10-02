/**
 * Express router for FinanzBankkonto generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */
import { FinanzBankkontoService } from '../../application/services/finanzBankkonto.service';
export interface FinanzBankkontoRouterDependencies {
    service: FinanzBankkontoService;
    baseRoute?: string;
}
export declare function buildFinanzBankkontoRouter({ service, baseRoute }: FinanzBankkontoRouterDependencies): any;
//# sourceMappingURL=finanzBankkonto.controller.d.ts.map