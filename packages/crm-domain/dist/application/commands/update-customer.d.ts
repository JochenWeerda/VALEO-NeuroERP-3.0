import { CRMDomainService } from '../../services/crm-domain-service';
import type { UpdateCustomerDTO, CustomerDTO } from '../dto/customer-dto';
export declare class UpdateCustomerCommand {
    private readonly service;
    constructor(service: CRMDomainService);
    execute(id: string, payload: UpdateCustomerDTO): Promise<CustomerDTO>;
}
//# sourceMappingURL=update-customer.d.ts.map