import { CRMDomainService } from '../../services/crm-domain-service';
import { toCustomerId } from '../mappers/customer-mapper';

export class DeleteCustomerCommand {
  constructor(private readonly service: CRMDomainService) {}

  async execute(id: string): Promise<void> {
    await this.service.deleteCustomer(toCustomerId(id));
  }
}
