"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ContactEntity = exports.UpdateContactInputSchema = exports.CreateContactInputSchema = exports.ContactSchema = void 0;
const zod_1 = require("zod");
const uuid_1 = require("uuid");
// Contact Entity Schema
exports.ContactSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    customerId: zod_1.z.string().uuid(),
    firstName: zod_1.z.string().min(1),
    lastName: zod_1.z.string().min(1),
    role: zod_1.z.string().optional(),
    email: zod_1.z.string().email(),
    phone: zod_1.z.string().optional(),
    isPrimary: zod_1.z.boolean().default(false),
    notes: zod_1.z.string().optional(),
    createdAt: zod_1.z.date(),
    updatedAt: zod_1.z.date(),
    version: zod_1.z.number().int().nonnegative()
});
// Create Contact Input Schema (for API)
exports.CreateContactInputSchema = exports.ContactSchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
    version: true
});
// Update Contact Input Schema (for API)
exports.UpdateContactInputSchema = zod_1.z.object({
    firstName: zod_1.z.string().min(1).optional(),
    lastName: zod_1.z.string().min(1).optional(),
    role: zod_1.z.string().nullish(),
    email: zod_1.z.string().email().optional(),
    phone: zod_1.z.string().nullish(),
    isPrimary: zod_1.z.boolean().optional(),
    notes: zod_1.z.string().nullish()
});
// Contact Aggregate Root
class ContactEntity {
    props;
    constructor(props) {
        this.props = props;
    }
    static create(props) {
        const now = new Date();
        const contact = {
            ...props,
            id: (0, uuid_1.v4)(),
            isPrimary: props.isPrimary || false,
            createdAt: now,
            updatedAt: now,
            version: 1
        };
        return new ContactEntity(contact);
    }
    static fromPersistence(props) {
        return new ContactEntity(props);
    }
    update(props) {
        if (props.firstName !== undefined) {
            this.props.firstName = props.firstName;
        }
        if (props.lastName !== undefined) {
            this.props.lastName = props.lastName;
        }
        if (props.role !== undefined) {
            this.props.role = props.role;
        }
        if (props.email !== undefined) {
            this.props.email = props.email;
        }
        if (props.phone !== undefined) {
            this.props.phone = props.phone;
        }
        if (props.isPrimary !== undefined) {
            this.props.isPrimary = props.isPrimary;
        }
        if (props.notes !== undefined) {
            this.props.notes = props.notes;
        }
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    makePrimary() {
        this.props.isPrimary = true;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    makeSecondary() {
        this.props.isPrimary = false;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    updateNotes(notes) {
        this.props.notes = notes;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    // Getters
    get id() { return this.props.id; }
    get tenantId() { return this.props.tenantId; }
    get customerId() { return this.props.customerId; }
    get firstName() { return this.props.firstName; }
    get lastName() { return this.props.lastName; }
    get fullName() { return `${this.props.firstName} ${this.props.lastName}`; }
    get role() { return this.props.role; }
    get email() { return this.props.email; }
    get phone() { return this.props.phone; }
    get isPrimary() { return this.props.isPrimary; }
    get notes() { return this.props.notes; }
    get createdAt() { return this.props.createdAt; }
    get updatedAt() { return this.props.updatedAt; }
    get version() { return this.props.version; }
    // Export for persistence
    toPersistence() {
        return { ...this.props };
    }
    // Export for API responses
    toJSON() {
        const { tenantId, ...contactWithoutTenant } = this.props;
        return contactWithoutTenant;
    }
}
exports.ContactEntity = ContactEntity;
//# sourceMappingURL=contact.js.map