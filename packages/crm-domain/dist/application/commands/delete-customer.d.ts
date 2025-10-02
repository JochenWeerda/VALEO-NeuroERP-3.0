import { CRMDomainService } from '../../services/crm-domain-service';
export declare class DeleteCustomerCommand {
    private readonly service;
    constructor(service: CRMDomainService);
    execute(id: string): Promise<void>;
}
//# sourceMappingURL=delete-customer.d.ts.map