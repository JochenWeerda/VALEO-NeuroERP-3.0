/**
 * Employee Service for VALEO NeuroERP 3.0 HR Domain
 * Business logic for employee management
 */
import { Employee } from '../entities/employee';
import { EmployeeRepository } from '../repositories/employee-repository';
export interface CreateEmployeeCommand {
    tenantId: string;
    employeeNumber: string;
    person: {
        firstName: string;
        lastName: string;
        birthDate?: string;
    };
    contact?: {
        email?: string;
        phone?: string;
    };
    employment: {
        hireDate: string;
        type: 'Full' | 'Part' | 'Temp';
    };
    org?: {
        departmentId?: string;
        position?: string;
        managerId?: string;
    };
    payroll?: {
        taxClass?: string;
        socialSecurityId?: string;
        iban?: string;
    };
    roles?: string[];
    createdBy?: string;
}
export interface UpdateEmployeeCommand {
    tenantId: string;
    employeeId: string;
    updates: {
        contact?: {
            email?: string;
            phone?: string;
        };
        org?: {
            departmentId?: string;
            position?: string;
            managerId?: string;
        };
        payroll?: {
            taxClass?: string;
            socialSecurityId?: string;
            iban?: string;
        };
    };
    updatedBy?: string;
}
export interface AssignRoleCommand {
    tenantId: string;
    employeeId: string;
    roleId: string;
    updatedBy?: string;
}
export interface RemoveRoleCommand {
    tenantId: string;
    employeeId: string;
    roleId: string;
    updatedBy?: string;
}
export interface DeactivateEmployeeCommand {
    tenantId: string;
    employeeId: string;
    reason?: string;
    terminationDate?: string;
    updatedBy?: string;
}
export declare class EmployeeService {
    private employeeRepository;
    private eventPublisher;
    constructor(employeeRepository: EmployeeRepository, eventPublisher: (event: any) => Promise<void>);
    createEmployee(command: CreateEmployeeCommand): Promise<Employee>;
    updateEmployee(command: UpdateEmployeeCommand): Promise<Employee>;
    assignRole(command: AssignRoleCommand): Promise<Employee>;
    removeRole(command: RemoveRoleCommand): Promise<Employee>;
    deactivateEmployee(command: DeactivateEmployeeCommand): Promise<Employee>;
    reactivateEmployee(tenantId: string, employeeId: string, updatedBy?: string): Promise<Employee>;
    getEmployee(tenantId: string, employeeId: string): Promise<Employee>;
    listEmployees(tenantId: string, filters?: any, pagination?: any): Promise<any>;
    getEmployeeStatistics(tenantId: string): Promise<any>;
}
//# sourceMappingURL=employee-service.d.ts.map