"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ContactService = void 0;
class ContactService {
    deps;
    constructor(deps) {
        this.deps = deps;
    }
    async createContact(data) {
        // Business validation
        await this.validateContactEmail(data.email, data.tenantId);
        // If this contact is marked as primary, ensure no other primary contact exists for this customer
        if (data.isPrimary) {
            await this.ensureNoPrimaryContact(data.customerId, data.tenantId);
        }
        const contact = await this.deps.contactRepo.create(data);
        return contact;
    }
    async getContact(id, tenantId) {
        return this.deps.contactRepo.findById(id, tenantId);
    }
    async getContactsByCustomer(customerId, tenantId, pagination = { page: 1, pageSize: 20 }) {
        return this.deps.contactRepo.findByCustomerId(customerId, tenantId, {}, pagination);
    }
    async updateContact(id, data) {
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
    async deleteContact(id, tenantId) {
        const contact = await this.deps.contactRepo.findById(id, tenantId);
        if (!contact) {
            throw new Error(`Contact ${id} not found`);
        }
        return this.deps.contactRepo.delete(id, tenantId);
    }
    async setPrimaryContact(customerId, contactId, tenantId) {
        const contact = await this.deps.contactRepo.findById(contactId, tenantId);
        if (!contact) {
            throw new Error(`Contact ${contactId} not found`);
        }
        if (contact.customerId !== customerId) {
            throw new Error(`Contact ${contactId} does not belong to customer ${customerId}`);
        }
        await this.deps.contactRepo.setPrimaryContact(customerId, contactId, tenantId);
    }
    async getPrimaryContact(customerId, tenantId) {
        return this.deps.contactRepo.getPrimaryContact(customerId, tenantId);
    }
    async validateContactEmail(email, tenantId) {
        // Check if email is already used by another contact
        const existingContact = await this.deps.contactRepo.findByEmail(email, tenantId);
        if (existingContact) {
            throw new Error(`Email ${email} is already in use by another contact`);
        }
    }
    async ensureNoPrimaryContact(customerId, tenantId) {
        const primaryContact = await this.deps.contactRepo.getPrimaryContact(customerId, tenantId);
        if (primaryContact) {
            // Demote existing primary contact to secondary
            await this.deps.contactRepo.update(primaryContact.id, tenantId, { isPrimary: false });
        }
    }
}
exports.ContactService = ContactService;
//# sourceMappingURL=contact-service.js.map