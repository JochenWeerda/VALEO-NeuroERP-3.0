import { pgTable, text, integer, timestamp, uuid, boolean, decimal, jsonb, index } from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';

// Enums
export const weighingTypeEnum = sql`enum('Vehicle', 'Container', 'Silo', 'Manual')`;
export const weighingStatusEnum = sql`enum('Draft', 'InProgress', 'Completed', 'Cancelled', 'Error')`;
export const commodityTypeEnum = sql`enum('WHEAT', 'BARLEY', 'RAPESEED', 'SOYMEAL', 'COMPOUND_FEED', 'FERTILIZER', 'OTHER')`;
export const weighingModeEnum = sql`enum('Gross', 'Tare', 'Net')`;

export const slotStatusEnum = sql`enum('Scheduled', 'Entered', 'Exited', 'Cancelled', 'NoShow')`;
export const gateTypeEnum = sql`enum('Inbound', 'Outbound', 'Weighing', 'Inspection')`;

export const anprConfidenceEnum = sql`enum('Low', 'Medium', 'High')`;
export const anprStatusEnum = sql`enum('Detected', 'Processed', 'Assigned', 'Rejected', 'Error')`;

export const waitLogStatusEnum = sql`enum('Waiting', 'InService', 'Completed', 'Cancelled')`;

// Weighing Tickets Table
export const weighingTickets = pgTable('weighing_tickets', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  ticketNumber: text('ticket_number').notNull(),
  type: text('type', { enum: ['Vehicle', 'Container', 'Silo', 'Manual'] }).notNull(),
  status: text('status', { enum: ['Draft', 'InProgress', 'Completed', 'Cancelled', 'Error'] }).notNull().default('Draft'),

  // Vehicle/Container Information
  licensePlate: text('license_plate'),
  containerNumber: text('container_number'),
  siloId: text('silo_id'),

  // Commodity Information
  commodity: text('commodity', { enum: ['WHEAT', 'BARLEY', 'RAPESEED', 'SOYMEAL', 'COMPOUND_FEED', 'FERTILIZER', 'OTHER'] }).notNull(),
  commodityDescription: text('commodity_description'),

  // Weights (stored as JSON for complex structure)
  grossWeight: jsonb('gross_weight'),
  tareWeight: jsonb('tare_weight'),
  netWeight: decimal('net_weight', { precision: 10, scale: 2 }),
  netWeightUnit: text('net_weight_unit', { enum: ['kg', 't'] }),

  // Quality & Tolerances
  expectedWeight: decimal('expected_weight', { precision: 10, scale: 2 }),
  tolerancePercent: decimal('tolerance_percent', { precision: 5, scale: 2 }).notNull().default('2.00'),
  isWithinTolerance: boolean('is_within_tolerance'),

  // References
  contractId: uuid('contract_id'),
  orderId: uuid('order_id'),
  deliveryNoteId: uuid('delivery_note_id'),

  // ANPR & Automation
  anprRecordId: uuid('anpr_record_id'),
  autoAssigned: boolean('auto_assigned').notNull().default(false),

  // Gate & Logistics
  gateId: text('gate_id'),
  slotId: uuid('slot_id'),

  // Metadata
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  completedAt: timestamp('completed_at'),
  version: integer('version').notNull().default(1),
}, (table) => ({
  tenantIdx: index('weighing_tickets_tenant_idx').on(table.tenantId),
  statusIdx: index('weighing_tickets_status_idx').on(table.status),
  ticketNumberIdx: index('weighing_tickets_number_idx').on(table.ticketNumber),
  licensePlateIdx: index('weighing_tickets_license_plate_idx').on(table.licensePlate),
  contractIdx: index('weighing_tickets_contract_idx').on(table.contractId),
  orderIdx: index('weighing_tickets_order_idx').on(table.orderId),
  gateIdx: index('weighing_tickets_gate_idx').on(table.gateId),
  createdAtIdx: index('weighing_tickets_created_at_idx').on(table.createdAt),
}));

// Slots Table
export const slots = pgTable('slots', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  gateId: text('gate_id').notNull(),
  gateType: text('gate_type', { enum: ['Inbound', 'Outbound', 'Weighing', 'Inspection'] }).notNull(),
  windowFrom: timestamp('window_from').notNull(),
  windowTo: timestamp('window_to').notNull(),
  assignedVehicleId: uuid('assigned_vehicle_id'),
  licensePlate: text('license_plate'),
  priority: integer('priority').notNull().default(5),

  status: text('status', { enum: ['Scheduled', 'Entered', 'Exited', 'Cancelled', 'NoShow'] }).notNull().default('Scheduled'),

  // Logistics
  contractId: uuid('contract_id'),
  orderId: uuid('order_id'),
  commodity: text('commodity'),
  expectedWeight: decimal('expected_weight', { precision: 10, scale: 2 }),

  // Actual times
  enteredAt: timestamp('entered_at'),
  exitedAt: timestamp('exited_at'),
  actualServiceStart: timestamp('actual_service_start'),

  // Metadata
  notes: text('notes'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  version: integer('version').notNull().default(1),
}, (table) => ({
  tenantIdx: index('slots_tenant_idx').on(table.tenantId),
  gateIdx: index('slots_gate_idx').on(table.gateId),
  statusIdx: index('slots_status_idx').on(table.status),
  windowFromIdx: index('slots_window_from_idx').on(table.windowFrom),
  assignedVehicleIdx: index('slots_assigned_vehicle_idx').on(table.assignedVehicleId),
  licensePlateIdx: index('slots_license_plate_idx').on(table.licensePlate),
}));

// ANPR Records Table
export const anprRecords = pgTable('anpr_records', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  licensePlate: text('license_plate').notNull(),
  confidence: decimal('confidence', { precision: 5, scale: 2 }).notNull(),
  confidenceLevel: text('confidence_level', { enum: ['Low', 'Medium', 'High'] }).notNull(),
  capturedAt: timestamp('captured_at').notNull(),
  imageUri: text('image_uri'),
  cameraId: text('camera_id').notNull(),
  gateId: text('gate_id'),

  // Processing
  status: text('status', { enum: ['Detected', 'Processed', 'Assigned', 'Rejected', 'Error'] }).notNull().default('Detected'),
  processedAt: timestamp('processed_at'),
  ticketSuggestionId: uuid('ticket_suggestion_id'),
  assignedTicketId: uuid('assigned_ticket_id'),

  // Vehicle data
  vehicleId: uuid('vehicle_id'),
  contractId: uuid('contract_id'),
  orderId: uuid('order_id'),
  commodity: text('commodity'),

  // Error handling
  errorMessage: text('error_message'),
  retryCount: integer('retry_count').notNull().default(0),

  // Metadata
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  version: integer('version').notNull().default(1),
}, (table) => ({
  tenantIdx: index('anpr_records_tenant_idx').on(table.tenantId),
  licensePlateIdx: index('anpr_records_license_plate_idx').on(table.licensePlate),
  statusIdx: index('anpr_records_status_idx').on(table.status),
  capturedAtIdx: index('anpr_records_captured_at_idx').on(table.capturedAt),
  cameraIdx: index('anpr_records_camera_idx').on(table.cameraId),
  gateIdx: index('anpr_records_gate_idx').on(table.gateId),
  assignedTicketIdx: index('anpr_records_assigned_ticket_idx').on(table.assignedTicketId),
}));

// Wait Logs Table
export const waitLogs = pgTable('wait_logs', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  ticketId: uuid('ticket_id').notNull(),
  licensePlate: text('license_plate'),

  // Timing
  arrivalAt: timestamp('arrival_at').notNull(),
  serviceStartAt: timestamp('service_start_at'),
  serviceEndAt: timestamp('service_end_at'),

  // Calculated fields
  waitTimeMinutes: integer('wait_time_minutes'),
  serviceTimeMinutes: integer('service_time_minutes'),
  totalTimeMinutes: integer('total_time_minutes'),

  // Gate & logistics
  gateId: text('gate_id').notNull(),
  gateType: text('gate_type', { enum: ['Inbound', 'Outbound', 'Weighing', 'Inspection'] }).notNull(),
  slotId: uuid('slot_id'),

  // Priority & categorization
  priority: integer('priority').notNull().default(5),
  isHighPriority: boolean('is_high_priority'),
  isOvertime: boolean('is_overtime'),

  // Context
  contractId: uuid('contract_id'),
  orderId: uuid('order_id'),
  commodity: text('commodity'),
  expectedWeight: decimal('expected_weight', { precision: 10, scale: 2 }),

  // Status
  status: text('status', { enum: ['Waiting', 'InService', 'Completed', 'Cancelled'] }).notNull().default('Waiting'),

  // Notes & metadata
  notes: text('notes'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  version: integer('version').notNull().default(1),
}, (table) => ({
  tenantIdx: index('wait_logs_tenant_idx').on(table.tenantId),
  ticketIdx: index('wait_logs_ticket_idx').on(table.ticketId),
  gateIdx: index('wait_logs_gate_idx').on(table.gateId),
  statusIdx: index('wait_logs_status_idx').on(table.status),
  arrivalAtIdx: index('wait_logs_arrival_at_idx').on(table.arrivalAt),
  licensePlateIdx: index('wait_logs_license_plate_idx').on(table.licensePlate),
  slotIdx: index('wait_logs_slot_idx').on(table.slotId),
}));

// Audit Logs Table
export const auditLogs = pgTable('audit_logs', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  entityType: text('entity_type').notNull(), // 'WeighingTicket', 'Slot', 'ANPRRecord', etc.
  entityId: uuid('entity_id').notNull(),
  action: text('action').notNull(), // 'CREATE', 'UPDATE', 'DELETE', 'WEIGH', etc.
  userId: uuid('user_id'),
  userRole: text('user_role'),
  ipAddress: text('ip_address'),
  userAgent: text('user_agent'),

  // Changes
  oldValues: jsonb('old_values'),
  newValues: jsonb('new_values'),
  changes: jsonb('changes'), // Summary of what changed

  // Context
  sessionId: uuid('session_id'),
  requestId: text('request_id'),
  gateId: text('gate_id'),
  scaleId: text('scale_id'),

  // Metadata
  timestamp: timestamp('timestamp').notNull().defaultNow(),
  notes: text('notes'),
}, (table) => ({
  tenantIdx: index('audit_logs_tenant_idx').on(table.tenantId),
  entityIdx: index('audit_logs_entity_idx').on(table.entityType, table.entityId),
  actionIdx: index('audit_logs_action_idx').on(table.action),
  timestampIdx: index('audit_logs_timestamp_idx').on(table.timestamp),
  userIdx: index('audit_logs_user_idx').on(table.userId),
}));

// Report Templates Table
export const reportTemplates = pgTable('report_templates', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  name: text('name').notNull(),
  description: text('description'),
  type: text('type').notNull(), // 'Volume', 'Performance', 'Compliance', etc.
  category: text('category').notNull(), // 'Daily', 'Weekly', 'Monthly', 'Custom'

  // Configuration
  config: jsonb('config').notNull(), // Filter criteria, date ranges, etc.
  parameters: jsonb('parameters'), // Dynamic parameters
  schedule: jsonb('schedule'), // Cron schedule for automated reports

  // Output
  format: text('format', { enum: ['CSV', 'Excel', 'JSON', 'PDF'] }).notNull().default('CSV'),
  recipients: jsonb('recipients'), // Email recipients for scheduled reports

  // Metadata
  isActive: boolean('is_active').notNull().default(true),
  createdBy: uuid('created_by').notNull(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  lastRunAt: timestamp('last_run_at'),
  version: integer('version').notNull().default(1),
}, (table) => ({
  tenantIdx: index('report_templates_tenant_idx').on(table.tenantId),
  typeIdx: index('report_templates_type_idx').on(table.type),
  categoryIdx: index('report_templates_category_idx').on(table.category),
  activeIdx: index('report_templates_active_idx').on(table.isActive),
}));

// Weighing Sessions Table (for grouping related operations)
export const weighingSessions = pgTable('weighing_sessions', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  sessionNumber: text('session_number').notNull(),
  gateId: text('gate_id').notNull(),
  scaleId: text('scale_id').notNull(),

  // Session info
  operatorId: uuid('operator_id'),
  startedAt: timestamp('started_at').notNull(),
  endedAt: timestamp('ended_at'),

  // Statistics
  totalTickets: integer('total_tickets').notNull().default(0),
  totalWeight: decimal('total_weight', { precision: 12, scale: 2 }),
  totalWeightUnit: text('total_weight_unit', { enum: ['kg', 't'] }),

  // Status
  status: text('status', { enum: ['Active', 'Completed', 'Error'] }).notNull().default('Active'),

  // Metadata
  notes: text('notes'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  version: integer('version').notNull().default(1),
}, (table) => ({
  tenantIdx: index('weighing_sessions_tenant_idx').on(table.tenantId),
  gateIdx: index('weighing_sessions_gate_idx').on(table.gateId),
  scaleIdx: index('weighing_sessions_scale_idx').on(table.scaleId),
  statusIdx: index('weighing_sessions_status_idx').on(table.status),
  startedAtIdx: index('weighing_sessions_started_at_idx').on(table.startedAt),
}));