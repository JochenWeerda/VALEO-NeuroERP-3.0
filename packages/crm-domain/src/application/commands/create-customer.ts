import { CRMDomainService } from '../../services/crm-domain-service';
import { toCreateCustomerInput, toCustomerDTO } from '../mappers/customer-mapper';
import type { CreateCustomerDTO, CustomerDTO } from '../dto/customer-dto';

export class CreateCustomerCommand {
  constructor(private readonly service: CRMDomainService) {}

  async execute(payload: CreateCustomerDTO): Promise<CustomerDTO> {
    const created = await this.service.createCustomer(toCreateCustomerInput(payload));
    return toCustomerDTO(created);
  }
}
