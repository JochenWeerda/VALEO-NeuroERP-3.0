import { CRMDomainService } from '../../services/crm-domain-service';
import { toUpdateCustomerInput, toCustomerDTO, toCustomerId } from '../mappers/customer-mapper';
import type { UpdateCustomerDTO, CustomerDTO } from '../dto/customer-dto';

export class UpdateCustomerCommand {
  constructor(private readonly service: CRMDomainService) {}

  async execute(id: string, payload: UpdateCustomerDTO): Promise<CustomerDTO> {
    const updated = await this.service.updateCustomer(toCustomerId(id), toUpdateCustomerInput(payload));
    return toCustomerDTO(updated);
  }
}
