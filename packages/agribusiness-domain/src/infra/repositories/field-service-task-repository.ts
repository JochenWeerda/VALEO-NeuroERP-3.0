/**
 * Field Service Task Repository
 * Data access layer for Field Service Task entities
 */

import { FieldServiceTask, FieldServiceTaskStatus, FieldServiceTaskType } from '../../domain/entities/field-service-task';
import {
  FieldServiceTaskRepository as IFieldServiceTaskRepository,
  FieldServiceTaskFilters,
  PaginationOptions,
  SortOptions,
} from '../../domain/services/mobile-field-service-service';

// In-memory implementation (would be replaced with database in production)
export class FieldServiceTaskRepository implements IFieldServiceTaskRepository {
  private tasks: Map<string, FieldServiceTask> = new Map();

  async findById(id: string): Promise<FieldServiceTask | null> {
    return this.tasks.get(id) || null;
  }

  async findByTaskNumber(taskNumber: string): Promise<FieldServiceTask | null> {
    for (const task of this.tasks.values()) {
      if (task.taskNumber === taskNumber) {
        return task;
      }
    }
    return null;
  }

  async findMany(
    filters: FieldServiceTaskFilters,
    pagination: PaginationOptions,
    sort: SortOptions
  ): Promise<{ data: FieldServiceTask[]; total: number }> {
    let filtered = Array.from(this.tasks.values());

    // Apply filters
    if (filters.taskNumber) {
      filtered = filtered.filter(t => t.taskNumber.includes(filters.taskNumber!));
    }
    if (filters.taskType) {
      filtered = filtered.filter(t => t.taskType === filters.taskType);
    }
    if (filters.status) {
      filtered = filtered.filter(t => t.status === filters.status);
    }
    if (filters.priority) {
      filtered = filtered.filter(t => t.priority === filters.priority);
    }
    if (filters.assignedToId) {
      filtered = filtered.filter(t => t.assignedToId === filters.assignedToId);
    }
    if (filters.farmerId) {
      filtered = filtered.filter(t => t.farmerId === filters.farmerId);
    }
    if (filters.scheduledStartDateFrom) {
      filtered = filtered.filter(t => t.scheduledStartDate >= filters.scheduledStartDateFrom!);
    }
    if (filters.scheduledStartDateTo) {
      filtered = filtered.filter(t => t.scheduledStartDate <= filters.scheduledStartDateTo!);
    }
    if (filters.relatedBatchId) {
      filtered = filtered.filter(t => t.relatedBatchId === filters.relatedBatchId);
    }
    if (filters.relatedContractId) {
      filtered = filtered.filter(t => t.relatedContractId === filters.relatedContractId);
    }
    if (filters.isBillable !== undefined) {
      filtered = filtered.filter(t => t.isBillable === filters.isBillable);
    }
    if (filters.requiresReview) {
      filtered = filtered.filter(t => t.status === 'REQUIRES_REVIEW');
    }
    if (filters.tags && filters.tags.length > 0) {
      filtered = filtered.filter(t =>
        filters.tags!.some(tag => t.tags.includes(tag))
      );
    }
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(t =>
        t.title.toLowerCase().includes(searchLower) ||
        t.description?.toLowerCase().includes(searchLower) ||
        t.taskNumber.includes(searchLower) ||
        t.assignedToName.toLowerCase().includes(searchLower) ||
        t.farmerName?.toLowerCase().includes(searchLower)
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sort.field) {
        case 'scheduledStartDate':
          aValue = a.scheduledStartDate.getTime();
          bValue = b.scheduledStartDate.getTime();
          break;
        case 'priority':
          const priorityOrder = { URGENT: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
          aValue = priorityOrder[a.priority as keyof typeof priorityOrder] || 0;
          bValue = priorityOrder[b.priority as keyof typeof priorityOrder] || 0;
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        case 'createdAt':
          aValue = a.createdAt.getTime();
          bValue = b.createdAt.getTime();
          break;
        case 'updatedAt':
          aValue = a.updatedAt.getTime();
          bValue = b.updatedAt.getTime();
          break;
        default:
          aValue = a.scheduledStartDate.getTime();
          bValue = b.scheduledStartDate.getTime();
      }

      if (sort.direction === 'asc') {
        return aValue > bValue ? 1 : aValue < bValue ? -1 : 0;
      } else {
        return aValue < bValue ? 1 : aValue > bValue ? -1 : 0;
      }
    });

    const total = filtered.length;
    const start = (pagination.page - 1) * pagination.pageSize;
    const end = start + pagination.pageSize;
    const data = filtered.slice(start, end);

    return { data, total };
  }

  async findByAssignedTo(userId: string, filters?: FieldServiceTaskFilters): Promise<FieldServiceTask[]> {
    const allTasks = await this.findMany(
      { ...filters, assignedToId: userId },
      { page: 1, pageSize: 10000 },
      { field: 'scheduledStartDate', direction: 'asc' }
    );
    return allTasks.data;
  }

  async findByFarmer(farmerId: string, filters?: FieldServiceTaskFilters): Promise<FieldServiceTask[]> {
    const allTasks = await this.findMany(
      { ...filters, farmerId },
      { page: 1, pageSize: 10000 },
      { field: 'scheduledStartDate', direction: 'asc' }
    );
    return allTasks.data;
  }

  async create(task: FieldServiceTask): Promise<FieldServiceTask> {
    this.tasks.set(task.id, task);
    return task;
  }

  async update(task: FieldServiceTask): Promise<FieldServiceTask> {
    if (!this.tasks.has(task.id)) {
      throw new Error(`Task with id ${task.id} not found`);
    }
    this.tasks.set(task.id, task);
    return task;
  }

  async delete(id: string): Promise<void> {
    if (!this.tasks.has(id)) {
      throw new Error(`Task with id ${id} not found`);
    }
    this.tasks.delete(id);
  }
}

