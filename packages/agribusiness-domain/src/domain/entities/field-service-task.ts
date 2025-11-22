/**
 * Field Service Task Entity
 * Mobile Field Service - Task Management for Field Operations
 * Based on Odoo project.task pattern with field service extensions
 */

import { randomUUID } from 'crypto';

export type FieldServiceTaskStatus =
  | 'DRAFT'            // Entwurf
  | 'SCHEDULED'        // Geplant
  | 'IN_PROGRESS'      // In Bearbeitung
  | 'ON_HOLD'          // Pausiert
  | 'COMPLETED'        // Abgeschlossen
  | 'CANCELLED'        // Abgebrochen
  | 'REQUIRES_REVIEW'; // Benötigt Überprüfung

export type FieldServiceTaskType =
  | 'INSPECTION'       // Inspektion
  | 'HARVEST'          // Ernte
  | 'PLANTING'         // Pflanzung
  | 'TREATMENT'        // Behandlung (Düngung, Pflanzenschutz)
  | 'SAMPLE_COLLECTION' // Probenahme
  | 'EQUIPMENT_MAINTENANCE' // Wartung
  | 'TRAINING'         // Schulung
  | 'AUDIT'            // Audit
  | 'OTHER';           // Sonstiges

export type TaskPriority =
  | 'LOW'              // Niedrig
  | 'MEDIUM'           // Mittel
  | 'HIGH'             // Hoch
  | 'URGENT';          // Dringend

export type WeatherCondition =
  | 'SUNNY'            // Sonnig
  | 'CLOUDY'           // Bewölkt
  | 'RAINY'            // Regnerisch
  | 'WINDY'            // Windig
  | 'FOGGY'            // Neblig
  | 'STORMY';          // Stürmisch

export interface FieldServiceLocation {
  id: string;
  name: string;
  address: string;
  city: string;
  postalCode: string;
  country: string;
  latitude: number;
  longitude: number;
  accuracy?: number; // GPS accuracy in meters
}

export interface FieldServiceAttachment {
  id: string;
  fileName: string;
  fileType: string;
  fileSize: number;
  url: string;
  uploadedAt: Date;
  uploadedBy: string;
  description?: string;
}

export interface FieldServiceNote {
  id: string;
  content: string;
  authorId: string;
  authorName: string;
  createdAt: Date;
  isInternal: boolean; // Internal note vs. customer-visible note
  attachments?: string[]; // Attachment IDs
}

export interface FieldServiceChecklistItem {
  id: string;
  description: string;
  isCompleted: boolean;
  completedAt?: Date;
  completedBy?: string;
  notes?: string;
}

export interface FieldServiceMeasurement {
  id: string;
  type: string; // e.g., 'TEMPERATURE', 'HUMIDITY', 'PH', 'YIELD', etc.
  value: number;
  unit: string;
  recordedAt: Date;
  recordedBy: string;
  location?: { latitude: number; longitude: number };
  notes?: string;
}

export interface CreateFieldServiceTaskInput {
  title: string;
  description?: string;
  taskType: FieldServiceTaskType;
  priority?: TaskPriority;
  assignedToId: string;
  assignedToName: string;
  farmerId?: string;
  farmerName?: string;
  location: Omit<FieldServiceLocation, 'id'>;
  scheduledStartDate: Date;
  scheduledEndDate?: Date;
  estimatedDuration?: number; // in minutes
  checklist?: Omit<FieldServiceChecklistItem, 'id' | 'isCompleted'>[];
  relatedBatchId?: string;
  relatedContractId?: string;
  tags?: string[];
}

export interface UpdateFieldServiceTaskInput {
  title?: string;
  description?: string;
  taskType?: FieldServiceTaskType;
  priority?: TaskPriority;
  status?: FieldServiceTaskStatus;
  assignedToId?: string;
  assignedToName?: string;
  scheduledStartDate?: Date;
  scheduledEndDate?: Date;
  actualStartDate?: Date;
  actualEndDate?: Date;
  estimatedDuration?: number;
  actualDuration?: number;
  location?: Partial<FieldServiceLocation>;
  weatherCondition?: WeatherCondition;
  temperature?: number;
  notes?: string;
  checklist?: FieldServiceChecklistItem[];
  tags?: string[];
}

export interface FieldServiceTask {
  id: string;
  taskNumber: string; // Unique task identifier
  title: string;
  description?: string;
  taskType: FieldServiceTaskType;
  priority: TaskPriority;
  status: FieldServiceTaskStatus;
  
  // Assignment
  assignedToId: string;
  assignedToName: string;
  createdById: string;
  createdByName: string;
  
  // Customer/Farmer
  farmerId?: string;
  farmerName?: string;
  
  // Scheduling
  scheduledStartDate: Date;
  scheduledEndDate?: Date;
  actualStartDate?: Date;
  actualEndDate?: Date;
  estimatedDuration?: number; // in minutes
  actualDuration?: number; // in minutes
  
  // Location
  location: FieldServiceLocation;
  
  // Field conditions
  weatherCondition?: WeatherCondition;
  temperature?: number;
  
  // Task details
  checklist: FieldServiceChecklistItem[];
  notes: FieldServiceNote[];
  attachments: FieldServiceAttachment[];
  measurements: FieldServiceMeasurement[];
  
  // Relations
  relatedBatchId?: string;
  relatedContractId?: string;
  relatedTaskIds?: string[]; // Related tasks
  
  // Metadata
  tags: string[];
  completionPercentage: number; // 0-100
  isBillable: boolean;
  billableHours?: number;
  billableRate?: number;
  
  // Mobile app specific
  mobileAppVersion?: string;
  lastSyncAt?: Date;
  isOfflineCreated: boolean;
  
  // Metadata
  createdAt: Date;
  updatedAt: Date;
  completedAt?: Date;
}

export class FieldServiceTaskEntity {
  static create(input: CreateFieldServiceTaskInput, userId: string, userName: string): FieldServiceTask {
    const now = new Date();
    const taskNumber = `TASK-${Date.now().toString().slice(-8)}-${Math.random().toString(36).substring(2, 6).toUpperCase()}`;
    
    const task: FieldServiceTask = {
      id: randomUUID(),
      taskNumber,
      title: input.title,
      description: input.description,
      taskType: input.taskType,
      priority: input.priority || 'MEDIUM',
      status: 'DRAFT',
      assignedToId: input.assignedToId,
      assignedToName: input.assignedToName,
      createdById: userId,
      createdByName: userName,
      farmerId: input.farmerId,
      farmerName: input.farmerName,
      scheduledStartDate: input.scheduledStartDate,
      scheduledEndDate: input.scheduledEndDate,
      estimatedDuration: input.estimatedDuration,
      location: {
        id: randomUUID(),
        ...input.location,
      },
      checklist: (input.checklist || []).map(item => ({
        id: randomUUID(),
        ...item,
        isCompleted: false,
      })),
      notes: [],
      attachments: [],
      measurements: [],
      relatedBatchId: input.relatedBatchId,
      relatedContractId: input.relatedContractId,
      tags: input.tags || [],
      completionPercentage: 0,
      isBillable: false,
      isOfflineCreated: false,
      createdAt: now,
      updatedAt: now,
    };

    return task;
  }

  static update(task: FieldServiceTask, input: UpdateFieldServiceTaskInput, userId: string): FieldServiceTask {
    const updated: FieldServiceTask = {
      ...task,
      ...(input.title && { title: input.title }),
      ...(input.description !== undefined && { description: input.description }),
      ...(input.taskType && { taskType: input.taskType }),
      ...(input.priority && { priority: input.priority }),
      ...(input.status && { status: input.status }),
      ...(input.assignedToId && { assignedToId: input.assignedToId }),
      ...(input.assignedToName && { assignedToName: input.assignedToName }),
      ...(input.scheduledStartDate && { scheduledStartDate: input.scheduledStartDate }),
      ...(input.scheduledEndDate !== undefined && { scheduledEndDate: input.scheduledEndDate }),
      ...(input.actualStartDate && { actualStartDate: input.actualStartDate }),
      ...(input.actualEndDate && { actualEndDate: input.actualEndDate }),
      ...(input.estimatedDuration !== undefined && { estimatedDuration: input.estimatedDuration }),
      ...(input.actualDuration !== undefined && { actualDuration: input.actualDuration }),
      ...(input.weatherCondition && { weatherCondition: input.weatherCondition }),
      ...(input.temperature !== undefined && { temperature: input.temperature }),
      ...(input.checklist && { checklist: input.checklist }),
      ...(input.tags && { tags: input.tags }),
      updatedAt: new Date(),
    };

    // Update location if provided
    if (input.location) {
      updated.location = {
        ...task.location,
        ...input.location,
      };
    }

    // Update completion percentage based on checklist
    if (updated.checklist.length > 0) {
      const completedItems = updated.checklist.filter(item => item.isCompleted).length;
      updated.completionPercentage = Math.round((completedItems / updated.checklist.length) * 100);
    }

    // Set completedAt if status is COMPLETED
    if (updated.status === 'COMPLETED' && !updated.completedAt) {
      updated.completedAt = new Date();
    }

    return updated;
  }

  static startTask(task: FieldServiceTask): FieldServiceTask {
    if (task.status === 'COMPLETED' || task.status === 'CANCELLED') {
      throw new Error(`Cannot start task in status ${task.status}`);
    }

    return {
      ...task,
      status: 'IN_PROGRESS',
      actualStartDate: new Date(),
      updatedAt: new Date(),
    };
  }

  static completeTask(task: FieldServiceTask, userId: string): FieldServiceTask {
    if (task.status === 'CANCELLED') {
      throw new Error('Cannot complete a cancelled task');
    }

    // Ensure all checklist items are completed
    const allCompleted = task.checklist.every(item => item.isCompleted);
    if (!allCompleted && task.checklist.length > 0) {
      throw new Error('Cannot complete task: not all checklist items are completed');
    }

    return {
      ...task,
      status: 'COMPLETED',
      actualEndDate: new Date(),
      completedAt: new Date(),
      completionPercentage: 100,
      updatedAt: new Date(),
    };
  }

  static addNote(task: FieldServiceTask, content: string, authorId: string, authorName: string, isInternal: boolean = false): FieldServiceTask {
    const note: FieldServiceNote = {
      id: randomUUID(),
      content,
      authorId,
      authorName,
      createdAt: new Date(),
      isInternal,
    };

    return {
      ...task,
      notes: [...task.notes, note],
      updatedAt: new Date(),
    };
  }

  static addAttachment(task: FieldServiceTask, attachment: Omit<FieldServiceAttachment, 'id' | 'uploadedAt'>): FieldServiceTask {
    const newAttachment: FieldServiceAttachment = {
      id: randomUUID(),
      ...attachment,
      uploadedAt: new Date(),
    };

    return {
      ...task,
      attachments: [...task.attachments, newAttachment],
      updatedAt: new Date(),
    };
  }

  static addMeasurement(task: FieldServiceTask, measurement: Omit<FieldServiceMeasurement, 'id' | 'recordedAt'>): FieldServiceTask {
    const newMeasurement: FieldServiceMeasurement = {
      id: randomUUID(),
      ...measurement,
      recordedAt: new Date(),
    };

    return {
      ...task,
      measurements: [...task.measurements, newMeasurement],
      updatedAt: new Date(),
    };
  }

  static completeChecklistItem(task: FieldServiceTask, itemId: string, userId: string, notes?: string): FieldServiceTask {
    const updatedChecklist = task.checklist.map(item => {
      if (item.id === itemId && !item.isCompleted) {
        return {
          ...item,
          isCompleted: true,
          completedAt: new Date(),
          completedBy: userId,
          notes,
        };
      }
      return item;
    });

    const completedItems = updatedChecklist.filter(item => item.isCompleted).length;
    const completionPercentage = updatedChecklist.length > 0
      ? Math.round((completedItems / updatedChecklist.length) * 100)
      : task.completionPercentage;

    return {
      ...task,
      checklist: updatedChecklist,
      completionPercentage,
      updatedAt: new Date(),
    };
  }

  static cancelTask(task: FieldServiceTask, reason?: string): FieldServiceTask {
    if (task.status === 'COMPLETED') {
      throw new Error('Cannot cancel a completed task');
    }

    const cancelledTask: FieldServiceTask = {
      ...task,
      status: 'CANCELLED',
      updatedAt: new Date(),
    };

    // Add cancellation note if reason provided
    if (reason) {
      return this.addNote(cancelledTask, `Task cancelled: ${reason}`, task.createdById, task.createdByName, true);
    }

    return cancelledTask;
  }
}

