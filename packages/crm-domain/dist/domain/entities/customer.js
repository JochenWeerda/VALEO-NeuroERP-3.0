"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CustomerEntity = exports.UpdateCustomerInputSchema = exports.CreateCustomerInputSchema = exports.CustomerSchema = exports.AddressSchema = exports.CustomerStatus = void 0;
const zod_1 = require("zod");
const uuid_1 = require("uuid");
// Enums
exports.CustomerStatus = {
    ACTIVE: 'Active',
    PROSPECT: 'Prospect',
    BLOCKED: 'Blocked'
};
// Address Schema
exports.AddressSchema = zod_1.z.object({
    street: zod_1.z.string().min(1),
    city: zod_1.z.string().min(1),
    postalCode: zod_1.z.string().min(1),
    country: zod_1.z.string().min(1),
    state: zod_1.z.string().optional()
});
// Customer Entity Schema
exports.CustomerSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    number: zod_1.z.string().min(1),
    name: zod_1.z.string().min(1),
    vatId: zod_1.z.string().optional(),
    billingAddress: exports.AddressSchema,
    shippingAddresses: zod_1.z.array(exports.AddressSchema).default([]),
    email: zod_1.z.string().email().optional(),
    phone: zod_1.z.string().optional(),
    tags: zod_1.z.array(zod_1.z.string()).default([]),
    status: zod_1.z.enum([exports.CustomerStatus.ACTIVE, exports.CustomerStatus.PROSPECT, exports.CustomerStatus.BLOCKED]),
    ownerUserId: zod_1.z.string().uuid().optional(),
    createdAt: zod_1.z.date(),
    updatedAt: zod_1.z.date(),
    version: zod_1.z.number().int().nonnegative()
});
// Create Customer Input Schema (for API)
exports.CreateCustomerInputSchema = exports.CustomerSchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
    version: true
}).extend({
    shippingAddresses: zod_1.z.array(exports.AddressSchema).optional().default([])
});
// Update Customer Input Schema (for API)
exports.UpdateCustomerInputSchema = zod_1.z.object({
    name: zod_1.z.string().min(1).optional(),
    vatId: zod_1.z.string().nullish(),
    billingAddress: exports.AddressSchema.optional(),
    shippingAddresses: zod_1.z.array(exports.AddressSchema).optional(),
    email: zod_1.z.string().email().nullish(),
    phone: zod_1.z.string().nullish(),
    tags: zod_1.z.array(zod_1.z.string()).optional(),
    status: zod_1.z.enum([exports.CustomerStatus.ACTIVE, exports.CustomerStatus.PROSPECT, exports.CustomerStatus.BLOCKED]).optional(),
    ownerUserId: zod_1.z.string().uuid().nullish()
});
// Customer Aggregate Root
class CustomerEntity {
    props;
    constructor(props) {
        this.props = props;
    }
    static create(props) {
        const now = new Date();
        const customer = {
            ...props,
            id: (0, uuid_1.v4)(),
            status: props.status || exports.CustomerStatus.PROSPECT,
            tags: props.tags || [],
            shippingAddresses: props.shippingAddresses || [],
            createdAt: now,
            updatedAt: now,
            version: 1
        };
        return new CustomerEntity(customer);
    }
    static fromPersistence(props) {
        return new CustomerEntity(props);
    }
    update(props) {
        if (props.name !== undefined) {
            this.props.name = props.name;
        }
        if (props.vatId !== undefined) {
            this.props.vatId = props.vatId;
        }
        if (props.billingAddress !== undefined) {
            this.props.billingAddress = props.billingAddress;
        }
        if (props.shippingAddresses !== undefined) {
            this.props.shippingAddresses = props.shippingAddresses;
        }
        if (props.email !== undefined) {
            this.props.email = props.email;
        }
        if (props.phone !== undefined) {
            this.props.phone = props.phone;
        }
        if (props.tags !== undefined) {
            this.props.tags = props.tags;
        }
        if (props.status !== undefined) {
            this.props.status = props.status;
        }
        if (props.ownerUserId !== undefined) {
            this.props.ownerUserId = props.ownerUserId;
        }
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    changeStatus(newStatus) {
        if (this.props.status !== newStatus) {
            this.props.status = newStatus;
            this.props.updatedAt = new Date();
            this.props.version += 1;
        }
    }
    addTag(tag) {
        if (!this.props.tags.includes(tag)) {
            this.props.tags.push(tag);
            this.props.updatedAt = new Date();
            this.props.version += 1;
        }
    }
    removeTag(tag) {
        const index = this.props.tags.indexOf(tag);
        if (index > -1) {
            this.props.tags.splice(index, 1);
            this.props.updatedAt = new Date();
            this.props.version += 1;
        }
    }
    addShippingAddress(address) {
        this.props.shippingAddresses.push(address);
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    removeShippingAddress(index) {
        if (index >= 0 && index < this.props.shippingAddresses.length) {
            this.props.shippingAddresses.splice(index, 1);
            this.props.updatedAt = new Date();
            this.props.version += 1;
        }
    }
    // Getters
    get id() { return this.props.id; }
    get tenantId() { return this.props.tenantId; }
    get number() { return this.props.number; }
    get name() { return this.props.name; }
    get vatId() { return this.props.vatId; }
    get billingAddress() { return this.props.billingAddress; }
    get shippingAddresses() { return [...this.props.shippingAddresses]; }
    get email() { return this.props.email; }
    get phone() { return this.props.phone; }
    get tags() { return [...this.props.tags]; }
    get status() { return this.props.status; }
    get ownerUserId() { return this.props.ownerUserId; }
    get createdAt() { return this.props.createdAt; }
    get updatedAt() { return this.props.updatedAt; }
    get version() { return this.props.version; }
    // Export for persistence
    toPersistence() {
        return { ...this.props };
    }
    // Export for API responses
    toJSON() {
        const { tenantId, ...customerWithoutTenant } = this.props;
        return customerWithoutTenant;
    }
}
exports.CustomerEntity = CustomerEntity;
//# sourceMappingURL=customer.js.map