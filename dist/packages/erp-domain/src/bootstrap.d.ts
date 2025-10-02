import { ServiceLocator } from "@valero-neuroerp/utilities";
import { OrderRepository } from './core/repositories/order-repository';
import type { CreateOrderInput } from './core/entities/order';
export interface ErpBootstrapOptions {
    locator?: ServiceLocator;
    repository?: OrderRepository;
    seed?: CreateOrderInput[];
}
export declare function registerErpDomain(options?: ErpBootstrapOptions): ServiceLocator;
export declare const resolveErpDomainService: (locator?: ServiceLocator) => any;
export declare const resolveErpController: (locator?: ServiceLocator) => any;
//***REMOVED*** sourceMappingURL=bootstrap.d.ts.map