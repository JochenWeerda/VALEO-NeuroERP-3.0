/**
 * Employee Repository Interface for VALEO NeuroERP 3.0 HR Domain
 * Repository pattern with tenant isolation
 */

import { Employee } from '../entities/employee';

export interface EmployeeRepository {
  // Basic CRUD operations
  save(tenantId: string, employee: Employee): Promise<Employee>;
  findById(tenantId: string, id: string): Promise<Employee | null>;
  findByEmployeeNumber(tenantId: string, employeeNumber: string): Promise<Employee | null>;
  findAll(tenantId: string, filters?: EmployeeFilters): Promise<Employee[]>;
  delete(tenantId: string, id: string): Promise<void>;

  // Search and filtering
  findByStatus(tenantId: string, status: string): Promise<Employee[]>;
  findByDepartment(tenantId: string, departmentId: string): Promise<Employee[]>;
  findByManager(tenantId: string, managerId: string): Promise<Employee[]>;
  findByRole(tenantId: string, roleId: string): Promise<Employee[]>;

  // Pagination
  findWithPagination(tenantId: string, options: PaginationOptions): Promise<PaginatedResult<Employee>>;

  // Bulk operations
  bulkSave(tenantId: string, employees: Employee[]): Promise<Employee[]>;
  bulkDelete(tenantId: string, ids: string[]): Promise<void>;

  // Statistics
  getEmployeeCount(tenantId: string, filters?: EmployeeFilters): Promise<number>;
  getActiveEmployeeCount(tenantId: string): Promise<number>;
  getDepartmentStatistics(tenantId: string): Promise<DepartmentStatistics[]>;
}

export interface EmployeeFilters {
  status?: string;
  departmentId?: string;
  managerId?: string;
  roleId?: string;
  search?: string; // Search in name, employeeNumber
  hireDateFrom?: string;
  hireDateTo?: string;
}

export interface PaginationOptions {
  page: number;
  pageSize: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  filters?: EmployeeFilters;
}

export interface PaginatedResult<T> {
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}

export interface DepartmentStatistics {
  departmentId: string;
  departmentName?: string;
  totalEmployees: number;
  activeEmployees: number;
  inactiveEmployees: number;
  onLeaveEmployees: number;
}

