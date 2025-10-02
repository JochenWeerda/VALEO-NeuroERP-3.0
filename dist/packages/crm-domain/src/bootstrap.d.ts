import { Logger, MetricsRecorder, ServiceLocator } from '@valero-neuroerp/utilities';
import { CustomerRepository } from './core/repositories/customer-repository';
import { CreateCustomerInput } from './core/entities/customer';
export interface CRMBootstrapOptions {
    locator?: ServiceLocator;
    repository?: CustomerRepository;
    seed?: CreateCustomerInput[];
    logger?: Logger;
    metrics?: MetricsRecorder;
}
export declare function registerCrmDomain(options?: CRMBootstrapOptions): ServiceLocator;
export declare const resolveCrmDomainService: (locator?: ServiceLocator) => any;
export declare const resolveCrmController: (locator?: ServiceLocator) => any;
//***REMOVED*** sourceMappingURL=bootstrap.d.ts.map