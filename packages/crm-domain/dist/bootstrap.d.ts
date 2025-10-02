import { Logger, MetricsRecorder, ServiceLocator } from '@valero-neuroerp/utilities';
import { CustomerRepository } from './core/repositories/customer-repository';
import { CreateCustomerInput } from './core/entities/customer';
import { CRMDomainService } from './services/crm-domain-service';
import { CRMApiController } from './presentation/controllers/crm-api-controller';
export interface CRMBootstrapOptions {
    locator?: ServiceLocator;
    repository?: CustomerRepository;
    seed?: CreateCustomerInput[];
    logger?: Logger;
    metrics?: MetricsRecorder;
}
export declare function registerCrmDomain(options?: CRMBootstrapOptions): ServiceLocator;
export declare const resolveCrmDomainService: (locator?: ServiceLocator) => CRMDomainService;
export declare const resolveCrmController: (locator?: ServiceLocator) => CRMApiController;
//# sourceMappingURL=bootstrap.d.ts.map