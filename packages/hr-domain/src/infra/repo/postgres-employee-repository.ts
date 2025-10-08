/**
 * In-Memory Employee Repository for VALEO NeuroERP 3.0 HR Domain
 * Temporary implementation for development/testing
 */

import { Employee } from '../../domain/entities/employee';
import {
  DepartmentStatistics,
  EmployeeFilters,
  EmployeeRepository,
  PaginatedResult,
  PaginationOptions
} from '../../domain/repositories/employee-repository';

const UNKNOWN_DEPARTMENT_ID = 'unknown';

export class PostgresEmployeeRepository implements EmployeeRepository {
  private readonly employees: Map<string, Employee> = new Map();

  async save(tenantId: string, employee: Employee): Promise<Employee> {
    // Simple in-memory storage
    this.employees.set(employee.id, employee);
    return employee;
  }

  async findById(tenantId: string, id: string): Promise<Employee | null> {
    const employee = this.employees.get(id);
    return employee && employee.tenantId === tenantId ? employee : null;
  }

  async findByEmployeeNumber(tenantId: string, employeeNumber: string): Promise<Employee | null> {
    for (const employee of this.employees.values()) {
      if (employee.tenantId === tenantId && employee.employeeNumber === employeeNumber) {
        return employee;
      }
    }
    return null;
  }

  async findAll(tenantId: string, filters?: EmployeeFilters): Promise<Employee[]> {
    let results = Array.from(this.employees.values()).filter(e => e.tenantId === tenantId);

    if (filters) {
      const { status, departmentId, managerId, roleId, search } = filters;

      if (typeof status === 'string' && status.length > 0) {
        results = results.filter(e => e.status === status);
      }
      if (typeof departmentId === 'string' && departmentId.length > 0) {
        results = results.filter(e => e.org.departmentId === departmentId);
      }
      if (typeof managerId === 'string' && managerId.length > 0) {
        results = results.filter(e => e.org.managerId === managerId);
      }
      if (typeof roleId === 'string' && roleId.length > 0) {
        results = results.filter(e => e.roles.includes(roleId));
      }
      if (typeof search === 'string' && search.length > 0) {
        const normalizedSearch = search.toLowerCase();
        results = results.filter(e =>
          e.person.firstName.toLowerCase().includes(normalizedSearch) ||
          e.person.lastName.toLowerCase().includes(normalizedSearch) ||
          e.employeeNumber.toLowerCase().includes(normalizedSearch)
        );
      }
    }

    return results.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }

  async delete(tenantId: string, id: string): Promise<void> {
    const employee = this.employees.get(id);
    if (employee && employee.tenantId === tenantId) {
      this.employees.delete(id);
    }
  }

  async findByStatus(tenantId: string, status: string): Promise<Employee[]> {
    return Array.from(this.employees.values())
      .filter(e => e.tenantId === tenantId && e.status === status);
  }

  async findByDepartment(tenantId: string, departmentId: string): Promise<Employee[]> {
    return Array.from(this.employees.values())
      .filter(e => e.tenantId === tenantId && e.org.departmentId === departmentId);
  }

  async findByManager(tenantId: string, managerId: string): Promise<Employee[]> {
    return Array.from(this.employees.values())
      .filter(e => e.tenantId === tenantId && e.org.managerId === managerId);
  }

  async findByRole(tenantId: string, roleId: string): Promise<Employee[]> {
    return Array.from(this.employees.values())
      .filter(e => e.tenantId === tenantId && e.roles.includes(roleId));
  }

  async findWithPagination(tenantId: string, options: PaginationOptions): Promise<PaginatedResult<Employee>> {
    const all = await this.findAll(tenantId, options.filters);
    const { page, pageSize } = options;
    const offset = (page - 1) * pageSize;
    const data = all.slice(offset, offset + pageSize);
    
    return {
      data,
      pagination: {
        page,
        pageSize,
        total: all.length,
        totalPages: Math.ceil(all.length / pageSize)
      }
    };
  }

  async bulkSave(tenantId: string, employees: Employee[]): Promise<Employee[]> {
    const saved: Employee[] = [];
    for (const employee of employees) {
      const savedEmployee = await this.save(tenantId, employee);
      saved.push(savedEmployee);
    }
    return saved;
  }

  async bulkDelete(tenantId: string, ids: string[]): Promise<void> {
    for (const id of ids) {
      await this.delete(tenantId, id);
    }
  }

  async getEmployeeCount(tenantId: string, filters?: EmployeeFilters): Promise<number> {
    const all = await this.findAll(tenantId, filters);
    return all.length;
  }

  async getActiveEmployeeCount(tenantId: string): Promise<number> {
    return this.getEmployeeCount(tenantId, { status: 'Active' });
  }

  async getDepartmentStatistics(tenantId: string): Promise<DepartmentStatistics[]> {
    const employees = await this.findAll(tenantId);
    const stats = new Map<string, DepartmentStatistics>();
    
    for (const emp of employees) {
      const deptId = emp.org.departmentId ?? UNKNOWN_DEPARTMENT_ID;
      let stat = stats.get(deptId);
      if (!stat) {
        stat = {
          departmentId: deptId,
          totalEmployees: 0,
          activeEmployees: 0,
          inactiveEmployees: 0,
          onLeaveEmployees: 0
        };
        stats.set(deptId, stat);
      }

      stat.totalEmployees += 1;
      switch (emp.status) {
        case 'Active':
          stat.activeEmployees += 1;
          break;
        case 'Inactive':
          stat.inactiveEmployees += 1;
          break;
        case 'OnLeave':
          stat.onLeaveEmployees += 1;
          break;
      }
    }
    
    return Array.from(stats.values());
  }
}

