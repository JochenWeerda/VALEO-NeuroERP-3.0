/**
 * Employee Service for VALEO NeuroERP 3.0 HR Domain
 * Business logic for employee management
 */

import pino from 'pino';
import { Employee, EmployeeEntity } from '../entities/employee';
import {
  DepartmentStatistics,
  EmployeeFilters,
  EmployeeRepository,
  PaginatedResult,
  PaginationOptions
} from '../repositories/employee-repository';
import {
  type HREvent,
  createEmployeeCreatedEvent,
  createEmployeeDeactivatedEvent,
  createEmployeeUpdatedEvent
} from '../events';

const employeeServiceLogger = pino({ name: 'employee-service' });

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

export class EmployeeService {
  private readonly logger = employeeServiceLogger;

  constructor(
    private readonly employeeRepository: EmployeeRepository,
    private readonly eventPublisher: DomainEventPublisher
  ) {}

  async createEmployee(command: CreateEmployeeCommand): Promise<Employee> {
    const existingEmployee = await this.employeeRepository.findByEmployeeNumber(
      command.tenantId,
      command.employeeNumber
    );

    if (existingEmployee) {
      throw new Error(`Employee with number ${command.employeeNumber} already exists`);
    }

    const employeeData = {
      tenantId: command.tenantId,
      employeeNumber: command.employeeNumber,
      person: command.person,
      contact: command.contact ?? {},
      employment: command.employment,
      org: command.org ?? {},
      payroll: command.payroll ?? {},
      status: 'Active' as const,
      roles: command.roles ?? [],
      createdBy: command.createdBy,
      updatedBy: command.createdBy
    };

    const employee = EmployeeEntity.create(employeeData);
    const savedEmployee = await this.employeeRepository.save(command.tenantId, employee.toJSON());

    await this.eventPublisher(createEmployeeCreatedEvent(
      {
        employeeId: savedEmployee.id,
        employeeNumber: savedEmployee.employeeNumber,
        firstName: savedEmployee.person.firstName,
        lastName: savedEmployee.person.lastName,
        hireDate: savedEmployee.employment.hireDate,
        departmentId: savedEmployee.org.departmentId,
        position: savedEmployee.org.position
      },
      command.tenantId
    ));

    return savedEmployee;
  }

  async updateEmployee(command: UpdateEmployeeCommand): Promise<Employee> {
    const existingEmployee = await this.employeeRepository.findById(command.tenantId, command.employeeId);

    if (!existingEmployee) {
      throw new Error(`Employee with ID ${command.employeeId} not found`);
    }

    const employee = EmployeeEntity.fromJSON(existingEmployee);
    const previousVersion = employee.toJSON().version;

    let updatedEmployee = employee;

    if (command.updates.contact !== undefined) {
      updatedEmployee = updatedEmployee.updateContact(command.updates.contact, command.updatedBy);
    }

    if (command.updates.org !== undefined) {
      updatedEmployee = updatedEmployee.updateOrganization(command.updates.org, command.updatedBy);
    }

    if (command.updates.payroll !== undefined) {
      this.logger.warn('Payroll updates require special authorization');
    }

    const savedEmployee = await this.employeeRepository.save(command.tenantId, updatedEmployee.toJSON());

    await this.eventPublisher(createEmployeeUpdatedEvent(
      {
        employeeId: savedEmployee.id,
        changes: command.updates,
        previousVersion
      },
      command.tenantId
    ));

    return savedEmployee;
  }

  async assignRole(command: AssignRoleCommand): Promise<Employee> {
    const existingEmployee = await this.employeeRepository.findById(command.tenantId, command.employeeId);

    if (!existingEmployee) {
      throw new Error(`Employee with ID ${command.employeeId} not found`);
    }

    const employee = EmployeeEntity.fromJSON(existingEmployee);
    const updatedEmployee = employee.addRole(command.roleId, command.updatedBy);

    return this.employeeRepository.save(command.tenantId, updatedEmployee.toJSON());
  }

  async removeRole(command: RemoveRoleCommand): Promise<Employee> {
    const existingEmployee = await this.employeeRepository.findById(command.tenantId, command.employeeId);

    if (!existingEmployee) {
      throw new Error(`Employee with ID ${command.employeeId} not found`);
    }

    const employee = EmployeeEntity.fromJSON(existingEmployee);
    const updatedEmployee = employee.removeRole(command.roleId, command.updatedBy);

    return this.employeeRepository.save(command.tenantId, updatedEmployee.toJSON());
  }

  async deactivateEmployee(command: DeactivateEmployeeCommand): Promise<Employee> {
    const existingEmployee = await this.employeeRepository.findById(command.tenantId, command.employeeId);

    if (!existingEmployee) {
      throw new Error(`Employee with ID ${command.employeeId} not found`);
    }

    const employee = EmployeeEntity.fromJSON(existingEmployee);

    if (!employee.isActive()) {
      throw new Error('Employee is already inactive');
    }

    let updatedEmployee = employee.deactivate(command.updatedBy);

    if (typeof command.terminationDate === 'string' && command.terminationDate.length > 0) {
      updatedEmployee = updatedEmployee.terminate(command.terminationDate, command.updatedBy);
    }

    const savedEmployee = await this.employeeRepository.save(command.tenantId, updatedEmployee.toJSON());

    await this.eventPublisher(createEmployeeDeactivatedEvent(
      {
        employeeId: savedEmployee.id,
        reason: command.reason,
        terminationDate: command.terminationDate
      },
      command.tenantId
    ));

    return savedEmployee;
  }

  async reactivateEmployee(tenantId: string, employeeId: string, updatedBy?: string): Promise<Employee> {
    const existingEmployee = await this.employeeRepository.findById(tenantId, employeeId);

    if (!existingEmployee) {
      throw new Error(`Employee with ID ${employeeId} not found`);
    }

    const employee = EmployeeEntity.fromJSON(existingEmployee);

    if (employee.isActive()) {
      throw new Error('Employee is already active');
    }

    const updatedEmployee = employee.activate(updatedBy);
    return this.employeeRepository.save(tenantId, updatedEmployee.toJSON());
  }

  async getEmployee(tenantId: string, employeeId: string): Promise<Employee> {
    const employee = await this.employeeRepository.findById(tenantId, employeeId);

    if (!employee) {
      throw new Error(`Employee with ID ${employeeId} not found`);
    }

    return employee;
  }

  async listEmployees(
    tenantId: string,
    filters?: EmployeeFilters,
    pagination?: PaginationOptions
  ): Promise<Employee[] | PaginatedResult<Employee>> {
    if (pagination !== undefined) {
      return this.employeeRepository.findWithPagination(tenantId, pagination);
    }

    return this.employeeRepository.findAll(tenantId, filters);
  }

  async getEmployeeStatistics(tenantId: string): Promise<EmployeeStatistics> {
    const totalCount = await this.employeeRepository.getEmployeeCount(tenantId);
    const activeCount = await this.employeeRepository.getActiveEmployeeCount(tenantId);
    const departmentStats = await this.employeeRepository.getDepartmentStatistics(tenantId);

    return {
      totalEmployees: totalCount,
      activeEmployees: activeCount,
      inactiveEmployees: totalCount - activeCount,
      departmentBreakdown: departmentStats
    };
  }
}
