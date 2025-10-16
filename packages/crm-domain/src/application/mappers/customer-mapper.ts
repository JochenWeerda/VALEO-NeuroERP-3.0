import type { Customer, CustomerFilters, CreateCustomerInput, UpdateCustomerInput, CustomerId, Email, PhoneNumber } from '../../core/entities/customer';
import type { CreateCustomerDTO, CustomerDTO, UpdateCustomerDTO } from '../dto/customer-dto';

function extractAddress(dto: CreateCustomerDTO | UpdateCustomerDTO) {
  const address = {
    street: dto.street,
    city: dto.city,
    postalCode: dto.postalCode,
    country: dto.country,
  };
  const hasValues = Object.values(address).some((value) => typeof value === 'string' && value.trim() !== '');
  return hasValues ? address : undefined;
}

export function toCustomerDTO(customer: Customer): CustomerDTO {
  return {
    id: customer.id,
    customerNumber: customer.customerNumber,
    name: customer.name,
    type: customer.type,
    status: customer.status,
    email: customer.email,
    phone: customer.phone,
    website: customer.website,
    street: customer.address?.street,
    city: customer.address?.city,
    postalCode: customer.address?.postalCode,
    country: customer.address?.country,
    industry: customer.industry,
    companySize: customer.companySize,
    annualRevenue: customer.annualRevenue,
    taxId: customer.taxId,
    vatNumber: customer.vatNumber,
    salesRepId: customer.salesRepId,
    leadSource: customer.leadSource,
    leadScore: customer.leadScore,
    notes: customer.notes,
    tags: customer.tags,
    createdAt: customer.createdAt.toISOString(),
    updatedAt: customer.updatedAt.toISOString(),
  } as CustomerDTO;
}

export function toCreateCustomerInput(dto: CreateCustomerDTO): CreateCustomerInput {
  return {
    customerNumber: dto.customerNumber,
    name: dto.name,
    type: dto.type,
    status: dto.status,
    email: dto.email as Email | undefined,
    phone: dto.phone as PhoneNumber | undefined,
    website: dto.website,
    address: extractAddress(dto),
    industry: dto.industry,
    companySize: dto.companySize,
    annualRevenue: dto.annualRevenue,
    taxId: dto.taxId,
    vatNumber: dto.vatNumber,
    salesRepId: dto.salesRepId,
    leadSource: dto.leadSource,
    leadScore: dto.leadScore,
    notes: dto.notes,
    tags: dto.tags,
  } as CreateCustomerInput;
}

export function toUpdateCustomerInput(dto: UpdateCustomerDTO): UpdateCustomerInput {
  return {
    customerNumber: dto.customerNumber,
    name: dto.name,
    type: dto.type,
    status: dto.status,
    email: dto.email as Email | undefined,
    phone: dto.phone as PhoneNumber | undefined,
    website: dto.website,
    address: extractAddress(dto),
    industry: dto.industry,
    companySize: dto.companySize,
    annualRevenue: dto.annualRevenue,
    taxId: dto.taxId,
    vatNumber: dto.vatNumber,
    salesRepId: dto.salesRepId,
    leadSource: dto.leadSource,
    leadScore: dto.leadScore,
    notes: dto.notes,
    tags: dto.tags,
  } as UpdateCustomerInput;
}

export function toCustomerFilters(query: GetCustomersQueryLike): CustomerFilters {
  return {
    search: query.search,
    status: query.status,
    type: query.type,
    tags: query.tags,
    limit: query.limit,
    offset: query.offset,
  } as CustomerFilters;
}

export const toCustomerId = (value: string): CustomerId => value as CustomerId;

export interface GetCustomersQueryLike {
  search?: string;
  status?: CustomerFilters['status'];
  type?: CustomerFilters['type'];
  tags?: string[];
  limit?: number;
  offset?: number;
}
