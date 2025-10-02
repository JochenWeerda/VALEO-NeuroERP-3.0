import type { CustomerStatus, CustomerType } from '../../core/entities/customer';
export interface CustomerDTO {
    id: string;
    customerNumber: string;
    name: string;
    type: CustomerType;
    status: CustomerStatus;
    email?: string;
    phone?: string;
    website?: string;
    street?: string;
    city?: string;
    postalCode?: string;
    country?: string;
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
    createdAt: string;
    updatedAt?: string;
}
export interface CreateCustomerDTO {
    customerNumber?: string;
    name: string;
    type: CustomerType;
    status?: CustomerStatus;
    email?: string;
    phone?: string;
    website?: string;
    street?: string;
    city?: string;
    postalCode?: string;
    country?: string;
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
export type UpdateCustomerDTO = Partial<CreateCustomerDTO>;
export interface GetCustomersQueryDTO {
    search?: string;
    status?: CustomerStatus;
    type?: CustomerType;
    limit?: number;
    offset?: number;
}
//# sourceMappingURL=customer-dto.d.ts.map