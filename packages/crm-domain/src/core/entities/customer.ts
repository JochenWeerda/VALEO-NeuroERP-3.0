import { createId } from '../../types/branded-types';
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
  // Sales-spezifische Felder (SALES-CRM-02)
  priceGroup?: string;  // NEU: sales.price_group (standard, premium, wholesale, retail)
  taxCategory?: string;  // NEU: tax.category (standard, reduced, zero, reverse_charge, exempt)
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
  // Sales-spezifische Felder (SALES-CRM-02)
  priceGroup?: string;  // NEU: sales.price_group
  taxCategory?: string;  // NEU: tax.category
}

export type UpdateCustomerInput = Partial<CreateCustomerInput> & { status?: CustomerStatus };

export interface CustomerFilters {
  search?: string;
  status?: CustomerStatus;
  type?: CustomerType;
  tags?: string[];
  limit?: number;
  offset?: number;
}

export const DEFAULT_PAGE_SIZE = 25;

export function createCustomer(input: CreateCustomerInput): Customer {
  if (!input.name?.trim()) {
    throw new Error('Customer name is required');
  }
  if (input.type === undefined || input.type === null) {
    throw new Error('Customer type is required');
  }

  const now = new Date();

  return {
    id: createId('CustomerId'),
    createdAt: now,
    updatedAt: now,
    customerNumber: input.customerNumber ?? generateCustomerNumber(),
    name: input.name.trim(),
    type: input.type,
    status: input.status ?? 'active',
    email: input.email,
    phone: input.phone,
    website: input.website?.trim(),
    address: input.address ? { ...input.address } : undefined,
    industry: input.industry,
    companySize: input.companySize,
    annualRevenue: input.annualRevenue,
    taxId: input.taxId,
    vatNumber: input.vatNumber,
    salesRepId: input.salesRepId,
    leadSource: input.leadSource,
    leadScore: input.leadScore,
    notes: input.notes,
    tags: normalizeTags(input.tags),
  } as any;
}

export function applyCustomerUpdate(customer: Customer, updates: UpdateCustomerInput): Customer {
  return {
    ...customer,
    customerNumber: updates.customerNumber ?? customer.customerNumber,
    name: updates.name ? updates.name.trim() : customer.name,
    type: updates.type ?? customer.type,
    status: updates.status ?? customer.status,
    email: updates.email ?? customer.email,
    phone: updates.phone ?? customer.phone,
    website: updates.website?.trim() ?? customer.website,
    address: updates.address ? { ...updates.address } : customer.address,
    industry: updates.industry ?? customer.industry,
    companySize: updates.companySize ?? customer.companySize,
    annualRevenue: updates.annualRevenue ?? customer.annualRevenue,
    taxId: updates.taxId ?? customer.taxId,
    vatNumber: updates.vatNumber ?? customer.vatNumber,
    salesRepId: updates.salesRepId ?? customer.salesRepId,
    leadSource: updates.leadSource ?? customer.leadSource,
    leadScore: updates.leadScore ?? customer.leadScore,
    notes: updates.notes ?? customer.notes,
    tags: updates.tags ? normalizeTags(updates.tags) : customer.tags,
    updatedAt: new Date(),
  } as any;
}

function generateCustomerNumber(): string {
  return `C-${Date.now().toString(36).toUpperCase()}`;
}

function normalizeTags(tags?: string[]): string[] {
  if (tags === undefined || tags === null) {
    return [];
  }
  return Array.from(new Set(tags.map((tag) => tag.trim()).filter(Boolean)));
}

export type { Email, PhoneNumber };


