/**
 * In-Memory Employee Repository for VALEO NeuroERP 3.0 HR Domain
 * Temporary implementation for development/testing
 */
import { Employee } from '../../domain/entities/employee';
import { DepartmentStatistics, EmployeeFilters, EmployeeRepository, PaginatedResult, PaginationOptions } from '../../domain/repositories/employee-repository';
export declare class PostgresEmployeeRepository implements EmployeeRepository {
    private readonly employees;
    save(tenantId: string, employee: Employee): Promise<Employee>;
    findById(tenantId: string, id: string): Promise<Employee | null>;
    findByEmployeeNumber(tenantId: string, employeeNumber: string): Promise<Employee | null>;
    findAll(tenantId: string, filters?: EmployeeFilters): Promise<Employee[]>;
    delete(tenantId: string, id: string): Promise<void>;
    findByStatus(tenantId: string, status: string): Promise<Employee[]>;
    findByDepartment(tenantId: string, departmentId: string): Promise<Employee[]>;
    findByManager(tenantId: string, managerId: string): Promise<Employee[]>;
    findByRole(tenantId: string, roleId: string): Promise<Employee[]>;
    findWithPagination(tenantId: string, options: PaginationOptions): Promise<PaginatedResult<Employee>>;
    bulkSave(tenantId: string, employees: Employee[]): Promise<Employee[]>;
    bulkDelete(tenantId: string, ids: string[]): Promise<void>;
    getEmployeeCount(tenantId: string, filters?: EmployeeFilters): Promise<number>;
    getActiveEmployeeCount(tenantId: string): Promise<number>;
    getDepartmentStatistics(tenantId: string): Promise<DepartmentStatistics[]>;
}
//# sourceMappingURL=postgres-employee-repository.d.ts.map