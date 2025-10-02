import { RepositoryBase } from '@valero-neuroerp/utilities';
import type { CustomerId } from '@valero-neuroerp/data-models';
import { Customer, CustomerFilters } from '../../core/entities/customer';

export class CustomerPostgresRepository extends RepositoryBase<Customer, CustomerId> {
  private readonly customers = new Map<CustomerId, Customer>();

  async findById(id: CustomerId): Promise<Customer | null> {
    return this.customers.get(id) ?? null;
  }

  async findMany(query?: any): Promise<Customer[]> {
    if (!query) {
      return Array.from(this.customers.values());
    }
    
    return Array.from(this.customers.values()).filter(customer => {
      if (query.where) {
        const conditions = query.where;
        return Object.entries(conditions).every(([key, value]) => {
          return (customer as any)[key] === value;
        });
      }
      return true;
    });
  }

  async create(entity: Customer): Promise<Customer> {
    this.customers.set(entity.id, entity);
    return entity;
  }

  async update(id: CustomerId, updates: Partial<Customer>): Promise<Customer> {
    const existing = this.customers.get(id);
    if (!existing) {
      throw new Error(`Customer ${String(id)} not found`);
    }
    
    const updated = { ...existing, ...updates, updatedAt: new Date() };
    this.customers.set(id, updated);
    return updated;
  }

  async delete(id: CustomerId): Promise<void> {
    this.customers.delete(id);
  }

  async list(filters?: CustomerFilters): Promise<Customer[]> {
    let customers = Array.from(this.customers.values());

    if (filters) {
      if (filters.search) {
        const search = filters.search.toLowerCase();
        customers = customers.filter(c => 
          c.name.toLowerCase().includes(search) ||
          c.customerNumber.toLowerCase().includes(search)
        );
      }

      if (filters.status) {
        customers = customers.filter(c => c.status === filters.status);
      }

      if (filters.type) {
        customers = customers.filter(c => c.type === filters.type);
      }

      if (filters.tags && filters.tags.length > 0) {
        customers = customers.filter(c => 
          filters.tags!.some(tag => c.tags.includes(tag))
        );
      }
    }

    // Apply pagination
    const offset = filters?.offset ?? 0;
    const limit = filters?.limit ?? 25;
    
    return customers.slice(offset, offset + limit);
  }

  async findByEmail(email: string): Promise<Customer | null> {
    return Array.from(this.customers.values()).find(c => c.email === email) ?? null;
  }

  async findByCustomerNumber(customerNumber: string): Promise<Customer | null> {
    return Array.from(this.customers.values()).find(c => c.customerNumber === customerNumber) ?? null;
  }
}
