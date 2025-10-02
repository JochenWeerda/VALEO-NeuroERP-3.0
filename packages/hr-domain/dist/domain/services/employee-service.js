"use strict";
/**
 * Employee Service for VALEO NeuroERP 3.0 HR Domain
 * Business logic for employee management
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.EmployeeService = void 0;
const employee_1 = require("../entities/employee");
const events_1 = require("../events");
class EmployeeService {
    employeeRepository;
    eventPublisher;
    constructor(employeeRepository, eventPublisher) {
        this.employeeRepository = employeeRepository;
        this.eventPublisher = eventPublisher;
    }
    async createEmployee(command) {
        // Check if employee number already exists
        const existingEmployee = await this.employeeRepository.findByEmployeeNumber(command.tenantId, command.employeeNumber);
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
            status: 'Active',
            roles: command.roles || [],
            createdBy: command.createdBy,
            updatedBy: command.createdBy
        };
        const employee = employee_1.EmployeeEntity.create(employeeData);
        const savedEmployee = await this.employeeRepository.save(command.tenantId, employee.toJSON());
        // Publish domain event
        await this.eventPublisher((0, events_1.createEmployeeCreatedEvent)({
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
    async updateEmployee(command) {
        const existingEmployee = await this.employeeRepository.findById(command.tenantId, command.employeeId);
        if (!existingEmployee) {
            throw new Error(`Employee with ID ${command.employeeId} not found`);
        }
        const employee = employee_1.EmployeeEntity.fromJSON(existingEmployee);
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
        await this.eventPublisher((0, events_1.createEmployeeUpdatedEvent)({
            employeeId: savedEmployee.id,
            changes: command.updates,
            previousVersion
        }, command.tenantId));
        return savedEmployee;
    }
    async assignRole(command) {
        const existingEmployee = await this.employeeRepository.findById(command.tenantId, command.employeeId);
        if (!existingEmployee) {
            throw new Error(`Employee with ID ${command.employeeId} not found`);
        }
        const employee = employee_1.EmployeeEntity.fromJSON(existingEmployee);
        const updatedEmployee = employee.addRole(command.roleId, command.updatedBy);
        return await this.employeeRepository.save(command.tenantId, updatedEmployee.toJSON());
    }
    async removeRole(command) {
        const existingEmployee = await this.employeeRepository.findById(command.tenantId, command.employeeId);
        if (!existingEmployee) {
            throw new Error(`Employee with ID ${command.employeeId} not found`);
        }
        const employee = employee_1.EmployeeEntity.fromJSON(existingEmployee);
        const updatedEmployee = employee.removeRole(command.roleId, command.updatedBy);
        return await this.employeeRepository.save(command.tenantId, updatedEmployee.toJSON());
    }
    async deactivateEmployee(command) {
        const existingEmployee = await this.employeeRepository.findById(command.tenantId, command.employeeId);
        if (!existingEmployee) {
            throw new Error(`Employee with ID ${command.employeeId} not found`);
        }
        const employee = employee_1.EmployeeEntity.fromJSON(existingEmployee);
        if (!employee.isActive()) {
            throw new Error('Employee is already inactive');
        }
        let updatedEmployee = employee.deactivate(command.updatedBy);
        if (command.terminationDate) {
            updatedEmployee = updatedEmployee.terminate(command.terminationDate, command.updatedBy);
        }
        const savedEmployee = await this.employeeRepository.save(command.tenantId, updatedEmployee.toJSON());
        // Publish domain event
        await this.eventPublisher((0, events_1.createEmployeeDeactivatedEvent)({
            employeeId: savedEmployee.id,
            reason: command.reason,
            terminationDate: command.terminationDate
        }, command.tenantId));
        return savedEmployee;
    }
    async reactivateEmployee(tenantId, employeeId, updatedBy) {
        const existingEmployee = await this.employeeRepository.findById(tenantId, employeeId);
        if (!existingEmployee) {
            throw new Error(`Employee with ID ${employeeId} not found`);
        }
        const employee = employee_1.EmployeeEntity.fromJSON(existingEmployee);
        if (employee.isActive()) {
            throw new Error('Employee is already active');
        }
        const updatedEmployee = employee.activate(updatedBy);
        return await this.employeeRepository.save(tenantId, updatedEmployee.toJSON());
    }
    async getEmployee(tenantId, employeeId) {
        const employee = await this.employeeRepository.findById(tenantId, employeeId);
        if (!employee) {
            throw new Error(`Employee with ID ${employeeId} not found`);
        }
        return employee;
    }
    async listEmployees(tenantId, filters, pagination) {
        if (pagination) {
            return await this.employeeRepository.findWithPagination(tenantId, pagination);
        }
        return await this.employeeRepository.findAll(tenantId, filters);
    }
    async getEmployeeStatistics(tenantId) {
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
exports.EmployeeService = EmployeeService;
//# sourceMappingURL=employee-service.js.map