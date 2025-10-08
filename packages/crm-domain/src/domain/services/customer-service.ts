import { CustomerEntity, CreateCustomerInput, UpdateCustomerInput, CustomerStatusType } from '../entities';
import { CustomerRepository } from '../../infra/repo';

export interface CustomerServiceDependencies {
  customerRepo: CustomerRepository;
}

export interface CreateCustomerData extends CreateCustomerInput {
  tenantId: string;
  number: string;
  vatId?: string;
}

export interface UpdateCustomerData extends UpdateCustomerInput {
  tenantId: string;
  vatId?: string;
}

export class CustomerService {
  constructor(private deps: CustomerServiceDependencies) {}

  async createCustomer(data: CreateCustomerData): Promise<CustomerEntity> {
    // Business validation
    if (data.vatId) {
      await this.validateVatId(data.vatId, data.tenantId);
    }

    // Check if customer number already exists
    const existingCustomer = await this.deps.customerRepo.findByNumber(data.number, data.tenantId);
    if (existingCustomer) {
      throw new Error(`Customer number ${data.number} already exists`);
    }

    // Create customer
    const customer = await this.deps.customerRepo.create(data);

    return customer;
  }

  async getCustomer(id: string, tenantId: string): Promise<CustomerEntity | null> {
    return this.deps.customerRepo.findById(id, tenantId);
  }

  async getCustomerByNumber(number: string, tenantId: string): Promise<CustomerEntity | null> {
    return this.deps.customerRepo.findByNumber(number, tenantId);
  }

  async updateCustomer(id: string, data: UpdateCustomerData): Promise<CustomerEntity> {
    // Get existing customer
    const existingCustomer = await this.deps.customerRepo.findById(id, data.tenantId);
    if (existingCustomer === undefined || existingCustomer === null) {
      throw new Error(`Customer ${id} not found`);
    }

    // Business validation
    if (data.vatId && data.vatId !== existingCustomer.vatId) {
      await this.validateVatId(data.vatId, data.tenantId);
    }

    // Update customer
    const updatedCustomer = await this.deps.customerRepo.update(id, data.tenantId, data);

    if (updatedCustomer === undefined || updatedCustomer === null) {
      throw new Error(`Failed to update customer ${id}`);
    }

    return updatedCustomer;
  }

  async deleteCustomer(id: string, tenantId: string): Promise<boolean> {
    // Check if customer exists
    const customer = await this.deps.customerRepo.findById(id, tenantId);
    if (customer === undefined || customer === null) {
      throw new Error(`Customer ${id} not found`);
    }

    // Check if customer has related records (contacts, opportunities, interactions)
    // This would typically be checked here before deletion

    return this.deps.customerRepo.delete(id, tenantId);
  }

  async changeCustomerStatus(id: string, tenantId: string, status: CustomerStatusType): Promise<CustomerEntity> {
    const customer = await this.deps.customerRepo.findById(id, tenantId);
    if (customer === undefined || customer === null) {
      throw new Error(`Customer ${id} not found`);
    }

    // Business rules for status changes
    if (customer.status === status) {
      return customer; // No change needed
    }

    // Validate status transition
    this.validateStatusTransition(customer.status, status);

    const updatedCustomer = await this.deps.customerRepo.updateStatus(id, tenantId, status);

    if (updatedCustomer === undefined || updatedCustomer === null) {
      throw new Error(`Failed to update customer status`);
    }

    return updatedCustomer;
  }

  async addTag(id: string, tenantId: string, tag: string): Promise<CustomerEntity> {
    const customer = await this.deps.customerRepo.findById(id, tenantId);
    if (customer === undefined || customer === null) {
      throw new Error(`Customer ${id} not found`);
    }

    if (customer.tags.includes(tag)) {
      return customer; // Tag already exists
    }

    const updatedCustomer = await this.deps.customerRepo.addTag(id, tenantId, tag);

    if (updatedCustomer === undefined || updatedCustomer === null) {
      throw new Error(`Failed to add tag to customer`);
    }

    return updatedCustomer;
  }

  async removeTag(id: string, tenantId: string, tag: string): Promise<CustomerEntity> {
    const customer = await this.deps.customerRepo.findById(id, tenantId);
    if (customer === undefined || customer === null) {
      throw new Error(`Customer ${id} not found`);
    }

    if (!customer.tags.includes(tag)) {
      return customer; // Tag doesn't exist
    }

    const updatedCustomer = await this.deps.customerRepo.removeTag(id, tenantId, tag);

    if (updatedCustomer === undefined || updatedCustomer === null) {
      throw new Error(`Failed to remove tag from customer`);
    }

    return updatedCustomer;
  }

  async searchCustomers(
    tenantId: string,
    filters: {
      search?: string;
      status?: CustomerStatusType;
      tags?: string[];
      ownerUserId?: string;
    } = {},
    pagination: { page: number; pageSize: number } = { page: 1, pageSize: 20 }
  ) {
    return this.deps.customerRepo.findAll(tenantId, filters, pagination);
  }

  private async validateVatId(vatId: string, tenantId: string): Promise<void> {
    // Basic VAT ID validation (you might want to implement more sophisticated validation)
    if (!vatId || vatId.length < 5) {
      throw new Error('Invalid VAT ID format');
    }

    // Check if VAT ID is already used by another customer
    // This would require a more complex query in a real implementation
  }

  private validateStatusTransition(currentStatus: CustomerStatusType, newStatus: CustomerStatusType): void {
    // Define valid status transitions
    const validTransitions: Record<CustomerStatusType, CustomerStatusType[]> = {
      'Prospect': ['Active', 'Blocked'],
      'Active': ['Blocked'],
      'Blocked': ['Active', 'Prospect']
    };

    const allowedStatuses = validTransitions[currentStatus];

    if (!allowedStatuses?.includes(newStatus)) {
      throw new Error(`Cannot change status from ${currentStatus} to ${newStatus}`);
    }
  }
}
