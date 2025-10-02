/**
 * Employee Entity for VALEO NeuroERP 3.0 HR Domain
 * Core employee management entity with DDD principles
 */

import { z } from 'zod';

// Value Objects
const PersonSchema = z.object({
  firstName: z.string().min(1).max(100),
  lastName: z.string().min(1).max(100),
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
  departmentId: z.string().optional(),
  position: z.string().optional(),
  managerId: z.string().optional()
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
  employeeNumber: z.string().min(1).max(50),
  person: PersonSchema,
  contact: ContactSchema,
  employment: EmploymentSchema,
  org: OrganizationSchema,
  payroll: PayrollSchema,
  status: z.enum(['Active', 'Inactive', 'OnLeave']),
  roles: z.array(z.string()),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  version: z.number().int().min(1),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

export type Employee = z.infer<typeof EmployeeSchema>;
export type Person = z.infer<typeof PersonSchema>;
export type Contact = z.infer<typeof ContactSchema>;
export type Employment = z.infer<typeof EmploymentSchema>;
export type Organization = z.infer<typeof OrganizationSchema>;
export type Payroll = z.infer<typeof PayrollSchema>;

// Employee Entity Class
export class EmployeeEntity {
  private data: Employee;

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
    return new EmployeeEntity({
      ...this.data,
      status: 'Active',
      updatedAt: new Date().toISOString(),
      updatedBy,
      version: this.data.version + 1
    });
  }

  deactivate(updatedBy?: string): EmployeeEntity {
    return new EmployeeEntity({
      ...this.data,
      status: 'Inactive',
      updatedAt: new Date().toISOString(),
      updatedBy,
      version: this.data.version + 1
    });
  }

  setOnLeave(updatedBy?: string): EmployeeEntity {
    return new EmployeeEntity({
      ...this.data,
      status: 'OnLeave',
      updatedAt: new Date().toISOString(),
      updatedBy,
      version: this.data.version + 1
    });
  }

  addRole(roleId: string, updatedBy?: string): EmployeeEntity {
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

  removeRole(roleId: string, updatedBy?: string): EmployeeEntity {
    return new EmployeeEntity({
      ...this.data,
      roles: this.data.roles.filter(r => r !== roleId),
      updatedAt: new Date().toISOString(),
      updatedBy,
      version: this.data.version + 1
    });
  }

  updateContact(contact: Partial<Contact>, updatedBy?: string): EmployeeEntity {
    return new EmployeeEntity({
      ...this.data,
      contact: { ...this.data.contact, ...contact },
      updatedAt: new Date().toISOString(),
      updatedBy,
      version: this.data.version + 1
    });
  }

  updateOrganization(org: Partial<Organization>, updatedBy?: string): EmployeeEntity {
    return new EmployeeEntity({
      ...this.data,
      org: { ...this.data.org, ...org },
      updatedAt: new Date().toISOString(),
      updatedBy,
      version: this.data.version + 1
    });
  }

  terminate(terminationDate: string, updatedBy?: string): EmployeeEntity {
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
  canWork(): boolean {
    return this.isActive() && !this.isOnLeave();
  }

  canManage(): boolean {
    return this.isActive() && this.data.roles.some(role => 
      role.includes('manager') || role.includes('supervisor')
    );
  }

  // Export for persistence
  toJSON(): Employee {
    return { ...this.data };
  }

  // Factory methods
  static create(data: Omit<Employee, 'id' | 'createdAt' | 'updatedAt' | 'version'>): EmployeeEntity {
    const now = new Date().toISOString();
    return new EmployeeEntity({
      ...data,
      id: require('uuid').v4(),
      createdAt: now,
      updatedAt: now,
      version: 1
    });
  }

  static fromJSON(data: Employee): EmployeeEntity {
    return new EmployeeEntity(data);
  }
}

