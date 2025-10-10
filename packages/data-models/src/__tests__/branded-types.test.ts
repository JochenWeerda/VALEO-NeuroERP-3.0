const { createCustomerId, createProductId, createOrderId, createId } = require('../branded-types');

describe('Branded Types', () => {
  describe('createId', () => {
    it('should create a valid Id', () => {
      const id = createId('test-id');
      expect(id).toBe('test-id');
      expect(typeof id).toBe('string');
    });
  });

  describe('createCustomerId', () => {
    it('should create a CustomerId', () => {
      const customerId = createCustomerId('customer-123');
      expect(customerId).toBe('customer-123');
      expect(typeof customerId).toBe('string');
    });
  });

  describe('createProductId', () => {
    it('should create a ProductId', () => {
      const productId = createProductId('product-456');
      expect(productId).toBe('product-456');
      expect(typeof productId).toBe('string');
    });
  });

  describe('createOrderId', () => {
    it('should create an OrderId', () => {
      const orderId = createOrderId('order-789');
      expect(orderId).toBe('order-789');
      expect(typeof orderId).toBe('string');
    });
  });
});