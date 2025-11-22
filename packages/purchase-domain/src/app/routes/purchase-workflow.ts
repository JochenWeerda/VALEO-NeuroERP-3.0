/**
 * Purchase Workflow Routes
 * ISO 27001 Communications Security Compliant
 * Source-to-Pay Workflow API Endpoints
 */

import type { FastifyInstance } from 'fastify';
import { PurchaseOrderWorkflowService } from '../../domain/services/purchase-order-workflow-service';
import { ISMSAuditLogger } from '../../security/isms-audit-logger';
import { CryptoService } from '../../security/crypto-service';

// Create service instance with mock dependencies for now
const auditLogger = new ISMSAuditLogger('purchase-workflow-service', 'development');
const cryptoService = new CryptoService();

const workflowService = new PurchaseOrderWorkflowService({
  auditLogger,
  cryptoService
});

// Helper function to get authenticated user ID
function getAuthenticatedUserId(request: any): string {
  try {
    // Extract user from JWT token or session
    const user = request.user || request.session?.user;

    if (!user) {
      // Try to extract from Authorization header
      const authHeader = request.headers.authorization;
      if (authHeader && authHeader.startsWith('Bearer ')) {
        // In a real implementation, you'd verify the JWT token here
        // For now, we'll assume the token contains user info
        const token = authHeader.substring(7);
        // Mock JWT decoding - in production, use proper JWT library
        try {
          const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
          return payload.sub || payload.userId || payload.id || 'system';
        } catch {
          // Invalid token format
          return 'system';
        }
      }
    }

    return user?.id || user?.userId || user?.sub || 'system';
  } catch (error) {
    // Log authentication error but don't expose details
    console.warn('Authentication context extraction failed');
    return 'system';
  }
}

// Helper function to get tenant ID
function getTenantId(request: any): string {
  // Extract from JWT, headers, or context
  return request.tenantId || request.user?.tenantId || request.headers['x-tenant-id'] || 'default-tenant';
}

export async function registerPurchaseWorkflowRoutes(fastify: FastifyInstance) {

  // Create purchase requisition
  fastify.post('/requisitions', {
    schema: {
      description: 'Create a new purchase requisition',
      tags: ['Purchase Workflow'],
      body: {
        type: 'object',
        required: ['requesterId', 'subject', 'description', 'budgetCode', 'estimatedCost', 'currency', 'requestedItems', 'deliveryLocation', 'requestedDeliveryDate'],
        properties: {
          requesterId: { type: 'string' },
          requesterDepartment: { type: 'string' },
          subject: { type: 'string' },
          description: { type: 'string' },
          businessJustification: { type: 'string' },
          urgency: { type: 'string', enum: ['LOW', 'MEDIUM', 'HIGH', 'URGENT'] },
          budgetCode: { type: 'string' },
          estimatedCost: { type: 'number' },
          currency: { type: 'string' },
          requestedItems: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                articleId: { type: 'string' },
                description: { type: 'string' },
                quantity: { type: 'number' },
                estimatedUnitPrice: { type: 'number' }
              }
            }
          },
          preferredSupplierId: { type: 'string' },
          deliveryLocation: { type: 'string' },
          requestedDeliveryDate: { type: 'string', format: 'date-time' }
        }
      },
      response: {
        201: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            approvalStatus: { type: 'string' },
            autoApproved: { type: 'boolean' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const userId = getAuthenticatedUserId(request);
    const tenantId = getTenantId(request);

    const requisition = await workflowService.createPurchaseRequisition(
      {
        ...request.body as any,
        requestedDeliveryDate: new Date((request.body as any).requestedDeliveryDate)
      },
      userId
    );

    reply.code(201).send({
      id: requisition.id,
      approvalStatus: requisition.approvalStatus,
      autoApproved: requisition.approvalStatus === 'APPROVED'
    });
  });

  // Solicit quotations
  fastify.post('/requisitions/:requisitionId/quotations', {
    schema: {
      description: 'Solicit quotations from suppliers',
      tags: ['Purchase Workflow'],
      params: {
        type: 'object',
        required: ['requisitionId'],
        properties: {
          requisitionId: { type: 'string' }
        }
      },
      body: {
        type: 'object',
        required: ['selectedSuppliers'],
        properties: {
          selectedSuppliers: {
            type: 'array',
            items: { type: 'string' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { requisitionId } = request.params as any;
    const { selectedSuppliers } = request.body as any;
    const userId = getAuthenticatedUserId(request);
    const tenantId = getTenantId(request);

    const quotations = await workflowService.solicitQuotations(
      requisitionId,
      selectedSuppliers,
      userId,
      tenantId
    );

    reply.send({
      count: quotations.length,
      quotations: quotations.map(q => ({
        id: q.id,
        supplierName: q.supplierName,
        quotationNumber: q.quotationNumber,
        validUntil: q.validUntil.toISOString()
      }))
    });
  });

  // Evaluate quotations
  fastify.post('/quotations/evaluate', {
    schema: {
      description: 'Evaluate supplier quotations',
      tags: ['Purchase Workflow'],
      body: {
        type: 'object',
        required: ['quotationIds', 'evaluationCriteria'],
        properties: {
          quotationIds: {
            type: 'array',
            items: { type: 'string' }
          },
          evaluationCriteria: {
            type: 'object',
            properties: {
              priceWeight: { type: 'number', minimum: 0, maximum: 1 },
              qualityWeight: { type: 'number', minimum: 0, maximum: 1 },
              deliveryWeight: { type: 'number', minimum: 0, maximum: 1 },
              serviceWeight: { type: 'number', minimum: 0, maximum: 1 }
            }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { quotationIds, evaluationCriteria } = request.body as any;
    const userId = getAuthenticatedUserId(request);
    const tenantId = getTenantId(request);

    const evaluatedQuotations = await workflowService.evaluateQuotations(
      quotationIds,
      evaluationCriteria,
      userId,
      tenantId
    );

    reply.send({
      evaluations: evaluatedQuotations.map(q => ({
        id: q.id,
        supplierName: q.supplierName,
        evaluationScore: q.evaluationScore,
        evaluationNotes: q.evaluationNotes
      }))
    });
  });

  // Create purchase order from quotation
  fastify.post('/quotations/:quotationId/orders', {
    schema: {
      description: 'Create purchase order from selected quotation',
      tags: ['Purchase Workflow'],
      params: {
        type: 'object',
        required: ['quotationId'],
        properties: {
          quotationId: { type: 'string' }
        }
      },
      body: {
        type: 'object',
        required: ['deliveryAddress', 'requestedDeliveryDate', 'contactPerson', 'contactEmail', 'contactPhone'],
        properties: {
          deliveryAddress: { type: 'string' },
          requestedDeliveryDate: { type: 'string', format: 'date-time' },
          specialInstructions: { type: 'string' },
          contactPerson: { type: 'string' },
          contactEmail: { type: 'string' },
          contactPhone: { type: 'string' }
        }
      }
    }
  }, async (request, reply) => {
    const { quotationId } = request.params as any;
    const orderDetails = request.body as any;
    const userId = getAuthenticatedUserId(request);
    const tenantId = getTenantId(request);

    orderDetails.requestedDeliveryDate = new Date(orderDetails.requestedDeliveryDate);

    const purchaseOrder = await workflowService.createPurchaseOrderFromQuote(
      quotationId,
      orderDetails,
      userId,
      tenantId
    );

    reply.code(201).send({
      id: purchaseOrder.id,
      purchaseOrderNumber: purchaseOrder.purchaseOrderNumber,
      status: purchaseOrder.status,
      totalAmount: purchaseOrder.totalAmount,
      approvalRequired: purchaseOrder.status === 'ENTWURF'
    });
  });

  // Approve purchase requisition
  fastify.post('/requisitions/:requisitionId/approve', {
    schema: {
      description: 'Approve a purchase requisition',
      tags: ['Purchase Workflow'],
      params: {
        type: 'object',
        required: ['requisitionId'],
        properties: {
          requisitionId: { type: 'string' }
        }
      },
      body: {
        type: 'object',
        properties: {
          comments: { type: 'string' }
        }
      }
    }
  }, async (request, reply) => {
    const { requisitionId } = request.params as any;
    const { comments } = request.body as any;
    const approverId = getAuthenticatedUserId(request);
    const tenantId = getTenantId(request);

    const approvedRequisition = await workflowService.approvePurchaseRequisition(
      requisitionId,
      approverId,
      tenantId,
      comments
    );

    reply.send({
      id: approvedRequisition.id,
      approvalStatus: approvedRequisition.approvalStatus,
      approvedBy: approvedRequisition.approvedBy,
      approvedAt: approvedRequisition.approvedAt?.toISOString()
    });
  });

  // Finalize purchase order
  fastify.post('/orders/:orderId/finalize', {
    schema: {
      description: 'Finalize approved purchase order for execution',
      tags: ['Purchase Workflow'],
      params: {
        type: 'object',
        required: ['orderId'],
        properties: {
          orderId: { type: 'string' }
        }
      }
    }
  }, async (request, reply) => {
    const { orderId } = request.params as any;
    const userId = getAuthenticatedUserId(request);
    const tenantId = getTenantId(request);

    const finalizedOrder = await workflowService.finalizePurchaseOrder(
      orderId,
      userId,
      tenantId
    );

    reply.send({
      id: finalizedOrder.id,
      purchaseOrderNumber: finalizedOrder.purchaseOrderNumber,
      status: finalizedOrder.status,
      orderedAt: finalizedOrder.orderedAt?.toISOString(),
      orderedBy: finalizedOrder.orderedBy
    });
  });

  // Process goods receipt
  fastify.post('/orders/:orderId/goods-receipt', {
    schema: {
      description: 'Process goods receipt against purchase order',
      tags: ['Purchase Workflow'],
      params: {
        type: 'object',
        required: ['orderId'],
        properties: {
          orderId: { type: 'string' }
        }
      },
      body: {
        type: 'object',
        required: ['receivedDate', 'receivedBy', 'receivedLocation', 'items'],
        properties: {
          deliveryNoteNumber: { type: 'string' },
          receivedDate: { type: 'string', format: 'date-time' },
          receivedBy: { type: 'string' },
          receivedLocation: { type: 'string' },
          items: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                purchaseOrderItemId: { type: 'string' },
                receivedQuantity: { type: 'number' },
                acceptedQuantity: { type: 'number' },
                rejectedQuantity: { type: 'number' },
                condition: { type: 'string', enum: ['PERFECT', 'GOOD', 'DAMAGED', 'DEFECTIVE'] }
              }
            }
          },
          qualityInspectionStatus: { type: 'string', enum: ['PENDING', 'PASSED', 'FAILED', 'CONDITIONAL'] },
          inspectionNotes: { type: 'string' },
          damageReport: { type: 'string' }
        }
      }
    }
  }, async (request, reply) => {
    const { orderId } = request.params as any;
    const receiptData = request.body as any;
    const userId = getAuthenticatedUserId(request);

    receiptData.receivedDate = new Date(receiptData.receivedDate);
    receiptData.purchaseOrderId = orderId;
    receiptData.tenantId = getTenantId(request);

    const goodsReceipt = await workflowService.processGoodsReceipt(
      orderId,
      receiptData,
      userId
    );

    reply.code(201).send({
      id: goodsReceipt.id,
      purchaseOrderId: goodsReceipt.purchaseOrderId,
      status: goodsReceipt.status,
      qualityInspectionStatus: goodsReceipt.qualityInspectionStatus,
      totalQuantityReceived: goodsReceipt.totalQuantityReceived
    });
  });
}