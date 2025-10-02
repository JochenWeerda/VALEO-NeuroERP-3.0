"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.toCustomerId = void 0;
exports.toCustomerDTO = toCustomerDTO;
exports.toCreateCustomerInput = toCreateCustomerInput;
exports.toUpdateCustomerInput = toUpdateCustomerInput;
exports.toCustomerFilters = toCustomerFilters;
function extractAddress(dto) {
    const address = {
        street: dto.street,
        city: dto.city,
        postalCode: dto.postalCode,
        country: dto.country,
    };
    const hasValues = Object.values(address).some((value) => typeof value === 'string' && value.trim() !== '');
    return hasValues ? address : undefined;
}
function toCustomerDTO(customer) {
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
    };
}
function toCreateCustomerInput(dto) {
    return {
        customerNumber: dto.customerNumber,
        name: dto.name,
        type: dto.type,
        status: dto.status,
        email: dto.email,
        phone: dto.phone,
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
    };
}
function toUpdateCustomerInput(dto) {
    return {
        customerNumber: dto.customerNumber,
        name: dto.name,
        type: dto.type,
        status: dto.status,
        email: dto.email,
        phone: dto.phone,
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
    };
}
function toCustomerFilters(query) {
    return {
        search: query.search,
        status: query.status,
        type: query.type,
        tags: query.tags,
        limit: query.limit,
        offset: query.offset,
    };
}
const toCustomerId = (value) => value;
exports.toCustomerId = toCustomerId;
//# sourceMappingURL=customer-mapper.js.map