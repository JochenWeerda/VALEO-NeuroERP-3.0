import { z } from 'zod';
import { Money, UUID, Address, ContactInfo } from './shared-schemas';

// Procurement-specific schemas

// Supplier
export const Supplier = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // Basic information
  name: z.string().min(1),
  code: z.string().optional(),

  // Contact details
  contactInfo: ContactInfo,

  // Business details
  taxId: z.string().optional(),
  paymentTerms: z.number().int().positive().default(30), // Days

  // Status
  status: z.enum(['ACTIVE', 'INACTIVE', 'SUSPENDED']),
  isPreferred: z.boolean().default(false),

  // Metadata
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

export type Supplier = z.infer<typeof Supplier>;

// Purchase order
export const PurchaseOrder = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // Order identification
  orderNumber: z.string(),
  supplierId: UUID,

  // Order details
  orderDate: z.string().datetime(),
  requestedDeliveryDate: z.string().datetime().optional(),
  actualDeliveryDate: z.string().datetime().optional(),

  // Financial details
  subtotal: Money,
  taxAmount: Money,
  total: Money,
  currency: z.string().default('EUR'),

  // Status
  status: z.enum(['DRAFT', 'SENT', 'CONFIRMED', 'PARTIALLY_RECEIVED', 'RECEIVED', 'CANCELLED']),

  // Line items
  lineItems: z.array(z.object({
    id: UUID,
    itemId: z.string(),
    description: z.string(),
    quantity: z.number().positive(),
    unitPrice: Money,
    totalPrice: Money,
    receivedQuantity: z.number().nonnegative().default(0)
  })),

  // Metadata
  createdBy: z.string(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

export type PurchaseOrder = z.infer<typeof PurchaseOrder>;

// Purchase requisition
export const PurchaseRequisition = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // Request details
  title: z.string(),
  description: z.string(),
  requestedBy: z.string(),

  // Urgency
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
  requiredBy: z.string().datetime(),

  // Financial
  estimatedCost: Money,
  budgetCode: z.string().optional(),

  // Status
  status: z.enum(['DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', 'ORDERED']),

  // Items
  items: z.array(z.object({
    description: z.string(),
    quantity: z.number().positive(),
    estimatedUnitPrice: Money,
    category: z.string().optional()
  })),

  // Approval workflow
  approvals: z.array(z.object({
    approverId: z.string(),
    status: z.enum(['PENDING', 'APPROVED', 'REJECTED']),
    comments: z.string().optional(),
    approvedAt: z.string().datetime().optional()
  })).default([]),

  // Metadata
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

export type PurchaseRequisition = z.infer<typeof PurchaseRequisition>;

// RFQ (Request for Quotation)
export const RFQ = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // RFQ details
  title: z.string(),
  description: z.string(),

  // Items
  items: z.array(z.object({
    id: UUID,
    description: z.string(),
    quantity: z.number().positive(),
    unitOfMeasure: z.string(),
    specifications: z.record(z.any()).optional()
  })),

  // Suppliers
  supplierIds: z.array(UUID),

  // Timeline
  responseDeadline: z.string().datetime(),
  validUntil: z.string().datetime(),

  // Status
  status: z.enum(['DRAFT', 'PUBLISHED', 'CLOSED', 'CANCELLED']),

  // Responses
  responses: z.array(z.object({
    supplierId: UUID,
    submittedAt: z.string().datetime(),
    totalAmount: Money,
    lineItems: z.array(z.object({
      itemId: UUID,
      unitPrice: Money,
      totalPrice: Money,
      leadTimeDays: z.number().int().positive()
    })),
    notes: z.string().optional()
  })).default([]),

  // Metadata
  createdBy: z.string(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

export type RFQ = z.infer<typeof RFQ>;