import { ServiceLocator } from "@valero-neuroerp/utilities";
import { OrderRepository } from './core/repositories/order-repository';
import { OrderDomainService } from './core/domain-services/order-domain-service';
import { ERPApiController } from './presentation/controllers/erp-api-controller';
import type { CreateOrderInput } from './core/entities/order';
export interface ErpBootstrapOptions {
    locator?: ServiceLocator;
    repository?: OrderRepository;
    seed?: CreateOrderInput[];
}
export declare function registerErpDomain(options?: ErpBootstrapOptions): ServiceLocator;
export declare const resolveErpDomainService: (locator?: ServiceLocator) => OrderDomainService;
export declare const resolveErpController: (locator?: ServiceLocator) => ERPApiController;
//# sourceMappingURL=bootstrap.d.ts.map