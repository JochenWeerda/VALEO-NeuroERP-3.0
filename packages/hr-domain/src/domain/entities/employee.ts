/**
 * Employee Entity for VALEO NeuroERP 3.0 HR Domain
 * Core employee management entity with DDD principles
 */

import { v4 as uuidv4 } from 'uuid';
import { z } from 'zod';

const PERSON_NAME_MIN_LENGTH = 1;
const PERSON_NAME_MAX_LENGTH = 100;
const EMPLOYEE_NUMBER_MIN_LENGTH = 1;
const EMPLOYEE_NUMBER_MAX_LENGTH = 50;
const INITIAL_VERSION = 1;
const MANAGER_ROLE_HINTS = ['manager', 'supervisor'] as const;

const employeeStatusSchema = z.enum(['Active', 'Inactive', 'OnLeave']);

// Value Objects
const PersonSchema = z.object({
  firstName: z.string().min(PERSON_NAME_MIN_LENGTH).max(PERSON_NAME_MAX_LENGTH),
  lastName: z.string().min(PERSON_NAME_MIN_LENGTH).max(PERSON_NAME_MAX_LENGTH),
  birthDate: z.string().datetime().optional()
});

const ContactSchema = z.object({
  email: z.string().email().optional(),
  phone: z.string().optional()
});

const EmploymentSchema = z.object({
  hireDate: z.string().datetime(),
  terminationDate: z.string().datetime().optional(),
  type: z.enum(['Full', 'Part', 'Temp'])
});

const OrganizationSchema = z.object({
  departmentId: z.string().uuid().optional(),
  position: z.string().optional(),
  managerId: z.string().uuid().optional()
});

const PayrollSchema = z.object({
  taxClass: z.string().optional(),
  socialSecurityId: z.string().optional(),
  iban: z.string().optional() // Sensible data - mask in logs
});

// Main Employee Schema
export const EmployeeSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  employeeNumber: z.string().min(EMPLOYEE_NUMBER_MIN_LENGTH).max(EMPLOYEE_NUMBER_MAX_LENGTH),
  person: PersonSchema,
  contact: ContactSchema,
  employment: EmploymentSchema,
  org: OrganizationSchema,
  payroll: PayrollSchema,
  status: employeeStatusSchema,
  roles: z.array(z.string()),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  version: z.number().int().min(INITIAL_VERSION),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

export type Employee = z.infer<typeof EmployeeSchema>;
export type Person = z.infer<typeof PersonSchema>;
export type Contact = z.infer<typeof ContactSchema>;
export type Employment = z.infer<typeof EmploymentSchema>;
export type Organization = z.infer<typeof OrganizationSchema>;
export type Payroll = z.infer<typeof PayrollSchema>;
export type EmployeeStatusType = z.infer<typeof employeeStatusSchema>;

// Employee Entity Class
export class EmployeeEntity {
  private readonly data: Employee;

  constructor(data: Employee) {
    this.data = EmployeeSchema.parse(data);
  }

  // Getters
  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get employeeNumber(): string { return this.data.employeeNumber; }
  get person(): Person { return this.data.person; }
  get contact(): Contact { return this.data.contact; }
  get employment(): Employment { return this.data.employment; }
  get org(): Organization { return this.data.org; }
  get payroll(): Payroll { return this.data.payroll; }
  get status(): string { return this.data.status; }
  get roles(): string[] { return [...this.data.roles]; }
  get createdAt(): string { return this.data.createdAt; }
  get updatedAt(): string { return this.data.updatedAt; }
  get version(): number { return this.data.version; }

  // Business Methods
  isActive(): boolean {
    return this.data.status === 'Active';
  }

  isOnLeave(): boolean {
    return this.data.status === 'OnLeave';
  }

  hasRole(roleId: string): boolean {
    return this.data.roles.includes(roleId);
  }

  getFullName(): string {
    return `${this.data.person.firstName} ${this.data.person.lastName}`;
  }

  isManagerOf(employeeId: string): boolean {
    return this.data.org.managerId === employeeId;
  }

  // State Changes
  activate(updatedBy?: string): EmployeeEntity {
    if (this.isActive()) {
      return this;
    }

    return this.clone({ status: 'Active', updatedBy });
  }

  deactivate(updatedBy?: string): EmployeeEntity {
    if (!this.isActive()) {
      return this;
    }

    return this.clone({ status: 'Inactive', updatedBy });
  }

  setOnLeave(updatedBy?: string): EmployeeEntity {
    if (this.isOnLeave()) {
      return this;
    }

    return this.clone({ status: 'OnLeave', updatedBy });
  }

  addRole(roleId: string, updatedBy?: string): EmployeeEntity {
    if (this.hasRole(roleId)) {
      return this;
    }

    return this.clone({
      roles: [...this.data.roles, roleId],
      updatedBy
    });
  }

  removeRole(roleId: string, updatedBy?: string): EmployeeEntity {
    if (!this.hasRole(roleId)) {
      return this;
    }

    return this.clone({
      roles: this.data.roles.filter(role => role !== roleId),
      updatedBy
    });
  }

  updateContact(contact: Partial<Contact>, updatedBy?: string): EmployeeEntity {
    if (Object.keys(contact).length === 0) {
      return this;
    }

    return this.clone({
      contact: { ...this.data.contact, ...contact },
      updatedBy
    });
  }

  updateOrganization(org: Partial<Organization>, updatedBy?: string): EmployeeEntity {
    if (Object.keys(org).length === 0) {
      return this;
    }

    return this.clone({
      org: { ...this.data.org, ...org },
      updatedBy
    });
  }

  terminate(terminationDate: string, updatedBy?: string): EmployeeEntity {
    return this.clone({
      status: 'Inactive',
      employment: { ...this.data.employment, terminationDate },
      updatedBy
    });
  }

  // Validation
  canWork(): boolean {
    return this.isActive() && !this.isOnLeave();
  }

  canManage(): boolean {
    const lowerCaseRoles = this.data.roles.map(role => role.toLowerCase());
    return this.isActive() && lowerCaseRoles.some(role =>
      MANAGER_ROLE_HINTS.some(hint => role.includes(hint))
    );
  }

  // Export for persistence
  toJSON(): Employee {
    return { ...this.data };
  }

  private clone(overrides: Partial<Employee>): EmployeeEntity {
    const now = new Date().toISOString();
    return new EmployeeEntity({
      ...this.data,
      ...overrides,
      updatedAt: now,
      version: this.data.version + 1
    });
  }

  // Factory methods
  static create(data: Omit<Employee, 'id' | 'createdAt' | 'updatedAt' | 'version'>): EmployeeEntity {
    const now = new Date().toISOString();
    return new EmployeeEntity({
      ...data,
      id: uuidv4(),
      createdAt: now,
      updatedAt: now,
      version: INITIAL_VERSION
    });
  }

  static fromJSON(data: Employee): EmployeeEntity {
    return new EmployeeEntity(data);
  }
}
