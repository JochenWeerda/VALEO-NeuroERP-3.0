/**
 * Employee Service for VALEO NeuroERP 3.0 HR Domain
 * Business logic for employee management
 */
import { Employee } from '../entities/employee';
import { DepartmentStatistics, EmployeeFilters, EmployeeRepository, PaginatedResult, PaginationOptions } from '../repositories/employee-repository';
import { type HREvent } from '../events';
type DomainEventPublisher = (event: HREvent) => Promise<void>;
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
export interface EmployeeStatistics {
    totalEmployees: number;
    activeEmployees: number;
    inactiveEmployees: number;
    departmentBreakdown: DepartmentStatistics[];
}
export declare class EmployeeService {
    private readonly employeeRepository;
    private readonly eventPublisher;
    private readonly logger;
    constructor(employeeRepository: EmployeeRepository, eventPublisher: DomainEventPublisher);
    createEmployee(command: CreateEmployeeCommand): Promise<Employee>;
    updateEmployee(command: UpdateEmployeeCommand): Promise<Employee>;
    assignRole(command: AssignRoleCommand): Promise<Employee>;
    removeRole(command: RemoveRoleCommand): Promise<Employee>;
    deactivateEmployee(command: DeactivateEmployeeCommand): Promise<Employee>;
    reactivateEmployee(tenantId: string, employeeId: string, updatedBy?: string): Promise<Employee>;
    getEmployee(tenantId: string, employeeId: string): Promise<Employee>;
    listEmployees(tenantId: string, filters?: EmployeeFilters, pagination?: PaginationOptions): Promise<Employee[] | PaginatedResult<Employee>>;
    getEmployeeStatistics(tenantId: string): Promise<EmployeeStatistics>;
}
export {};
//# sourceMappingURL=employee-service.d.ts.map