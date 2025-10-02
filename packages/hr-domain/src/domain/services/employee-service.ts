/**
 * Employee Service for VALEO NeuroERP 3.0 HR Domain
 * Business logic for employee management
 */

import { EmployeeEntity, Employee } from '../entities/employee';
import { EmployeeRepository } from '../repositories/employee-repository';
import { createEmployeeCreatedEvent, createEmployeeUpdatedEvent, createEmployeeDeactivatedEvent } from '../events';

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

export class EmployeeService {
  constructor(
    private employeeRepository: EmployeeRepository,
    private eventPublisher: (event: any) => Promise<void>
  ) {}

  async createEmployee(command: CreateEmployeeCommand): Promise<Employee> {
    // Check if employee number already exists
    const existingEmployee = await this.employeeRepository.findByEmployeeNumber(
      command.tenantId, 
      command.employeeNumber
    );
    
    if (existingEmployee) {
      throw new Error(`Employee with number ${command.employeeNumber} already exists`);
    }

    // Create new employee
    const employeeData = {
      tenantId: command.tenantId,
      employeeNumber: command.employeeNumber,
      person: command.person,
      contact: command.contact || {},
      employment: command.employment,
      org: command.org || {},
      payroll: command.payroll || {},
      status: 'Active' as const,
      roles: command.roles || [],
      createdBy: command.createdBy,
      updatedBy: command.createdBy
    };

    const employee = EmployeeEntity.create(employeeData);
    const savedEmployee = await this.employeeRepository.save(command.tenantId, employee.toJSON());

    // Publish domain event
    await this.eventPublisher(createEmployeeCreatedEvent({
      employeeId: savedEmployee.id,
      employeeNumber: savedEmployee.employeeNumber,
      firstName: savedEmployee.person.firstName,
      lastName: savedEmployee.person.lastName,
      hireDate: savedEmployee.employment.hireDate,
      departmentId: savedEmployee.org.departmentId,
      position: savedEmployee.org.position
    }, command.tenantId));

    return savedEmployee;
  }

  async updateEmployee(command: UpdateEmployeeCommand): Promise<Employee> {
    const existingEmployee = await this.employeeRepository.findById(command.tenantId, command.employeeId);
    
    if (!existingEmployee) {
      throw new Error(`Employee with ID ${command.employeeId} not found`);
    }

    const employee = EmployeeEntity.fromJSON(existingEmployee);
    const previousVersion = employee.toJSON().version;

    // Apply updates
    let updatedEmployee = employee;
    
    if (command.updates.contact) {
      updatedEmployee = updatedEmployee.updateContact(command.updates.contact, command.updatedBy);
    }
    
    if (command.updates.org) {
      updatedEmployee = updatedEmployee.updateOrganization(command.updates.org, command.updatedBy);
    }

    // Note: Payroll updates might require special permissions
    if (command.updates.payroll) {
      // This would typically involve additional authorization checks
      // For now, we'll skip payroll updates in this example
      console.warn('Payroll updates require special authorization');
    }

    const savedEmployee = await this.employeeRepository.save(command.tenantId, updatedEmployee.toJSON());

    // Publish domain event
    await this.eventPublisher(createEmployeeUpdatedEvent({
      employeeId: savedEmployee.id,
      changes: command.updates,
      previousVersion
    }, command.tenantId));

    return savedEmployee;
  }

  async assignRole(command: AssignRoleCommand): Promise<Employee> {
    const existingEmployee = await this.employeeRepository.findById(command.tenantId, command.employeeId);
    
    if (!existingEmployee) {
      throw new Error(`Employee with ID ${command.employeeId} not found`);
    }

    const employee = EmployeeEntity.fromJSON(existingEmployee);
    const updatedEmployee = employee.addRole(command.roleId, command.updatedBy);

    return await this.employeeRepository.save(command.tenantId, updatedEmployee.toJSON());
  }

  async removeRole(command: RemoveRoleCommand): Promise<Employee> {
    const existingEmployee = await this.employeeRepository.findById(command.tenantId, command.employeeId);
    
    if (!existingEmployee) {
      throw new Error(`Employee with ID ${command.employeeId} not found`);
    }

    const employee = EmployeeEntity.fromJSON(existingEmployee);
    const updatedEmployee = employee.removeRole(command.roleId, command.updatedBy);

    return await this.employeeRepository.save(command.tenantId, updatedEmployee.toJSON());
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
    
    if (command.terminationDate) {
      updatedEmployee = updatedEmployee.terminate(command.terminationDate, command.updatedBy);
    }

    const savedEmployee = await this.employeeRepository.save(command.tenantId, updatedEmployee.toJSON());

    // Publish domain event
    await this.eventPublisher(createEmployeeDeactivatedEvent({
      employeeId: savedEmployee.id,
      reason: command.reason,
      terminationDate: command.terminationDate
    }, command.tenantId));

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
    return await this.employeeRepository.save(tenantId, updatedEmployee.toJSON());
  }

  async getEmployee(tenantId: string, employeeId: string): Promise<Employee> {
    const employee = await this.employeeRepository.findById(tenantId, employeeId);
    
    if (!employee) {
      throw new Error(`Employee with ID ${employeeId} not found`);
    }

    return employee;
  }

  async listEmployees(tenantId: string, filters?: any, pagination?: any): Promise<any> {
    if (pagination) {
      return await this.employeeRepository.findWithPagination(tenantId, pagination);
    }
    
    return await this.employeeRepository.findAll(tenantId, filters);
  }

  async getEmployeeStatistics(tenantId: string): Promise<any> {
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

