import { z } from 'zod';
import { v4 as uuidv4 } from 'uuid';

// Enums
export const CustomerStatus = {
  ACTIVE: 'Active',
  PROSPECT: 'Prospect',
  BLOCKED: 'Blocked'
} as const;

export type CustomerStatusType = typeof CustomerStatus[keyof typeof CustomerStatus];

// Address Schema
export const AddressSchema = z.object({
  street: z.string().min(1),
  city: z.string().min(1),
  postalCode: z.string().min(1),
  country: z.string().min(1),
  state: z.string().optional()
});

export type Address = z.infer<typeof AddressSchema>;

// Customer Entity Schema
export const CustomerSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  number: z.string().min(1),
  name: z.string().min(1),
  vatId: z.string().optional(),
  billingAddress: AddressSchema,
  shippingAddresses: z.array(AddressSchema).default([]),
  email: z.string().email().optional(),
  phone: z.string().optional(),
  tags: z.array(z.string()).default([]),
  status: z.enum([CustomerStatus.ACTIVE, CustomerStatus.PROSPECT, CustomerStatus.BLOCKED]),
  ownerUserId: z.string().uuid().optional(),
  createdAt: z.date(),
  updatedAt: z.date(),
  version: z.number().int().nonnegative()
});

export type Customer = z.infer<typeof CustomerSchema>;

// Create Customer Input Schema (for API)
export const CreateCustomerInputSchema = CustomerSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  version: true
}).extend({
  shippingAddresses: z.array(AddressSchema).optional().default([])
});

export type CreateCustomerInput = z.infer<typeof CreateCustomerInputSchema>;

// Update Customer Input Schema (for API)
export const UpdateCustomerInputSchema = z.object({
  name: z.string().min(1).optional(),
  vatId: z.string().nullish(),
  billingAddress: AddressSchema.optional(),
  shippingAddresses: z.array(AddressSchema).optional(),
  email: z.string().email().nullish(),
  phone: z.string().nullish(),
  tags: z.array(z.string()).optional(),
  status: z.enum([CustomerStatus.ACTIVE, CustomerStatus.PROSPECT, CustomerStatus.BLOCKED]).optional(),
  ownerUserId: z.string().uuid().nullish()
});

export type UpdateCustomerInput = z.infer<typeof UpdateCustomerInputSchema>;

// Customer Aggregate Root
export class CustomerEntity {
  private constructor(private props: Customer) {}

  public static create(props: CreateCustomerInput & { tenantId: string }): CustomerEntity {
    const now = new Date();
    const customer: Customer = {
      ...props,
      id: uuidv4(),
      status: props.status || CustomerStatus.PROSPECT,
      tags: props.tags ?? [],
      shippingAddresses: props.shippingAddresses ?? [],
      createdAt: now,
      updatedAt: now,
      version: 1
    };

    return new CustomerEntity(customer);
  }

  public static fromPersistence(props: Customer): CustomerEntity {
    return new CustomerEntity(props);
  }

  public update(props: UpdateCustomerInput): void {
    if (props.name !== undefined) {
      this.props.name = props.name;
    }
    if (props.vatId !== undefined) {
      this.props.vatId = props.vatId ?? undefined;
    }
    if (props.billingAddress !== undefined) {
      this.props.billingAddress = props.billingAddress;
    }
    if (props.shippingAddresses !== undefined) {
      this.props.shippingAddresses = props.shippingAddresses;
    }
    if (props.email !== undefined) {
      this.props.email = props.email ?? undefined;
    }
    if (props.phone !== undefined) {
      this.props.phone = props.phone ?? undefined;
    }
    if (props.tags !== undefined) {
      this.props.tags = props.tags;
    }
    if (props.status !== undefined) {
      this.props.status = props.status;
    }
    if (props.ownerUserId !== undefined) {
      this.props.ownerUserId = props.ownerUserId ?? undefined;
    }

    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public changeStatus(newStatus: CustomerStatusType): void {
    if (this.props.status !== newStatus) {
      this.props.status = newStatus;
      this.props.updatedAt = new Date();
      this.props.version += 1;
    }
  }

  public addTag(tag: string): void {
    if (!this.props.tags.includes(tag)) {
      this.props.tags.push(tag);
      this.props.updatedAt = new Date();
      this.props.version += 1;
    }
  }

  public removeTag(tag: string): void {
    const index = this.props.tags.indexOf(tag);
    if (index > -1) {
      this.props.tags.splice(index, 1);
      this.props.updatedAt = new Date();
      this.props.version += 1;
    }
  }

  public addShippingAddress(address: Address): void {
    this.props.shippingAddresses.push(address);
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public removeShippingAddress(index: number): void {
    if (index >= 0 && index < this.props.shippingAddresses.length) {
      this.props.shippingAddresses.splice(index, 1);
      this.props.updatedAt = new Date();
      this.props.version += 1;
    }
  }

  // Getters
  public get id(): string { return this.props.id; }
  public get tenantId(): string { return this.props.tenantId; }
  public get number(): string { return this.props.number; }
  public get name(): string { return this.props.name; }
  public get vatId(): string | undefined { return this.props.vatId; }
  public get billingAddress(): Address { return this.props.billingAddress; }
  public get shippingAddresses(): Address[] { return [...this.props.shippingAddresses]; }
  public get email(): string | undefined { return this.props.email; }
  public get phone(): string | undefined { return this.props.phone; }
  public get tags(): string[] { return [...this.props.tags]; }
  public get status(): CustomerStatusType { return this.props.status; }
  public get ownerUserId(): string | undefined { return this.props.ownerUserId; }
  public get createdAt(): Date { return this.props.createdAt; }
  public get updatedAt(): Date { return this.props.updatedAt; }
  public get version(): number { return this.props.version; }

  // Export for persistence
  public toPersistence(): Customer {
    return { ...this.props };
  }

  // Export for API responses
  public toJSON(): Omit<Customer, 'tenantId'> {
    const { tenantId, ...customerWithoutTenant } = this.props;
    return customerWithoutTenant;
  }
}
