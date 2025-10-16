import { Logger, MetricsRecorder } from '@valero-neuroerp/utilities';
import {
  Customer,
  CustomerFilters,
  CreateCustomerInput,
  UpdateCustomerInput,
  applyCustomerUpdate,
  createCustomer,
  CustomerId,
} from "../core/entities/customer";
import { CustomerRepository } from "../core/repositories/customer-repository";

export interface CRMDomainServiceOptions {
  logger?: Logger;
  metrics?: MetricsRecorder;
}

const noopLogger: Logger = {
  debug() {},
  info() {},
  warn() {},
  error() {},
};

export class CRMDomainService {
  private readonly logger: Logger;
  private readonly metrics: MetricsRecorder | undefined;

  constructor(private readonly customers: CustomerRepository, options: CRMDomainServiceOptions = {}) {
    this.logger = options.logger ?? noopLogger;
    this.metrics = options.metrics ?? undefined;
  }

  async createCustomer(input: CreateCustomerInput): Promise<Customer> {
    this.logger.info('crm.customer.create.start', { name: input.name, type: input.type });
    const customer = createCustomer(input);
    const saved = await this.customers.create(customer);
    this.metrics?.incrementCounter('crm.customer.created', { type: saved.type });
    return saved;
  }

  async updateCustomer(id: CustomerId, updates: UpdateCustomerInput): Promise<Customer> {
    const existing = await this.customers.findById(id);
    if (existing === undefined || existing === null) {
      throw new Error(`Customer ${String(id)} not found`);
    }
    const next = applyCustomerUpdate(existing, updates);
    const updated = await this.customers.update(id, next);
    this.metrics?.incrementCounter('crm.customer.updated', { type: updated.type });
    return updated;
  }

  async listCustomers(filters?: CustomerFilters): Promise<Customer[]> {
    return this.customers.list(filters);
  }

  async getCustomer(id: CustomerId): Promise<Customer | null> {
    return this.customers.findById(id);
  }

  async deleteCustomer(id: CustomerId): Promise<void> {
    const existing = await this.customers.findById(id);
    if (existing === undefined || existing === null) {
      throw new Error(`Customer ${String(id)} not found`);
    }
    await this.customers.delete(id);
    this.metrics?.incrementCounter('crm.customer.deleted', { type: existing.type });
  }
}

