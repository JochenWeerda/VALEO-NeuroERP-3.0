/**
 * Purchase Order Integration Tests
 * Tests the complete Purchase Order workflow with ISO 27001 compliance
 */

import { PurchaseOrderService } from '../domain/services/purchase-order-service-complete';
import { ISMSAuditLogger } from '../../shared/security/isms-audit-logger';
import { CryptoService } from '../../shared/security/crypto-service';
import { PurchaseOrderStatus, PurchaseOrderItemType } from '../domain/entities/purchase-order';

describe('Purchase Order Integration Tests', () => {
  let purchaseOrderService: PurchaseOrderService;
  let mockAuditLogger: jest.Mocked<ISMSAuditLogger>;
  let mockCryptoService: jest.Mocked<CryptoService>;

  const testTenantId = 'test-tenant-001';
  const testUserId = 'test-user-001';

  beforeEach(() => {
    // Mock ISMS Audit Logger
    mockAuditLogger = {
      logSecureEvent: jest.fn().mockResolvedValue(void 0),
      logSecurityIncident: jest.fn().mockResolvedValue(void 0),
      logCommunicationEvent: jest.fn().mockResolvedValue(void 0),
      logDataAccess: jest.fn().mockResolvedValue(void 0),
      logAuthEvent: jest.fn().mockResolvedValue(void 0)
    } as jest.Mocked<ISMSAuditLogger>;

    // Mock Crypto Service
    mockCryptoService = {
      encrypt: jest.fn().mockResolvedValue({
        encrypted: 'encrypted-data',
        iv: 'test-iv',
        salt: 'test-salt',
        algorithm: 'aes-256-gcm',
        keyId: 'default'
      }),
      decrypt: jest.fn().mockResolvedValue('decrypted-data'),
      createHmac: jest.fn().mockResolvedValue('test-hmac'),
      verifyHmac: jest.fn().mockResolvedValue(true),
      hash: jest.fn().mockResolvedValue({ hash: 'test-hash', salt: 'test-salt' }),
      generateSecureRandom: jest.fn().mockResolvedValue('random-string'),
      rotateKey: jest.fn().mockResolvedValue({
        keyId: 'new-key-id',
        algorithm: 'aes-256-gcm',
        keySize: 256,
        purpose: 'ENCRYPTION' as const,
        createdAt: new Date(),
        expiresAt: new Date(),
        status: 'ACTIVE' as const,
        tenantId: testTenantId
      }),
      validateEncryptionStandards: jest.fn().mockReturnValue(true)
    } as jest.Mocked<CryptoService>;

    purchaseOrderService = new PurchaseOrderService(mockAuditLogger, mockCryptoService);
  });

  describe('Purchase Order Creation Workflow', () => {
    it('should create a new purchase order successfully', async () => {
      // Arrange
      const createInput = {
        supplierId: 'supplier-001',
        subject: 'Test Purchase Order',
        description: 'Integration test purchase order',
        deliveryDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000), // 2 weeks from now
        items: [
          {
            itemType: PurchaseOrderItemType.PRODUCT,
            description: 'Test Product 1',
            quantity: 10,
            unitPrice: 25.50,
            discountPercent: 5,
            articleId: 'ART-001',
            notes: 'High quality required'
          },
          {
            itemType: PurchaseOrderItemType.SERVICE,
            description: 'Installation Service',
            quantity: 1,
            unitPrice: 150.00,
            discountPercent: 0
          }
        ],
        contactPerson: 'John Procurement',
        paymentTerms: 'NET 30',
        currency: 'EUR',
        taxRate: 19.0,
        shippingAddress: {
          street: 'Test Street 123',
          postalCode: '12345',
          city: 'Test City',
          country: 'DE'
        },
        notes: 'Urgent delivery required'
      };

      // Act
      const result = await purchaseOrderService.createPurchaseOrder(
        createInput,
        testUserId,
        testTenantId
      );

      // Assert
      expect(result).toBeDefined();
      expect(result.supplierId).toBe('supplier-001');
      expect(result.subject).toBe('Test Purchase Order');
      expect(result.items).toHaveLength(2);
      expect(result.items[0].description).toBe('Test Product 1');
      expect(result.items[1].description).toBe('Installation Service');

      // Verify audit logging
      expect(mockAuditLogger.logSecureEvent).toHaveBeenCalledWith(
        'PURCHASE_ORDER_CREATED',
        expect.objectContaining({
          purchaseOrderId: result.id,
          supplierId: 'supplier-001',
          itemCount: 2
        }),
        testTenantId,
        testUserId
      );
    });

    it('should handle creation errors with proper audit logging', async () => {
      // Arrange
      const invalidInput = {
        supplierId: '', // Invalid empty supplier ID
        subject: 'Test',
        description: 'Test',
        deliveryDate: new Date(),
        items: []
      } as any;

      // Act & Assert
      await expect(
        purchaseOrderService.createPurchaseOrder(invalidInput, testUserId, testTenantId)
      ).rejects.toThrow();

      // Verify security incident logging
      expect(mockAuditLogger.logSecurityIncident).toHaveBeenCalledWith(
        'PURCHASE_ORDER_CREATION_FAILED',
        expect.objectContaining({
          supplierId: '',
          error: expect.any(String)
        }),
        testTenantId,
        testUserId
      );
    });
  });

  describe('Purchase Order Retrieval', () => {
    it('should retrieve purchase order by ID', async () => {
      // Act
      const result = await purchaseOrderService.getPurchaseOrderById(
        'test-po-id',
        testTenantId,
        testUserId
      );

      // Assert
      expect(result).toBeDefined();
      expect(result?.id).toBe('test-po-id');
      expect(result?.purchaseOrderNumber).toBe('PO-TEST-001');

      // Verify audit logging
      expect(mockAuditLogger.logSecureEvent).toHaveBeenCalledWith(
        'PURCHASE_ORDER_RETRIEVED',
        expect.objectContaining({
          purchaseOrderId: 'test-po-id',
          supplierId: result?.supplierId
        }),
        testTenantId,
        testUserId
      );
    });

    it('should return null for non-existent purchase order', async () => {
      // Act
      const result = await purchaseOrderService.getPurchaseOrderById(
        'non-existent-id',
        testTenantId,
        testUserId
      );

      // Assert
      expect(result).toBeNull();
    });
  });

  describe('Purchase Order Approval Workflow', () => {
    it('should approve purchase order successfully', async () => {
      // Act
      const result = await purchaseOrderService.approvePurchaseOrder(
        'test-po-id',
        testUserId,
        testTenantId
      );

      // Assert
      expect(result).toBeDefined();
      expect(result.id).toBe('test-po-id');

      // Verify audit logging
      expect(mockAuditLogger.logSecureEvent).toHaveBeenCalledWith(
        'PURCHASE_ORDER_APPROVED',
        expect.objectContaining({
          purchaseOrderId: 'test-po-id',
          approvedBy: testUserId
        }),
        testTenantId,
        testUserId
      );
    });

    it('should handle approval of non-existent purchase order', async () => {
      // Act & Assert
      await expect(
        purchaseOrderService.approvePurchaseOrder('non-existent', testUserId, testTenantId)
      ).rejects.toThrow('Purchase order not found');

      // Verify security incident logging
      expect(mockAuditLogger.logSecurityIncident).toHaveBeenCalledWith(
        'PURCHASE_ORDER_APPROVAL_FAILED',
        expect.objectContaining({
          purchaseOrderId: 'non-existent',
          error: expect.any(String)
        }),
        testTenantId,
        testUserId
      );
    });
  });

  describe('Purchase Order Listing with Pagination', () => {
    it('should list purchase orders with filtering and pagination', async () => {
      // Arrange
      const filter = {
        status: PurchaseOrderStatus.FREIGEGEBEN,
        supplierId: 'supplier-001'
      };
      const sort = {
        field: 'orderDate' as const,
        direction: 'desc' as const
      };

      // Act
      const result = await purchaseOrderService.listPurchaseOrders(
        filter,
        sort,
        1, // page
        10, // pageSize
        testTenantId
      );

      // Assert
      expect(result).toBeDefined();
      expect(result.items).toBeInstanceOf(Array);
      expect(result.currentPage).toBe(1);
      expect(result.pageSize).toBe(10);
      expect(result.totalCount).toBeDefined();
      expect(result.totalPages).toBeDefined();

      // Verify audit logging
      expect(mockAuditLogger.logSecureEvent).toHaveBeenCalledWith(
        'PURCHASE_ORDERS_LISTED',
        expect.objectContaining({
          filterApplied: true,
          resultCount: expect.any(Number),
          page: 1,
          pageSize: 10
        }),
        testTenantId
      );
    });
  });

  describe('Purchase Order Update Workflow', () => {
    it('should update purchase order successfully', async () => {
      // Arrange
      const updateInput = {
        subject: 'Updated Purchase Order',
        description: 'Updated description',
        notes: 'Updated notes'
      };

      // Act
      const result = await purchaseOrderService.updatePurchaseOrder(
        'test-po-id',
        updateInput,
        testUserId,
        testTenantId
      );

      // Assert
      expect(result).toBeDefined();
      expect(result.subject).toBe('Updated Purchase Order');

      // Verify audit logging
      expect(mockAuditLogger.logSecureEvent).toHaveBeenCalledWith(
        'PURCHASE_ORDER_UPDATED',
        expect.objectContaining({
          purchaseOrderId: 'test-po-id',
          updatedFields: ['subject', 'description', 'notes']
        }),
        testTenantId,
        testUserId
      );
    });
  });

  describe('Purchase Order Lifecycle Management', () => {
    it('should handle complete purchase order lifecycle', async () => {
      const poId = 'test-po-id';

      // 1. Order (send to supplier)
      await purchaseOrderService.orderPurchaseOrder(poId, testUserId, testTenantId);
      expect(mockAuditLogger.logSecureEvent).toHaveBeenCalledWith(
        'PURCHASE_ORDER_ORDERED',
        expect.any(Object),
        testTenantId,
        testUserId
      );

      // 2. Mark as partially delivered
      await purchaseOrderService.markPartiallyDelivered(poId, testUserId, testTenantId);
      expect(mockAuditLogger.logSecureEvent).toHaveBeenCalledWith(
        'PURCHASE_ORDER_PARTIALLY_DELIVERED',
        expect.any(Object),
        testTenantId,
        testUserId
      );

      // 3. Mark as fully delivered
      await purchaseOrderService.markDelivered(poId, testUserId, testTenantId);
      expect(mockAuditLogger.logSecureEvent).toHaveBeenCalledWith(
        'PURCHASE_ORDER_DELIVERED',
        expect.any(Object),
        testTenantId,
        testUserId
      );
    });

    it('should handle purchase order cancellation', async () => {
      const poId = 'test-po-id';
      const reason = 'Supplier unavailable';

      // Act
      const result = await purchaseOrderService.cancelPurchaseOrder(
        poId,
        reason,
        testUserId,
        testTenantId
      );

      // Assert
      expect(result).toBeDefined();
      expect(mockAuditLogger.logSecureEvent).toHaveBeenCalledWith(
        'PURCHASE_ORDER_CANCELLED',
        expect.objectContaining({
          purchaseOrderId: poId,
          reason,
          cancelledBy: testUserId
        }),
        testTenantId,
        testUserId
      );
    });
  });

  describe('ISO 27001 Compliance Tests', () => {
    it('should log all security events with proper audit trail', async () => {
      // Arrange
      const createInput = {
        supplierId: 'supplier-001',
        subject: 'Security Test PO',
        description: 'Testing security compliance',
        deliveryDate: new Date(),
        items: []
      };

      // Act - Perform multiple operations
      const po = await purchaseOrderService.createPurchaseOrder(createInput, testUserId, testTenantId);
      await purchaseOrderService.getPurchaseOrderById(po.id, testTenantId, testUserId);
      await purchaseOrderService.approvePurchaseOrder(po.id, testUserId, testTenantId);

      // Assert - Verify all operations were logged
      expect(mockAuditLogger.logSecureEvent).toHaveBeenCalledTimes(3);
      
      // Verify event types
      const calls = mockAuditLogger.logSecureEvent.mock.calls;
      expect(calls[0][0]).toBe('PURCHASE_ORDER_CREATED');
      expect(calls[1][0]).toBe('PURCHASE_ORDER_RETRIEVED');
      expect(calls[2][0]).toBe('PURCHASE_ORDER_APPROVED');

      // Verify tenant isolation
      calls.forEach(call => {
        expect(call[2]).toBe(testTenantId); // tenantId parameter
      });
    });

    it('should log security incidents for error scenarios', async () => {
      // Act - Trigger various error scenarios
      await expect(
        purchaseOrderService.approvePurchaseOrder('invalid-id', testUserId, testTenantId)
      ).rejects.toThrow();

      await expect(
        purchaseOrderService.updatePurchaseOrder('invalid-id', {}, testUserId, testTenantId)
      ).rejects.toThrow();

      // Assert - Verify security incidents were logged
      expect(mockAuditLogger.logSecurityIncident).toHaveBeenCalledTimes(2);
      
      const incidentCalls = mockAuditLogger.logSecurityIncident.mock.calls;
      expect(incidentCalls[0][0]).toBe('PURCHASE_ORDER_APPROVAL_FAILED');
      expect(incidentCalls[1][0]).toBe('PURCHASE_ORDER_UPDATE_FAILED');
    });
  });

  describe('Performance Tests', () => {
    it('should handle concurrent operations efficiently', async () => {
      // Arrange
      const concurrentOperations = Array.from({ length: 10 }, (_, i) => 
        purchaseOrderService.getPurchaseOrderById(`test-po-${i}`, testTenantId, testUserId)
      );

      // Act
      const startTime = Date.now();
      const results = await Promise.all(concurrentOperations);
      const endTime = Date.now();

      // Assert
      expect(results).toHaveLength(10);
      expect(endTime - startTime).toBeLessThan(1000); // Should complete within 1 second
      
      // Verify all operations were logged
      expect(mockAuditLogger.logSecureEvent).toHaveBeenCalledTimes(1); // Only one valid ID
    });
  });
});
