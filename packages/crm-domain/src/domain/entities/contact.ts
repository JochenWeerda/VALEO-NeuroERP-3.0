import { z } from 'zod';
import { v4 as uuidv4 } from 'uuid';

// Contact Entity Schema
export const ContactSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  customerId: z.string().uuid(),
  firstName: z.string().min(1),
  lastName: z.string().min(1),
  role: z.string().optional(),
  email: z.string().email(),
  phone: z.string().optional(),
  isPrimary: z.boolean().default(false),
  notes: z.string().optional(),
  createdAt: z.date(),
  updatedAt: z.date(),
  version: z.number().int().nonnegative()
});

export type Contact = z.infer<typeof ContactSchema>;

// Create Contact Input Schema (for API)
export const CreateContactInputSchema = ContactSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  version: true
});

export type CreateContactInput = z.infer<typeof CreateContactInputSchema>;

// Update Contact Input Schema (for API)
export const UpdateContactInputSchema = z.object({
  firstName: z.string().min(1).optional(),
  lastName: z.string().min(1).optional(),
  role: z.string().nullish(),
  email: z.string().email().optional(),
  phone: z.string().nullish(),
  isPrimary: z.boolean().optional(),
  notes: z.string().nullish()
});

export type UpdateContactInput = z.infer<typeof UpdateContactInputSchema>;

// Contact Aggregate Root
export class ContactEntity {
  private constructor(private props: Contact) {}

  public static create(props: CreateContactInput & { tenantId: string }): ContactEntity {
    const now = new Date();
    const contact: Contact = {
      ...props,
      id: uuidv4(),
      isPrimary: props.isPrimary || false,
      createdAt: now,
      updatedAt: now,
      version: 1
    };

    return new ContactEntity(contact);
  }

  public static fromPersistence(props: Contact): ContactEntity {
    return new ContactEntity(props);
  }

  public update(props: UpdateContactInput): void {
    if (props.firstName !== undefined) {
      this.props.firstName = props.firstName;
    }
    if (props.lastName !== undefined) {
      this.props.lastName = props.lastName;
    }
    if (props.role !== undefined) {
      this.props.role = props.role ?? undefined;
    }
    if (props.email !== undefined) {
      this.props.email = props.email ?? undefined;
    }
    if (props.phone !== undefined) {
      this.props.phone = props.phone ?? undefined;
    }
    if (props.isPrimary !== undefined) {
      this.props.isPrimary = props.isPrimary;
    }
    if (props.notes !== undefined) {
      this.props.notes = props.notes ?? undefined;
    }

    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public makePrimary(): void {
    this.props.isPrimary = true;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public makeSecondary(): void {
    this.props.isPrimary = false;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  public updateNotes(notes: string): void {
    this.props.notes = notes;
    this.props.updatedAt = new Date();
    this.props.version += 1;
  }

  // Getters
  public get id(): string { return this.props.id; }
  public get tenantId(): string { return this.props.tenantId; }
  public get customerId(): string { return this.props.customerId; }
  public get firstName(): string { return this.props.firstName; }
  public get lastName(): string { return this.props.lastName; }
  public get fullName(): string { return `${this.props.firstName} ${this.props.lastName}`; }
  public get role(): string | undefined { return this.props.role; }
  public get email(): string { return this.props.email; }
  public get phone(): string | undefined { return this.props.phone; }
  public get isPrimary(): boolean { return this.props.isPrimary; }
  public get notes(): string | undefined { return this.props.notes; }
  public get createdAt(): Date { return this.props.createdAt; }
  public get updatedAt(): Date { return this.props.updatedAt; }
  public get version(): number { return this.props.version; }

  // Export for persistence
  public toPersistence(): Contact {
    return { ...this.props };
  }

  // Export for API responses
  public toJSON(): Omit<Contact, 'tenantId'> {
    const { tenantId, ...contactWithoutTenant } = this.props;
    return contactWithoutTenant;
  }
}