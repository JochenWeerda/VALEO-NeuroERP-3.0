"use strict";
/**
 * Employee Entity for VALEO NeuroERP 3.0 HR Domain
 * Core employee management entity with DDD principles
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.EmployeeEntity = exports.EmployeeSchema = void 0;
const uuid_1 = require("uuid");
const zod_1 = require("zod");
const PERSON_NAME_MIN_LENGTH = 1;
const PERSON_NAME_MAX_LENGTH = 100;
const EMPLOYEE_NUMBER_MIN_LENGTH = 1;
const EMPLOYEE_NUMBER_MAX_LENGTH = 50;
const INITIAL_VERSION = 1;
const MANAGER_ROLE_HINTS = ['manager', 'supervisor'];
const employeeStatusSchema = zod_1.z.enum(['Active', 'Inactive', 'OnLeave']);
// Value Objects
const PersonSchema = zod_1.z.object({
    firstName: zod_1.z.string().min(PERSON_NAME_MIN_LENGTH).max(PERSON_NAME_MAX_LENGTH),
    lastName: zod_1.z.string().min(PERSON_NAME_MIN_LENGTH).max(PERSON_NAME_MAX_LENGTH),
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
    departmentId: zod_1.z.string().uuid().optional(),
    position: zod_1.z.string().optional(),
    managerId: zod_1.z.string().uuid().optional()
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
    employeeNumber: zod_1.z.string().min(EMPLOYEE_NUMBER_MIN_LENGTH).max(EMPLOYEE_NUMBER_MAX_LENGTH),
    person: PersonSchema,
    contact: ContactSchema,
    employment: EmploymentSchema,
    org: OrganizationSchema,
    payroll: PayrollSchema,
    status: employeeStatusSchema,
    roles: zod_1.z.array(zod_1.z.string()),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    version: zod_1.z.number().int().min(INITIAL_VERSION),
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
        if (this.isActive()) {
            return this;
        }
        return this.clone({ status: 'Active', updatedBy });
    }
    deactivate(updatedBy) {
        if (!this.isActive()) {
            return this;
        }
        return this.clone({ status: 'Inactive', updatedBy });
    }
    setOnLeave(updatedBy) {
        if (this.isOnLeave()) {
            return this;
        }
        return this.clone({ status: 'OnLeave', updatedBy });
    }
    addRole(roleId, updatedBy) {
        if (this.hasRole(roleId)) {
            return this;
        }
        return this.clone({
            roles: [...this.data.roles, roleId],
            updatedBy
        });
    }
    removeRole(roleId, updatedBy) {
        if (!this.hasRole(roleId)) {
            return this;
        }
        return this.clone({
            roles: this.data.roles.filter(role => role !== roleId),
            updatedBy
        });
    }
    updateContact(contact, updatedBy) {
        if (Object.keys(contact).length === 0) {
            return this;
        }
        return this.clone({
            contact: { ...this.data.contact, ...contact },
            updatedBy
        });
    }
    updateOrganization(org, updatedBy) {
        if (Object.keys(org).length === 0) {
            return this;
        }
        return this.clone({
            org: { ...this.data.org, ...org },
            updatedBy
        });
    }
    terminate(terminationDate, updatedBy) {
        return this.clone({
            status: 'Inactive',
            employment: { ...this.data.employment, terminationDate },
            updatedBy
        });
    }
    // Validation
    canWork() {
        return this.isActive() && !this.isOnLeave();
    }
    canManage() {
        const lowerCaseRoles = this.data.roles.map(role => role.toLowerCase());
        return this.isActive() && lowerCaseRoles.some(role => MANAGER_ROLE_HINTS.some(hint => role.includes(hint)));
    }
    // Export for persistence
    toJSON() {
        return { ...this.data };
    }
    clone(overrides) {
        const now = new Date().toISOString();
        return new EmployeeEntity({
            ...this.data,
            ...overrides,
            updatedAt: now,
            version: this.data.version + 1
        });
    }
    // Factory methods
    static create(data) {
        const now = new Date().toISOString();
        return new EmployeeEntity({
            ...data,
            id: (0, uuid_1.v4)(),
            createdAt: now,
            updatedAt: now,
            version: INITIAL_VERSION
        });
    }
    static fromJSON(data) {
        return new EmployeeEntity(data);
    }
}
exports.EmployeeEntity = EmployeeEntity;
//# sourceMappingURL=employee.js.map