import type { Brand, Email, PhoneNumber } from '../../types/branded-types';
export type CustomerId = Brand<string, 'CustomerId'>;
export type CustomerStatus = 'active' | 'inactive' | 'suspended';
export type CustomerType = 'company' | 'individual' | 'partner' | 'distributor';
export interface CustomerAddress {
    street?: string;
    city?: string;
    postalCode?: string;
    country?: string;
}
export interface Customer {
    readonly id: CustomerId;
    readonly createdAt: Date;
    customerNumber: string;
    name: string;
    type: CustomerType;
    status: CustomerStatus;
    email?: Email;
    phone?: PhoneNumber;
    website?: string;
    address?: CustomerAddress;
    industry?: string;
    companySize?: string;
    annualRevenue?: number;
    taxId?: string;
    vatNumber?: string;
    salesRepId?: string;
    leadSource?: string;
    leadScore?: number;
    notes?: string;
    tags: string[];
    updatedAt: Date;
}
export interface CreateCustomerInput {
    customerNumber?: string;
    name: string;
    type: CustomerType;
    status?: CustomerStatus;
    email?: Email;
    phone?: PhoneNumber;
    website?: string;
    address?: CustomerAddress;
    industry?: string;
    companySize?: string;
    annualRevenue?: number;
    taxId?: string;
    vatNumber?: string;
    salesRepId?: string;
    leadSource?: string;
    leadScore?: number;
    notes?: string;
    tags?: string[];
}
export type UpdateCustomerInput = Partial<CreateCustomerInput> & {
    status?: CustomerStatus;
};
export interface CustomerFilters {
    search?: string;
    status?: CustomerStatus;
    type?: CustomerType;
    tags?: string[];
    limit?: number;
    offset?: number;
}
export declare const DEFAULT_PAGE_SIZE = 25;
export declare function createCustomer(input: CreateCustomerInput): Customer;
export declare function applyCustomerUpdate(customer: Customer, updates: UpdateCustomerInput): Customer;
export type { Email, PhoneNumber };
//# sourceMappingURL=customer.d.ts.map