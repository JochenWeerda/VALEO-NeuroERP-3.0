import type { CustomerId } from "@valero-neuroerp/data-models";
import { createQueryBuilder, InMemoryRepository } from "@valero-neuroerp/utilities";
import {
  Customer,
  CustomerFilters,
  CreateCustomerInput,
  applyCustomerUpdate,
  createCustomer,
} from "../../core/entities/customer";
import { CustomerRepository, buildCustomerQuery } from "../../core/repositories/customer-repository";

export class InMemoryCustomerRepository
  extends InMemoryRepository<Customer, 'id', CustomerId>
  implements CustomerRepository {
  constructor(seed: CreateCustomerInput[] = []) {
    super('id');
    seed.forEach((input) => {
      const entity = createCustomer(input);
      void this.create(entity);
    });
  }

  async list(filters?: CustomerFilters): Promise<Customer[]> {
    return this.findMany(buildCustomerQuery(filters));
  }

  async findByEmail(email: string): Promise<Customer | null> {
    const query = createQueryBuilder<Customer>().where('email', 'eq', email as Customer['email']).build();
    return this.findOne(query);
  }

  async findByCustomerNumber(customerNumber: string): Promise<Customer | null> {
    const query = createQueryBuilder<Customer>()
      .where('customerNumber', 'eq', customerNumber as Customer['customerNumber'])
      .build();
    return this.findOne(query);
  }
}
