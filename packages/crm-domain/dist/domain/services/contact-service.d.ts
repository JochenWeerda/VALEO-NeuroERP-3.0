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
export declare class ContactService {
    private deps;
    constructor(deps: ContactServiceDependencies);
    createContact(data: CreateContactData): Promise<ContactEntity>;
    getContact(id: string, tenantId: string): Promise<ContactEntity | null>;
    getContactsByCustomer(customerId: string, tenantId: string, pagination?: {
        page: number;
        pageSize: number;
    }): Promise<import("../../infra/repo/contact-repository").PaginatedResult<ContactEntity>>;
    updateContact(id: string, data: UpdateContactData): Promise<ContactEntity>;
    deleteContact(id: string, tenantId: string): Promise<boolean>;
    setPrimaryContact(customerId: string, contactId: string, tenantId: string): Promise<void>;
    getPrimaryContact(customerId: string, tenantId: string): Promise<ContactEntity | null>;
    private validateContactEmail;
    private ensureNoPrimaryContact;
}
//# sourceMappingURL=contact-service.d.ts.map