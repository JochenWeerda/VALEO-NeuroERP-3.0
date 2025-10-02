/**
 * In-Memory Employee Repository for VALEO NeuroERP 3.0 HR Domain
 * Temporary implementation for development/testing
 */

import { EmployeeRepository, EmployeeFilters, PaginationOptions, PaginatedResult, DepartmentStatistics } from '../../domain/repositories/employee-repository';
import { Employee } from '../../domain/entities/employee';

export class PostgresEmployeeRepository implements EmployeeRepository {
  private employees: Map<string, Employee> = new Map();

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
      if (filters.status) {
        results = results.filter(e => e.status === filters.status);
      }
      if (filters.departmentId) {
        results = results.filter(e => e.org.departmentId === filters.departmentId);
      }
      if (filters.managerId) {
        results = results.filter(e => e.org.managerId === filters.managerId);
      }
      if (filters.roleId) {
        results = results.filter(e => e.roles.includes(filters.roleId!));
      }
      if (filters.search) {
        const search = filters.search.toLowerCase();
        results = results.filter(e => 
          e.person.firstName.toLowerCase().includes(search) ||
          e.person.lastName.toLowerCase().includes(search) ||
          e.employeeNumber.toLowerCase().includes(search)
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
      const deptId = emp.org.departmentId || 'unknown';
      if (!stats.has(deptId)) {
        stats.set(deptId, {
          departmentId: deptId,
          totalEmployees: 0,
          activeEmployees: 0,
          inactiveEmployees: 0,
          onLeaveEmployees: 0
        });
      }
      
      const stat = stats.get(deptId)!;
      stat.totalEmployees++;
      switch (emp.status) {
        case 'Active':
          stat.activeEmployees++;
          break;
        case 'Inactive':
          stat.inactiveEmployees++;
          break;
        case 'OnLeave':
          stat.onLeaveEmployees++;
          break;
      }
    }
    
    return Array.from(stats.values());
  }
}

