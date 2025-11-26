/**
 * Mobile Field Service Service
 * Task Management for Field Operations
 * Based on Odoo project.task pattern
 */

import {
  FieldServiceTask,
  FieldServiceTaskEntity,
  CreateFieldServiceTaskInput,
  UpdateFieldServiceTaskInput,
  FieldServiceTaskStatus,
  FieldServiceTaskType,
  FieldServiceNote,
  FieldServiceAttachment,
  FieldServiceMeasurement,
  FieldServiceChecklistItem,
} from '../entities/field-service-task';

export interface FieldServiceTaskRepository {
  findById(id: string): Promise<FieldServiceTask | null>;
  findByTaskNumber(taskNumber: string): Promise<FieldServiceTask | null>;
  findMany(filters: FieldServiceTaskFilters, pagination: PaginationOptions, sort: SortOptions): Promise<{ data: FieldServiceTask[]; total: number }>;
  findByAssignedTo(userId: string, filters?: FieldServiceTaskFilters): Promise<FieldServiceTask[]>;
  findByFarmer(farmerId: string, filters?: FieldServiceTaskFilters): Promise<FieldServiceTask[]>;
  create(task: FieldServiceTask): Promise<FieldServiceTask>;
  update(task: FieldServiceTask): Promise<FieldServiceTask>;
  delete(id: string): Promise<void>;
}

export interface FieldServiceTaskFilters {
  taskNumber?: string;
  taskType?: FieldServiceTaskType;
  status?: FieldServiceTaskStatus;
  priority?: string;
  assignedToId?: string;
  farmerId?: string;
  scheduledStartDateFrom?: Date;
  scheduledStartDateTo?: Date;
  search?: string;
  tags?: string[];
  relatedBatchId?: string;
  relatedContractId?: string;
  isBillable?: boolean;
  requiresReview?: boolean;
}

export interface PaginationOptions {
  page: number;
  pageSize: number;
}

export interface SortOptions {
  field: 'createdAt' | 'updatedAt' | 'scheduledStartDate' | 'priority' | 'status';
  direction: 'asc' | 'desc';
}

export interface FieldServiceTaskStats {
  total: number;
  byStatus: Record<FieldServiceTaskStatus, number>;
  byType: Record<FieldServiceTaskType, number>;
  byPriority: Record<string, number>;
  overdue: number;
  dueToday: number;
  dueThisWeek: number;
  averageCompletionTime?: number; // in minutes
}

export interface FieldServiceTaskServiceDependencies {
  taskRepository: FieldServiceTaskRepository;
}

export class MobileFieldServiceService {
  constructor(private deps: FieldServiceTaskServiceDependencies) {}

  /**
   * Create a new field service task
   */
  async createTask(input: CreateFieldServiceTaskInput, userId: string, userName: string): Promise<FieldServiceTask> {
    const task = FieldServiceTaskEntity.create(input, userId, userName);
    return await this.deps.taskRepository.create(task);
  }

  /**
   * Get task by ID
   */
  async getTaskById(taskId: string): Promise<FieldServiceTask> {
    const task = await this.deps.taskRepository.findById(taskId);
    if (!task) {
      throw new Error(`Task with id ${taskId} not found`);
    }
    return task;
  }

  /**
   * Get task by task number
   */
  async getTaskByTaskNumber(taskNumber: string): Promise<FieldServiceTask> {
    const task = await this.deps.taskRepository.findByTaskNumber(taskNumber);
    if (!task) {
      throw new Error(`Task with number ${taskNumber} not found`);
    }
    return task;
  }

  /**
   * Update task
   */
  async updateTask(taskId: string, input: UpdateFieldServiceTaskInput, userId: string): Promise<FieldServiceTask> {
    const task = await this.getTaskById(taskId);
    const updated = FieldServiceTaskEntity.update(task, input, userId);
    return await this.deps.taskRepository.update(updated);
  }

  /**
   * List tasks with filtering and pagination
   */
  async listTasks(
    filters: FieldServiceTaskFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 },
    sort: SortOptions = { field: 'scheduledStartDate', direction: 'asc' }
  ): Promise<{ data: FieldServiceTask[]; total: number; page: number; pageSize: number }> {
    const result = await this.deps.taskRepository.findMany(filters, pagination, sort);
    return {
      ...result,
      page: pagination.page,
      pageSize: pagination.pageSize,
    };
  }

  /**
   * Get tasks assigned to a user
   */
  async getTasksForUser(
    userId: string,
    filters: FieldServiceTaskFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<{ data: FieldServiceTask[]; total: number }> {
    const allTasks = await this.deps.taskRepository.findByAssignedTo(userId, filters);
    const start = (pagination.page - 1) * pagination.pageSize;
    const end = start + pagination.pageSize;
    return {
      data: allTasks.slice(start, end),
      total: allTasks.length,
    };
  }

  /**
   * Get tasks for a farmer
   */
  async getTasksForFarmer(
    farmerId: string,
    filters: FieldServiceTaskFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<{ data: FieldServiceTask[]; total: number }> {
    const allTasks = await this.deps.taskRepository.findByFarmer(farmerId, filters);
    const start = (pagination.page - 1) * pagination.pageSize;
    const end = start + pagination.pageSize;
    return {
      data: allTasks.slice(start, end),
      total: allTasks.length,
    };
  }

  /**
   * Start a task
   */
  async startTask(taskId: string): Promise<FieldServiceTask> {
    const task = await this.getTaskById(taskId);
    const started = FieldServiceTaskEntity.startTask(task);
    return await this.deps.taskRepository.update(started);
  }

  /**
   * Complete a task
   */
  async completeTask(taskId: string, userId: string): Promise<FieldServiceTask> {
    const task = await this.getTaskById(taskId);
    const completed = FieldServiceTaskEntity.completeTask(task, userId);
    return await this.deps.taskRepository.update(completed);
  }

  /**
   * Cancel a task
   */
  async cancelTask(taskId: string, reason?: string): Promise<FieldServiceTask> {
    const task = await this.getTaskById(taskId);
    const cancelled = FieldServiceTaskEntity.cancelTask(task, reason);
    return await this.deps.taskRepository.update(cancelled);
  }

  /**
   * Add note to task
   */
  async addNote(
    taskId: string,
    content: string,
    authorId: string,
    authorName: string,
    isInternal: boolean = false
  ): Promise<FieldServiceTask> {
    const task = await this.getTaskById(taskId);
    const updated = FieldServiceTaskEntity.addNote(task, content, authorId, authorName, isInternal);
    return await this.deps.taskRepository.update(updated);
  }

  /**
   * Add attachment to task
   */
  async addAttachment(
    taskId: string,
    attachment: Omit<FieldServiceAttachment, 'id' | 'uploadedAt'>
  ): Promise<FieldServiceTask> {
    const task = await this.getTaskById(taskId);
    const updated = FieldServiceTaskEntity.addAttachment(task, attachment);
    return await this.deps.taskRepository.update(updated);
  }

  /**
   * Add measurement to task
   */
  async addMeasurement(
    taskId: string,
    measurement: Omit<FieldServiceMeasurement, 'id' | 'recordedAt'>
  ): Promise<FieldServiceTask> {
    const task = await this.getTaskById(taskId);
    const updated = FieldServiceTaskEntity.addMeasurement(task, measurement);
    return await this.deps.taskRepository.update(updated);
  }

  /**
   * Complete checklist item
   */
  async completeChecklistItem(
    taskId: string,
    itemId: string,
    userId: string,
    notes?: string
  ): Promise<FieldServiceTask> {
    const task = await this.getTaskById(taskId);
    const updated = FieldServiceTaskEntity.completeChecklistItem(task, itemId, userId, notes);
    return await this.deps.taskRepository.update(updated);
  }

  /**
   * Get task statistics
   */
  async getTaskStats(filters?: FieldServiceTaskFilters): Promise<FieldServiceTaskStats> {
    const allTasks = await this.deps.taskRepository.findMany(
      filters || {},
      { page: 1, pageSize: 10000 },
      { field: 'createdAt', direction: 'desc' }
    );

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekFromNow = new Date(today);
    weekFromNow.setDate(weekFromNow.getDate() + 7);

    const stats: FieldServiceTaskStats = {
      total: allTasks.total,
      byStatus: {
        DRAFT: 0,
        SCHEDULED: 0,
        IN_PROGRESS: 0,
        ON_HOLD: 0,
        COMPLETED: 0,
        CANCELLED: 0,
        REQUIRES_REVIEW: 0,
      },
      byType: {
        INSPECTION: 0,
        HARVEST: 0,
        PLANTING: 0,
        TREATMENT: 0,
        SAMPLE_COLLECTION: 0,
        EQUIPMENT_MAINTENANCE: 0,
        TRAINING: 0,
        AUDIT: 0,
        OTHER: 0,
      },
      byPriority: {
        LOW: 0,
        MEDIUM: 0,
        HIGH: 0,
        URGENT: 0,
      },
      overdue: 0,
      dueToday: 0,
      dueThisWeek: 0,
    };

    let totalCompletionTime = 0;
    let completedTasksCount = 0;

    for (const task of allTasks.data) {
      // Count by status
      stats.byStatus[task.status]++;

      // Count by type
      stats.byType[task.taskType]++;

      // Count by priority
      stats.byPriority[task.priority]++;

      // Check overdue
      if (task.scheduledStartDate < now && task.status !== 'COMPLETED' && task.status !== 'CANCELLED') {
        stats.overdue++;
      }

      // Check due today
      if (
        task.scheduledStartDate >= today &&
        task.scheduledStartDate < new Date(today.getTime() + 24 * 60 * 60 * 1000) &&
        task.status !== 'COMPLETED' &&
        task.status !== 'CANCELLED'
      ) {
        stats.dueToday++;
      }

      // Check due this week
      if (
        task.scheduledStartDate >= today &&
        task.scheduledStartDate < weekFromNow &&
        task.status !== 'COMPLETED' &&
        task.status !== 'CANCELLED'
      ) {
        stats.dueThisWeek++;
      }

      // Calculate average completion time
      if (task.status === 'COMPLETED' && task.actualStartDate && task.actualEndDate) {
        const duration = task.actualEndDate.getTime() - task.actualStartDate.getTime();
        totalCompletionTime += duration;
        completedTasksCount++;
      }
    }

    if (completedTasksCount > 0) {
      stats.averageCompletionTime = Math.round(totalCompletionTime / completedTasksCount / (60 * 1000)); // in minutes
    }

    return stats;
  }

  /**
   * Search tasks
   */
  async searchTasks(query: string, limit: number = 20): Promise<FieldServiceTask[]> {
    const result = await this.deps.taskRepository.findMany(
      { search: query },
      { page: 1, pageSize: limit },
      { field: 'scheduledStartDate', direction: 'asc' }
    );
    return result.data;
  }

  /**
   * Mark task as requiring review
   */
  async markForReview(taskId: string, reason?: string): Promise<FieldServiceTask> {
    const task = await this.getTaskById(taskId);
    if (task.status !== 'COMPLETED') {
      throw new Error('Only completed tasks can be marked for review');
    }
    const updated = FieldServiceTaskEntity.update(task, { status: 'REQUIRES_REVIEW' }, task.createdById);
    if (reason) {
      return await this.addNote(taskId, `Marked for review: ${reason}`, task.createdById, task.createdByName, true);
    }
    return await this.deps.taskRepository.update(updated);
  }

  /**
   * Sync task from mobile app
   */
  async syncFromMobile(
    taskId: string,
    updates: Partial<UpdateFieldServiceTaskInput>,
    mobileAppVersion: string
  ): Promise<FieldServiceTask> {
    const task = await this.getTaskById(taskId);
    const updated = FieldServiceTaskEntity.update(task, updates, task.assignedToId);
    updated.mobileAppVersion = mobileAppVersion;
    updated.lastSyncAt = new Date();
    return await this.deps.taskRepository.update(updated);
  }
}

