import { CRMDomainService } from '../../services/crm-domain-service';
import type { GetCustomersQueryDTO, CustomerDTO } from '../dto/customer-dto';
export declare class GetCustomersQuery {
    private readonly service;
    constructor(service: CRMDomainService);
    execute(filters: GetCustomersQueryDTO): Promise<CustomerDTO[]>;
}
//# sourceMappingURL=get-customers.d.ts.map