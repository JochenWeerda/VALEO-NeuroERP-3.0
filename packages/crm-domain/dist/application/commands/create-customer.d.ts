import { CRMDomainService } from '../../services/crm-domain-service';
import type { CreateCustomerDTO, CustomerDTO } from '../dto/customer-dto';
export declare class CreateCustomerCommand {
    private readonly service;
    constructor(service: CRMDomainService);
    execute(payload: CreateCustomerDTO): Promise<CustomerDTO>;
}
//# sourceMappingURL=create-customer.d.ts.map