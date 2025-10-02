/**
 * Express router for FinanzDebitor generated via CRM toolkit.
 * Provides baseline CRUD endpoints; extend with domain-specific routes.
 */
import { FinanzDebitorService } from '../../application/services/finanzDebitor.service';
export interface FinanzDebitorRouterDependencies {
    service: FinanzDebitorService;
    baseRoute?: string;
}
export declare function buildFinanzDebitorRouter({ service, baseRoute }: FinanzDebitorRouterDependencies): any;
//# sourceMappingURL=finanzDebitor.controller.d.ts.map