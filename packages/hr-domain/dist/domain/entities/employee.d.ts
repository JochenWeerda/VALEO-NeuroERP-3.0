/**
 * Employee Entity for VALEO NeuroERP 3.0 HR Domain
 * Core employee management entity with DDD principles
 */
import { z } from 'zod';
declare const employeeStatusSchema: z.ZodEnum<["Active", "Inactive", "OnLeave"]>;
declare const PersonSchema: z.ZodObject<{
    firstName: z.ZodString;
    lastName: z.ZodString;
    birthDate: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    firstName: string;
    lastName: string;
    birthDate?: string | undefined;
}, {
    firstName: string;
    lastName: string;
    birthDate?: string | undefined;
}>;
declare const ContactSchema: z.ZodObject<{
    email: z.ZodOptional<z.ZodString>;
    phone: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    email?: string | undefined;
    phone?: string | undefined;
}, {
    email?: string | undefined;
    phone?: string | undefined;
}>;
declare const EmploymentSchema: z.ZodObject<{
    hireDate: z.ZodString;
    terminationDate: z.ZodOptional<z.ZodString>;
    type: z.ZodEnum<["Full", "Part", "Temp"]>;
}, "strip", z.ZodTypeAny, {
    type: "Full" | "Part" | "Temp";
    hireDate: string;
    terminationDate?: string | undefined;
}, {
    type: "Full" | "Part" | "Temp";
    hireDate: string;
    terminationDate?: string | undefined;
}>;
declare const OrganizationSchema: z.ZodObject<{
    departmentId: z.ZodOptional<z.ZodString>;
    position: z.ZodOptional<z.ZodString>;
    managerId: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    departmentId?: string | undefined;
    position?: string | undefined;
    managerId?: string | undefined;
}, {
    departmentId?: string | undefined;
    position?: string | undefined;
    managerId?: string | undefined;
}>;
declare const PayrollSchema: z.ZodObject<{
    taxClass: z.ZodOptional<z.ZodString>;
    socialSecurityId: z.ZodOptional<z.ZodString>;
    iban: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    taxClass?: string | undefined;
    socialSecurityId?: string | undefined;
    iban?: string | undefined;
}, {
    taxClass?: string | undefined;
    socialSecurityId?: string | undefined;
    iban?: string | undefined;
}>;
export declare const EmployeeSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    employeeNumber: z.ZodString;
    person: z.ZodObject<{
        firstName: z.ZodString;
        lastName: z.ZodString;
        birthDate: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        firstName: string;
        lastName: string;
        birthDate?: string | undefined;
    }, {
        firstName: string;
        lastName: string;
        birthDate?: string | undefined;
    }>;
    contact: z.ZodObject<{
        email: z.ZodOptional<z.ZodString>;
        phone: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        email?: string | undefined;
        phone?: string | undefined;
    }, {
        email?: string | undefined;
        phone?: string | undefined;
    }>;
    employment: z.ZodObject<{
        hireDate: z.ZodString;
        terminationDate: z.ZodOptional<z.ZodString>;
        type: z.ZodEnum<["Full", "Part", "Temp"]>;
    }, "strip", z.ZodTypeAny, {
        type: "Full" | "Part" | "Temp";
        hireDate: string;
        terminationDate?: string | undefined;
    }, {
        type: "Full" | "Part" | "Temp";
        hireDate: string;
        terminationDate?: string | undefined;
    }>;
    org: z.ZodObject<{
        departmentId: z.ZodOptional<z.ZodString>;
        position: z.ZodOptional<z.ZodString>;
        managerId: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        departmentId?: string | undefined;
        position?: string | undefined;
        managerId?: string | undefined;
    }, {
        departmentId?: string | undefined;
        position?: string | undefined;
        managerId?: string | undefined;
    }>;
    payroll: z.ZodObject<{
        taxClass: z.ZodOptional<z.ZodString>;
        socialSecurityId: z.ZodOptional<z.ZodString>;
        iban: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        taxClass?: string | undefined;
        socialSecurityId?: string | undefined;
        iban?: string | undefined;
    }, {
        taxClass?: string | undefined;
        socialSecurityId?: string | undefined;
        iban?: string | undefined;
    }>;
    status: z.ZodEnum<["Active", "Inactive", "OnLeave"]>;
    roles: z.ZodArray<z.ZodString, "many">;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    version: z.ZodNumber;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    status: "Active" | "Inactive" | "OnLeave";
    id: string;
    tenantId: string;
    employeeNumber: string;
    person: {
        firstName: string;
        lastName: string;
        birthDate?: string | undefined;
    };
    contact: {
        email?: string | undefined;
        phone?: string | undefined;
    };
    employment: {
        type: "Full" | "Part" | "Temp";
        hireDate: string;
        terminationDate?: string | undefined;
    };
    org: {
        departmentId?: string | undefined;
        position?: string | undefined;
        managerId?: string | undefined;
    };
    payroll: {
        taxClass?: string | undefined;
        socialSecurityId?: string | undefined;
        iban?: string | undefined;
    };
    roles: string[];
    createdAt: string;
    updatedAt: string;
    version: number;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
}, {
    status: "Active" | "Inactive" | "OnLeave";
    id: string;
    tenantId: string;
    employeeNumber: string;
    person: {
        firstName: string;
        lastName: string;
        birthDate?: string | undefined;
    };
    contact: {
        email?: string | undefined;
        phone?: string | undefined;
    };
    employment: {
        type: "Full" | "Part" | "Temp";
        hireDate: string;
        terminationDate?: string | undefined;
    };
    org: {
        departmentId?: string | undefined;
        position?: string | undefined;
        managerId?: string | undefined;
    };
    payroll: {
        taxClass?: string | undefined;
        socialSecurityId?: string | undefined;
        iban?: string | undefined;
    };
    roles: string[];
    createdAt: string;
    updatedAt: string;
    version: number;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
}>;
export type Employee = z.infer<typeof EmployeeSchema>;
export type Person = z.infer<typeof PersonSchema>;
export type Contact = z.infer<typeof ContactSchema>;
export type Employment = z.infer<typeof EmploymentSchema>;
export type Organization = z.infer<typeof OrganizationSchema>;
export type Payroll = z.infer<typeof PayrollSchema>;
export type EmployeeStatusType = z.infer<typeof employeeStatusSchema>;
export declare class EmployeeEntity {
    private readonly data;
    constructor(data: Employee);
    get id(): string;
    get tenantId(): string;
    get employeeNumber(): string;
    get person(): Person;
    get contact(): Contact;
    get employment(): Employment;
    get org(): Organization;
    get payroll(): Payroll;
    get status(): string;
    get roles(): string[];
    get createdAt(): string;
    get updatedAt(): string;
    get version(): number;
    isActive(): boolean;
    isOnLeave(): boolean;
    hasRole(roleId: string): boolean;
    getFullName(): string;
    isManagerOf(employeeId: string): boolean;
    activate(updatedBy?: string): EmployeeEntity;
    deactivate(updatedBy?: string): EmployeeEntity;
    setOnLeave(updatedBy?: string): EmployeeEntity;
    addRole(roleId: string, updatedBy?: string): EmployeeEntity;
    removeRole(roleId: string, updatedBy?: string): EmployeeEntity;
    updateContact(contact: Partial<Contact>, updatedBy?: string): EmployeeEntity;
    updateOrganization(org: Partial<Organization>, updatedBy?: string): EmployeeEntity;
    terminate(terminationDate: string, updatedBy?: string): EmployeeEntity;
    canWork(): boolean;
    canManage(): boolean;
    toJSON(): Employee;
    private clone;
    static create(data: Omit<Employee, 'id' | 'createdAt' | 'updatedAt' | 'version'>): EmployeeEntity;
    static fromJSON(data: Employee): EmployeeEntity;
}
export {};
//# sourceMappingURL=employee.d.ts.map