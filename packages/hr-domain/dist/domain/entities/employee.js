"use strict";
/**
 * Employee Entity for VALEO NeuroERP 3.0 HR Domain
 * Core employee management entity with DDD principles
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.EmployeeEntity = exports.EmployeeSchema = void 0;
const zod_1 = require("zod");
// Value Objects
const PersonSchema = zod_1.z.object({
    firstName: zod_1.z.string().min(1).max(100),
    lastName: zod_1.z.string().min(1).max(100),
    birthDate: zod_1.z.string().datetime().optional()
});
const ContactSchema = zod_1.z.object({
    email: zod_1.z.string().email().optional(),
    phone: zod_1.z.string().optional()
});
const EmploymentSchema = zod_1.z.object({
    hireDate: zod_1.z.string().datetime(),
    terminationDate: zod_1.z.string().datetime().optional(),
    type: zod_1.z.enum(['Full', 'Part', 'Temp'])
});
const OrganizationSchema = zod_1.z.object({
    departmentId: zod_1.z.string().optional(),
    position: zod_1.z.string().optional(),
    managerId: zod_1.z.string().optional()
});
const PayrollSchema = zod_1.z.object({
    taxClass: zod_1.z.string().optional(),
    socialSecurityId: zod_1.z.string().optional(),
    iban: zod_1.z.string().optional() // Sensible data - mask in logs
});
// Main Employee Schema
exports.EmployeeSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    employeeNumber: zod_1.z.string().min(1).max(50),
    person: PersonSchema,
    contact: ContactSchema,
    employment: EmploymentSchema,
    org: OrganizationSchema,
    payroll: PayrollSchema,
    status: zod_1.z.enum(['Active', 'Inactive', 'OnLeave']),
    roles: zod_1.z.array(zod_1.z.string()),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    version: zod_1.z.number().int().min(1),
    createdBy: zod_1.z.string().optional(),
    updatedBy: zod_1.z.string().optional()
});
// Employee Entity Class
class EmployeeEntity {
    data;
    constructor(data) {
        this.data = exports.EmployeeSchema.parse(data);
    }
    // Getters
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get employeeNumber() { return this.data.employeeNumber; }
    get person() { return this.data.person; }
    get contact() { return this.data.contact; }
    get employment() { return this.data.employment; }
    get org() { return this.data.org; }
    get payroll() { return this.data.payroll; }
    get status() { return this.data.status; }
    get roles() { return [...this.data.roles]; }
    get createdAt() { return this.data.createdAt; }
    get updatedAt() { return this.data.updatedAt; }
    get version() { return this.data.version; }
    // Business Methods
    isActive() {
        return this.data.status === 'Active';
    }
    isOnLeave() {
        return this.data.status === 'OnLeave';
    }
    hasRole(roleId) {
        return this.data.roles.includes(roleId);
    }
    getFullName() {
        return `${this.data.person.firstName} ${this.data.person.lastName}`;
    }
    isManagerOf(employeeId) {
        return this.data.org.managerId === employeeId;
    }
    // State Changes
    activate(updatedBy) {
        return new EmployeeEntity({
            ...this.data,
            status: 'Active',
            updatedAt: new Date().toISOString(),
            updatedBy,
            version: this.data.version + 1
        });
    }
    deactivate(updatedBy) {
        return new EmployeeEntity({
            ...this.data,
            status: 'Inactive',
            updatedAt: new Date().toISOString(),
            updatedBy,
            version: this.data.version + 1
        });
    }
    setOnLeave(updatedBy) {
        return new EmployeeEntity({
            ...this.data,
            status: 'OnLeave',
            updatedAt: new Date().toISOString(),
            updatedBy,
            version: this.data.version + 1
        });
    }
    addRole(roleId, updatedBy) {
        if (this.hasRole(roleId)) {
            return this;
        }
        return new EmployeeEntity({
            ...this.data,
            roles: [...this.data.roles, roleId],
            updatedAt: new Date().toISOString(),
            updatedBy,
            version: this.data.version + 1
        });
    }
    removeRole(roleId, updatedBy) {
        return new EmployeeEntity({
            ...this.data,
            roles: this.data.roles.filter(r => r !== roleId),
            updatedAt: new Date().toISOString(),
            updatedBy,
            version: this.data.version + 1
        });
    }
    updateContact(contact, updatedBy) {
        return new EmployeeEntity({
            ...this.data,
            contact: { ...this.data.contact, ...contact },
            updatedAt: new Date().toISOString(),
            updatedBy,
            version: this.data.version + 1
        });
    }
    updateOrganization(org, updatedBy) {
        return new EmployeeEntity({
            ...this.data,
            org: { ...this.data.org, ...org },
            updatedAt: new Date().toISOString(),
            updatedBy,
            version: this.data.version + 1
        });
    }
    terminate(terminationDate, updatedBy) {
        return new EmployeeEntity({
            ...this.data,
            employment: { ...this.data.employment, terminationDate },
            status: 'Inactive',
            updatedAt: new Date().toISOString(),
            updatedBy,
            version: this.data.version + 1
        });
    }
    // Validation
    canWork() {
        return this.isActive() && !this.isOnLeave();
    }
    canManage() {
        return this.isActive() && this.data.roles.some(role => role.includes('manager') || role.includes('supervisor'));
    }
    // Export for persistence
    toJSON() {
        return { ...this.data };
    }
    // Factory methods
    static create(data) {
        const now = new Date().toISOString();
        return new EmployeeEntity({
            ...data,
            id: require('uuid').v4(),
            createdAt: now,
            updatedAt: now,
            version: 1
        });
    }
    static fromJSON(data) {
        return new EmployeeEntity(data);
    }
}
exports.EmployeeEntity = EmployeeEntity;
//# sourceMappingURL=employee.js.map