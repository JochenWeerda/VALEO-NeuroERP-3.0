import { ContactEntity, CreateContactInput, UpdateContactInput } from '../entities';
import { ContactRepository } from '../../infra/repo';

export interface ContactServiceDependencies {
  contactRepo: ContactRepository;
}

export interface CreateContactData extends CreateContactInput {
  tenantId: string;
  customerId: string;
  email: string;
  firstName: string;
  lastName: string;
  isPrimary: boolean;
}

export interface UpdateContactData extends UpdateContactInput {
  tenantId: string;
  email?: string;
  isPrimary?: boolean;
}

export class ContactService {
  constructor(private deps: ContactServiceDependencies) {}

  async createContact(data: CreateContactData): Promise<ContactEntity> {
    // Business validation
    await this.validateContactEmail(data.email, data.tenantId);

    // If this contact is marked as primary, ensure no other primary contact exists for this customer
    if (data.isPrimary) {
      await this.ensureNoPrimaryContact(data.customerId, data.tenantId);
    }

    const contact = await this.deps.contactRepo.create(data);
    return contact;
  }

  async getContact(id: string, tenantId: string): Promise<ContactEntity | null> {
    return this.deps.contactRepo.findById(id, tenantId);
  }

  async getContactsByCustomer(
    customerId: string,
    tenantId: string,
    pagination: { page: number; pageSize: number } = { page: 1, pageSize: 20 }
  ) {
    return this.deps.contactRepo.findByCustomerId(customerId, tenantId, {}, pagination);
  }

  async updateContact(id: string, data: UpdateContactData): Promise<ContactEntity> {
    const existingContact = await this.deps.contactRepo.findById(id, data.tenantId);
    if (!existingContact) {
      throw new Error(`Contact ${id} not found`);
    }

    // Business validation
    if (data.email && data.email !== existingContact.email) {
      await this.validateContactEmail(data.email, data.tenantId);
    }

    // If this contact is being marked as primary, ensure no other primary contact exists
    if (data.isPrimary && !existingContact.isPrimary) {
      await this.ensureNoPrimaryContact(existingContact.customerId, data.tenantId);
    }

    const updatedContact = await this.deps.contactRepo.update(id, data.tenantId, data);

    if (!updatedContact) {
      throw new Error(`Failed to update contact ${id}`);
    }

    return updatedContact;
  }

  async deleteContact(id: string, tenantId: string): Promise<boolean> {
    const contact = await this.deps.contactRepo.findById(id, tenantId);
    if (!contact) {
      throw new Error(`Contact ${id} not found`);
    }

    return this.deps.contactRepo.delete(id, tenantId);
  }

  async setPrimaryContact(customerId: string, contactId: string, tenantId: string): Promise<void> {
    const contact = await this.deps.contactRepo.findById(contactId, tenantId);
    if (!contact) {
      throw new Error(`Contact ${contactId} not found`);
    }

    if (contact.customerId !== customerId) {
      throw new Error(`Contact ${contactId} does not belong to customer ${customerId}`);
    }

    await this.deps.contactRepo.setPrimaryContact(customerId, contactId, tenantId);
  }

  async getPrimaryContact(customerId: string, tenantId: string): Promise<ContactEntity | null> {
    return this.deps.contactRepo.getPrimaryContact(customerId, tenantId);
  }

  private async validateContactEmail(email: string, tenantId: string): Promise<void> {
    // Check if email is already used by another contact
    const existingContact = await this.deps.contactRepo.findByEmail(email, tenantId);
    if (existingContact) {
      throw new Error(`Email ${email} is already in use by another contact`);
    }
  }

  private async ensureNoPrimaryContact(customerId: string, tenantId: string): Promise<void> {
    const primaryContact = await this.deps.contactRepo.getPrimaryContact(customerId, tenantId);
    if (primaryContact) {
      // Demote existing primary contact to secondary
      await this.deps.contactRepo.update(primaryContact.id, tenantId, { isPrimary: false });
    }
  }
}