import { CRMDomainService } from '../../services/crm-domain-service';
import { toCustomerDTO, toCustomerFilters } from '../mappers/customer-mapper';
import type { GetCustomersQueryDTO, CustomerDTO } from '../dto/customer-dto';

export class GetCustomersQuery {
  constructor(private readonly service: CRMDomainService) {}

  async execute(filters: GetCustomersQueryDTO): Promise<CustomerDTO[]> {
    const customers = await this.service.listCustomers(toCustomerFilters(filters));
    return customers.map(toCustomerDTO);
  }
}
