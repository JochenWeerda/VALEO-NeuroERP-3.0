/**
 * Sales-to-Cash Integration Tests
 * Complete End-to-End Testing: Offer → Order → Delivery → Invoice
 */

import { SalesOfferService } from '../domain/services/sales-offer-service';
import { SalesOfferRepository } from '../infra/repositories/sales-offer-repository';
import { SalesOrderService } from '../domain/services/sales-order-service';
import { SalesOrderRepository } from '../infra/repositories/sales-order-repository';
import { DeliveryNoteService } from '../domain/services/delivery-note-service';
import { DeliveryNoteRepository } from '../infra/repositories/delivery-note-repository';
import { SalesInvoiceService } from '../domain/services/sales-invoice-service';
import { SalesInvoiceRepository } from '../infra/repositories/sales-invoice-repository';

describe('Sales-to-Cash Integration Tests', () => {
  let salesOfferService: SalesOfferService;
  let salesOrderService: SalesOrderService;
  let deliveryNoteService: DeliveryNoteService;
  let salesInvoiceService: SalesInvoiceService;

  // Test data
  const testUser = 'test-user-123';
  const testCustomerId = 'customer-456';
  const testDeliveryDate = new Date('2024-12-01');
  const testAddress = {
    name: 'Test Customer GmbH',
    street: 'Teststraße 123',
    postalCode: '12345',
    city: 'Teststadt',
    country: 'Deutschland'
  };

  beforeEach(() => {
    // Initialize repositories
    const salesOfferRepository = new SalesOfferRepository();
    const salesOrderRepository = new SalesOrderRepository();
    const deliveryNoteRepository = new DeliveryNoteRepository();
    const salesInvoiceRepository = new SalesInvoiceRepository();

    // Initialize services
    salesOfferService = new SalesOfferService({ salesOfferRepository });
    salesOrderService = new SalesOrderService({ salesOrderRepository, salesOfferService });
    deliveryNoteService = new DeliveryNoteService({ deliveryNoteRepository, salesOrderService });
    salesInvoiceService = new SalesInvoiceService({ 
      salesInvoiceRepository, 
      deliveryNoteService, 
      salesOrderService 
    });
  });

  describe('Complete Sales-to-Cash Workflow', () => {
    test('should execute full workflow: Offer → Order → Delivery → Invoice', async () => {
      // ================================
      // STEP 1: CREATE SALES OFFER
      // ================================
      const offerInput = {
        customerId: testCustomerId,
        subject: 'Test Sales Offer',
        description: 'Integration test sales offer',
        validUntil: new Date('2024-12-31'),
        items: [
          {
            itemType: 'PRODUCT' as const,
            articleId: 'ART-001',
            description: 'Test Product 1',
            quantity: 10,
            unitPrice: 100.00,
            discountPercent: 5,
            taxRate: 19,
            deliveryDate: testDeliveryDate
          },
          {
            itemType: 'SERVICE' as const,
            description: 'Installation Service',
            quantity: 1,
            unitPrice: 250.00,
            discountPercent: 0,
            taxRate: 19,
            deliveryDate: testDeliveryDate
          }
        ]
      };

      const offer = await salesOfferService.createSalesOffer(offerInput, testUser);
      
      // Verify offer creation
      expect(offer.id).toBeDefined();
      expect(offer.customerId).toBe(testCustomerId);
      expect(offer.status).toBe('ENTWURF');
      expect(offer.items).toHaveLength(2);
      expect(offer.totalAmount).toBeGreaterThan(0);
      
      console.log(`✅ Step 1 Complete: Created Sales Offer ${offer.offerNumber} - Total: €${offer.totalAmount}`);

      // ================================
      // STEP 2: FINALIZE AND ACCEPT OFFER
      // ================================
      await salesOfferService.finalizeSalesOffer(offer.id, testUser);
      await salesOfferService.acceptSalesOffer(offer.id, testUser);

      const finalizedOffer = await salesOfferService.getSalesOfferById(offer.id);
      expect(finalizedOffer?.status).toBe('ANGENOMMEN');
      
      console.log(`✅ Step 2 Complete: Finalized and Accepted Offer ${offer.offerNumber}`);

      // ================================
      // STEP 3: CONVERT OFFER TO ORDER
      // ================================
      const order = await salesOrderService.convertOfferToOrder(
        offer.id,
        testUser,
        {
          deliveryDate: testDeliveryDate,
          paymentTerms: '30 days net',
          notes: 'Integration test order'
        }
      );

      // Verify order creation
      expect(order.id).toBeDefined();
      expect(order.sourceOfferId).toBe(offer.id);
      expect(order.customerId).toBe(testCustomerId);
      expect(order.status).toBe('DRAFT');
      expect(order.items).toHaveLength(2);
      expect(order.totalAmount).toBe(offer.totalAmount);
      
      console.log(`✅ Step 3 Complete: Converted to Sales Order ${order.orderNumber} - Total: €${order.totalAmount}`);

      // ================================
      // STEP 4: CONFIRM ORDER
      // ================================
      await salesOrderService.confirmOrder(order.id, testUser);
      const confirmedOrder = await salesOrderService.getSalesOrderById(order.id);
      expect(confirmedOrder?.status).toBe('CONFIRMED');
      
      console.log(`✅ Step 4 Complete: Confirmed Order ${order.orderNumber}`);

      // ================================
      // STEP 5: CONVERT ORDER TO DELIVERY NOTE
      // ================================
      const deliveryNote = await deliveryNoteService.convertOrderToDeliveryNote(
        order.id,
        testUser,
        {
          plannedDeliveryDate: testDeliveryDate,
          deliveryAddress: testAddress,
          carrierInfo: {
            carrierName: 'Test Logistics GmbH',
            trackingNumber: 'TRK-123456',
            carrierService: 'Standard Delivery'
          },
          specialInstructions: 'Handle with care - integration test'
        }
      );

      // Verify delivery note creation
      expect(deliveryNote.id).toBeDefined();
      expect(deliveryNote.orderId).toBe(order.id);
      expect(deliveryNote.customerId).toBe(testCustomerId);
      expect(deliveryNote.status).toBe('PREPARED');
      expect(deliveryNote.items).toHaveLength(2);
      expect(deliveryNote.totalAmount).toBe(order.totalAmount);
      
      console.log(`✅ Step 5 Complete: Created Delivery Note ${deliveryNote.deliveryNoteNumber} - Total: €${deliveryNote.totalAmount}`);

      // ================================
      // STEP 6: PROCESS DELIVERY WORKFLOW
      // ================================
      
      // Mark ready for pickup
      await deliveryNoteService.markReadyForPickup(deliveryNote.id, testUser);
      let updatedDeliveryNote = await deliveryNoteService.getDeliveryNoteById(deliveryNote.id);
      expect(updatedDeliveryNote?.status).toBe('READY_FOR_PICKUP');
      
      // Mark in transit
      await deliveryNoteService.markInTransit(deliveryNote.id, testUser, 'TRK-123456-UPD');
      updatedDeliveryNote = await deliveryNoteService.getDeliveryNoteById(deliveryNote.id);
      expect(updatedDeliveryNote?.status).toBe('IN_TRANSIT');
      
      // Mark delivered
      await deliveryNoteService.markDelivered(deliveryNote.id, new Date());
      updatedDeliveryNote = await deliveryNoteService.getDeliveryNoteById(deliveryNote.id);
      expect(updatedDeliveryNote?.status).toBe('DELIVERED');
      
      // Confirm delivery
      await deliveryNoteService.confirmDelivery(deliveryNote.id, testUser, {
        signatureBase64: 'base64-signature-data',
        recipientName: 'Max Mustermann',
        notes: 'Delivery confirmed by customer'
      });
      updatedDeliveryNote = await deliveryNoteService.getDeliveryNoteById(deliveryNote.id);
      expect(updatedDeliveryNote?.status).toBe('CONFIRMED');
      
      console.log(`✅ Step 6 Complete: Delivery Workflow - Status: ${updatedDeliveryNote?.status}`);

      // ================================
      // STEP 7: CONVERT DELIVERY TO INVOICE
      // ================================
      const invoice = await salesInvoiceService.convertDeliveryToInvoice(
        deliveryNote.id,
        testUser,
        {
          invoiceDate: new Date(),
          dueDate: new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000), // 30 days from now
          paymentTerms: '30 days net',
          currency: 'EUR',
          billingAddress: testAddress,
          notes: 'Integration test invoice'
        }
      );

      // Verify invoice creation
      expect(invoice.id).toBeDefined();
      expect(invoice.sourceOrderId).toBe(order.id);
      expect(invoice.sourceDeliveryNoteId).toBe(deliveryNote.id);
      expect(invoice.customerId).toBe(testCustomerId);
      expect(invoice.status).toBe('DRAFT');
      expect(invoice.items).toHaveLength(2);
      expect(invoice.totalAmount).toBe(deliveryNote.totalAmount);
      
      console.log(`✅ Step 7 Complete: Created Invoice ${invoice.invoiceNumber} - Total: €${invoice.totalAmount}`);

      // ================================
      // STEP 8: PROCESS INVOICE WORKFLOW
      // ================================
      
      // Issue invoice
      await salesInvoiceService.issueInvoice(invoice.id, testUser);
      let updatedInvoice = await salesInvoiceService.getSalesInvoiceById(invoice.id);
      expect(updatedInvoice?.status).toBe('ISSUED');
      
      // Send invoice
      await salesInvoiceService.sendInvoice(invoice.id, testUser);
      updatedInvoice = await salesInvoiceService.getSalesInvoiceById(invoice.id);
      expect(updatedInvoice?.status).toBe('SENT');
      
      // Record partial payment
      const partialPayment = invoice.totalAmount * 0.5;
      await salesInvoiceService.recordPayment(invoice.id, partialPayment, testUser);
      updatedInvoice = await salesInvoiceService.getSalesInvoiceById(invoice.id);
      expect(updatedInvoice?.status).toBe('PARTIAL_PAID');
      expect(updatedInvoice?.paidAmount).toBe(partialPayment);
      
      // Record final payment
      const remainingPayment = invoice.totalAmount - partialPayment;
      await salesInvoiceService.recordPayment(invoice.id, remainingPayment, testUser);
      updatedInvoice = await salesInvoiceService.getSalesInvoiceById(invoice.id);
      expect(updatedInvoice?.status).toBe('PAID');
      expect(updatedInvoice?.paidAmount).toBe(invoice.totalAmount);
      expect(updatedInvoice?.remainingAmount).toBe(0);
      
      console.log(`✅ Step 8 Complete: Invoice Workflow - Status: ${updatedInvoice?.status}, Paid: €${updatedInvoice?.paidAmount}`);

      // ================================
      // STEP 9: VERIFY FINAL STATE
      // ================================
      
      // Verify order is fully processed
      const finalOrder = await salesOrderService.getSalesOrderById(order.id);
      expect(finalOrder?.status).toBe('INVOICED'); // Should be updated after invoice completion
      
      // Verify all entities are linked correctly
      expect(finalOrder?.sourceOfferId).toBe(offer.id);
      expect(deliveryNote.orderId).toBe(order.id);
      expect(invoice.sourceOrderId).toBe(order.id);
      expect(invoice.sourceDeliveryNoteId).toBe(deliveryNote.id);
      
      console.log(`✅ Step 9 Complete: Final State Verification Passed`);

      // ================================
      // STEP 10: BUSINESS METRICS VERIFICATION
      // ================================
      
      // Verify statistics
      const offerStats = await salesOfferService.getSalesOfferStatistics();
      expect(offerStats.total).toBeGreaterThanOrEqual(1);
      expect(offerStats.byStatus['ANGENOMMEN']).toBeGreaterThanOrEqual(1);
      
      const orderStats = await salesOrderService.getSalesOrderStatistics();
      expect(orderStats.total).toBeGreaterThanOrEqual(1);
      expect(orderStats.totalValue).toBeGreaterThanOrEqual(invoice.totalAmount);
      
      const deliveryStats = await deliveryNoteService.getDeliveryStatistics();
      expect(deliveryStats.total).toBeGreaterThanOrEqual(1);
      expect(deliveryStats.byStatus['CONFIRMED']).toBeGreaterThanOrEqual(1);
      
      const invoiceStats = await salesInvoiceService.getSalesInvoiceStatistics();
      expect(invoiceStats.total).toBeGreaterThanOrEqual(1);
      expect(invoiceStats.byStatus['PAID']).toBeGreaterThanOrEqual(1);
      expect(invoiceStats.totalPaid).toBeGreaterThanOrEqual(invoice.totalAmount);
      
      console.log(`✅ Step 10 Complete: Business Metrics Verified`);

      // ================================
      // SUCCESS MESSAGE
      // ================================
      console.log(`\n🎉 SALES-TO-CASH INTEGRATION TEST SUCCESSFUL!`);
      console.log(`📊 Workflow Summary:`);
      console.log(`   • Offer: ${offer.offerNumber} (€${offer.totalAmount}) - Status: ANGENOMMEN`);
      console.log(`   • Order: ${order.orderNumber} (€${order.totalAmount}) - Status: INVOICED`);
      console.log(`   • Delivery: ${deliveryNote.deliveryNoteNumber} (€${deliveryNote.totalAmount}) - Status: CONFIRMED`);
      console.log(`   • Invoice: ${invoice.invoiceNumber} (€${invoice.totalAmount}) - Status: PAID`);
      console.log(`\n✅ Complete Sales-to-Cash workflow executed successfully without mocks!`);
    });

    test('should handle partial deliveries and invoicing', async () => {
      // Create a simple offer
      const offerInput = {
        customerId: testCustomerId,
        subject: 'Partial Delivery Test',
        description: 'Test partial deliveries and invoicing',
        validUntil: new Date('2024-12-31'),
        items: [{
          itemType: 'PRODUCT' as const,
          articleId: 'ART-PARTIAL',
          description: 'Partially Delivered Product',
          quantity: 100,
          unitPrice: 10.00,
          discountPercent: 0,
          taxRate: 19,
          deliveryDate: testDeliveryDate
        }]
      };

      // Create, finalize, and accept offer
      const offer = await salesOfferService.createSalesOffer(offerInput, testUser);
      await salesOfferService.finalizeSalesOffer(offer.id, testUser);
      await salesOfferService.acceptSalesOffer(offer.id, testUser);

      // Convert to order and confirm
      const order = await salesOrderService.convertOfferToOrder(offer.id, testUser);
      await salesOrderService.confirmOrder(order.id, testUser);

      // Create partial delivery (50 out of 100 units)
      const deliveryNote1 = await deliveryNoteService.convertOrderToDeliveryNote(
        order.id,
        testUser,
        {
          plannedDeliveryDate: testDeliveryDate,
          deliveryAddress: testAddress,
          partialDelivery: {
            itemQuantities: { [order.items[0].id]: 50 }
          }
        }
      );

      // Verify partial delivery
      expect(deliveryNote1.items[0].deliveredQuantity).toBe(50);
      expect(deliveryNote1.items[0].orderedQuantity).toBe(100);

      // Complete delivery workflow
      await deliveryNoteService.markReadyForPickup(deliveryNote1.id, testUser);
      await deliveryNoteService.markInTransit(deliveryNote1.id, testUser);
      await deliveryNoteService.markDelivered(deliveryNote1.id);
      await deliveryNoteService.confirmDelivery(deliveryNote1.id, testUser);

      // Create partial invoice (30 out of 50 delivered units)
      const invoice1 = await salesInvoiceService.convertDeliveryToInvoice(
        deliveryNote1.id,
        testUser,
        {
          billingAddress: testAddress,
          partialInvoicing: {
            itemQuantities: { [deliveryNote1.items[0].id]: 30 }
          }
        }
      );

      // Verify partial invoice
      expect(invoice1.items[0].invoicedQuantity).toBe(30);
      expect(invoice1.items[0].deliveredQuantity).toBe(50);
      expect(invoice1.totalAmount).toBe(30 * 10 * 1.19); // 30 units * €10 * 1.19 (19% VAT)

      console.log(`✅ Partial Delivery and Invoicing Test Completed Successfully`);
    });

    test('should handle error cases and validations', async () => {
      // Test converting non-existent offer to order
      await expect(
        salesOrderService.convertOfferToOrder('non-existent-id', testUser)
      ).rejects.toThrow('Sales offer not found');

      // Test converting non-confirmed order to delivery
      const offerInput = {
        customerId: testCustomerId,
        subject: 'Error Test Offer',
        description: 'Test error handling',
        validUntil: new Date('2024-12-31'),
        items: [{
          itemType: 'PRODUCT' as const,
          description: 'Test Product',
          quantity: 1,
          unitPrice: 100.00,
          discountPercent: 0,
          taxRate: 19,
          deliveryDate: testDeliveryDate
        }]
      };

      const offer = await salesOfferService.createSalesOffer(offerInput, testUser);
      await salesOfferService.finalizeSalesOffer(offer.id, testUser);
      await salesOfferService.acceptSalesOffer(offer.id, testUser);
      const order = await salesOrderService.convertOfferToOrder(offer.id, testUser);

      // Try to create delivery from non-confirmed order
      await expect(
        deliveryNoteService.convertOrderToDeliveryNote(order.id, testUser, {
          plannedDeliveryDate: testDeliveryDate,
          deliveryAddress: testAddress
        })
      ).rejects.toThrow('Can only create delivery notes from confirmed or in-progress orders');

      // Test converting non-delivered delivery note to invoice
      await salesOrderService.confirmOrder(order.id, testUser);
      const deliveryNote = await deliveryNoteService.convertOrderToDeliveryNote(order.id, testUser, {
        plannedDeliveryDate: testDeliveryDate,
        deliveryAddress: testAddress
      });

      await expect(
        salesInvoiceService.convertDeliveryToInvoice(deliveryNote.id, testUser, {
          billingAddress: testAddress
        })
      ).rejects.toThrow('Can only create invoices from delivered or confirmed delivery notes');

      console.log(`✅ Error Handling and Validations Test Completed Successfully`);
    });
  });

  describe('Status Workflow Tests', () => {
    test('should enforce correct status transitions', async () => {
      // Create basic entities for status testing
      const offerInput = {
        customerId: testCustomerId,
        subject: 'Status Test Offer',
        description: 'Test status workflows',
        validUntil: new Date('2024-12-31'),
        items: [{
          itemType: 'PRODUCT' as const,
          description: 'Status Test Product',
          quantity: 1,
          unitPrice: 100.00,
          discountPercent: 0,
          taxRate: 19,
          deliveryDate: testDeliveryDate
        }]
      };

      const offer = await salesOfferService.createSalesOffer(offerInput, testUser);
      
      // Test offer status transitions
      expect(offer.status).toBe('ENTWURF');
      
      await salesOfferService.finalizeSalesOffer(offer.id, testUser);
      const finalizedOffer = await salesOfferService.getSalesOfferById(offer.id);
      expect(finalizedOffer?.status).toBe('VERSENDET');
      
      await salesOfferService.acceptSalesOffer(offer.id, testUser);
      const acceptedOffer = await salesOfferService.getSalesOfferById(offer.id);
      expect(acceptedOffer?.status).toBe('ANGENOMMEN');

      // Test order status transitions
      const order = await salesOrderService.convertOfferToOrder(offer.id, testUser);
      expect(order.status).toBe('DRAFT');
      
      await salesOrderService.confirmOrder(order.id, testUser);
      const confirmedOrder = await salesOrderService.getSalesOrderById(order.id);
      expect(confirmedOrder?.status).toBe('CONFIRMED');
      
      // Test delivery status transitions
      const deliveryNote = await deliveryNoteService.convertOrderToDeliveryNote(order.id, testUser, {
        plannedDeliveryDate: testDeliveryDate,
        deliveryAddress: testAddress
      });
      expect(deliveryNote.status).toBe('PREPARED');
      
      await deliveryNoteService.markReadyForPickup(deliveryNote.id, testUser);
      await deliveryNoteService.markInTransit(deliveryNote.id, testUser);
      await deliveryNoteService.markDelivered(deliveryNote.id);
      await deliveryNoteService.confirmDelivery(deliveryNote.id, testUser);
      
      const finalDeliveryNote = await deliveryNoteService.getDeliveryNoteById(deliveryNote.id);
      expect(finalDeliveryNote?.status).toBe('CONFIRMED');
      
      // Test invoice status transitions
      const invoice = await salesInvoiceService.convertDeliveryToInvoice(deliveryNote.id, testUser, {
        billingAddress: testAddress
      });
      expect(invoice.status).toBe('DRAFT');
      
      await salesInvoiceService.issueInvoice(invoice.id, testUser);
      await salesInvoiceService.sendInvoice(invoice.id, testUser);
      await salesInvoiceService.recordPayment(invoice.id, invoice.totalAmount, testUser);
      
      const finalInvoice = await salesInvoiceService.getSalesInvoiceById(invoice.id);
      expect(finalInvoice?.status).toBe('PAID');

      console.log(`✅ Status Workflow Tests Completed Successfully`);
    });
  });
});
