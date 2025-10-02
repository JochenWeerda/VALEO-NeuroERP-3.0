"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.toCustomerDTO = toCustomerDTO;
exports.toNewCustomer = toNewCustomer;
exports.toUpdateCustomer = toUpdateCustomer;
exports.toCustomerId = toCustomerId;
const branded_types_1 = require("../../../../../packages/data-models/src/branded-types");
function extractAddress(dto) {
    const address = {
        street: dto.street,
        city: dto.city,
        postalCode: dto.postalCode,
        country: dto.country,
    };
    if (!address.street && !address.city && !address.postalCode && !address.country) {
        return undefined;
    }
    return address;
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
        updatedAt: customer.updatedAt?.toISOString(),
    };
}
function toNewCustomer(dto) {
    return {
        customerNumber: dto.customerNumber,
        name: dto.name,
        type: dto.type,
        status: dto.status,
        email: dto.email ? dto.email : undefined,
        phone: dto.phone ? dto.phone : undefined,
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
function toUpdateCustomer(dto) {
    const updates = {};
    if (dto.customerNumber !== undefined)
        updates.customerNumber = dto.customerNumber;
    if (dto.name !== undefined)
        updates.name = dto.name;
    if (dto.type !== undefined)
        updates.type = dto.type;
    if (dto.status !== undefined)
        updates.status = dto.status;
    if (dto.email !== undefined)
        updates.email = dto.email ? dto.email : undefined;
    if (dto.phone !== undefined)
        updates.phone = dto.phone ? dto.phone : undefined;
    if (dto.website !== undefined)
        updates.website = dto.website;
    const address = extractAddress(dto);
    if (dto.street !== undefined || dto.city !== undefined || dto.postalCode !== undefined || dto.country !== undefined) {
        updates.address = address;
    }
    if (dto.industry !== undefined)
        updates.industry = dto.industry;
    if (dto.companySize !== undefined)
        updates.companySize = dto.companySize;
    if (dto.annualRevenue !== undefined)
        updates.annualRevenue = dto.annualRevenue;
    if (dto.taxId !== undefined)
        updates.taxId = dto.taxId;
    if (dto.vatNumber !== undefined)
        updates.vatNumber = dto.vatNumber;
    if (dto.salesRepId !== undefined)
        updates.salesRepId = dto.salesRepId;
    if (dto.leadSource !== undefined)
        updates.leadSource = dto.leadSource;
    if (dto.leadScore !== undefined)
        updates.leadScore = dto.leadScore;
    if (dto.notes !== undefined)
        updates.notes = dto.notes;
    if (dto.tags !== undefined)
        updates.tags = dto.tags;
    return updates;
}
function toCustomerId(value) {
    return (0, branded_types_1.brandValue)(value, 'CustomerId');
}
