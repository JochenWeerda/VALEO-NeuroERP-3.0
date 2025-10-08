/**
 * Tests for Value Objects
 */

import { Email, PhoneNumber, Address, Money, Percentage, DateRange } from '../domain/value-objects/common-value-objects.js';
import { createUserId, createTenantId } from '../domain/value-objects/branded-types.js';

describe('Value Objects', () => {
  describe('Email', () => {
    it('should create a valid email', () => {
      const email = new Email('test@example.com');
      expect(email.getValue()).toBe('test@example.com');
    });

    it('should normalize email to lowercase', () => {
      const email = new Email('TEST@EXAMPLE.COM');
      expect(email.getValue()).toBe('test@example.com');
    });

    it('should throw error for invalid email', () => {
      expect(() => new Email('invalid-email')).toThrow();
    });

    it('should compare emails correctly', () => {
      const email1 = new Email('test@example.com');
      const email2 = new Email('TEST@EXAMPLE.COM');
      expect(email1.equals(email2)).toBe(true);
    });
  });

  describe('PhoneNumber', () => {
    it('should create a valid phone number', () => {
      const phone = new PhoneNumber('+1234567890');
      expect(phone.getValue()).toBe('+1234567890');
    });

    it('should throw error for invalid phone number', () => {
      expect(() => new PhoneNumber('abc')).toThrow();
    });

    it('should compare phone numbers correctly', () => {
      const phone1 = new PhoneNumber('+1234567890');
      const phone2 = new PhoneNumber('+1234567890');
      expect(phone1.equals(phone2)).toBe(true);
    });
  });

  describe('Address', () => {
    it('should create a valid address', () => {
      const address = new Address('123 Main St', 'City', '12345', 'Country');
      expect(address.street).toBe('123 Main St');
      expect(address.city).toBe('City');
      expect(address.postalCode).toBe('12345');
      expect(address.country).toBe('Country');
    });

    it('should create full address string', () => {
      const address = new Address('123 Main St', 'City', '12345', 'Country');
      expect(address.getFullAddress()).toBe('123 Main St, City, 12345, Country');
    });

    it('should compare addresses correctly', () => {
      const address1 = new Address('123 Main St', 'City', '12345', 'Country');
      const address2 = new Address('123 Main St', 'City', '12345', 'Country');
      expect(address1.equals(address2)).toBe(true);
    });
  });

  describe('Money', () => {
    it('should create a valid money amount', () => {
      const money = new Money(100.50, 'EUR');
      expect(money.amount).toBe(100.50);
      expect(money.currency).toBe('EUR');
    });

    it('should add money amounts', () => {
      const money1 = new Money(100, 'EUR');
      const money2 = new Money(50, 'EUR');
      const result = money1.add(money2);
      expect(result.amount).toBe(150);
      expect(result.currency).toBe('EUR');
    });

    it('should throw error for different currencies', () => {
      const money1 = new Money(100, 'EUR');
      const money2 = new Money(50, 'USD');
      expect(() => money1.add(money2)).toThrow();
    });

    it('should multiply money amount', () => {
      const money = new Money(100, 'EUR');
      const result = money.multiply(2);
      expect(result.amount).toBe(200);
      expect(result.currency).toBe('EUR');
    });
  });

  describe('Percentage', () => {
    it('should create a valid percentage', () => {
      const percentage = new Percentage(50);
      expect(percentage.getValue()).toBe(50);
      expect(percentage.getDecimal()).toBe(0.5);
    });

    it('should throw error for invalid percentage', () => {
      expect(() => new Percentage(150)).toThrow();
      expect(() => new Percentage(-10)).toThrow();
    });
  });

  describe('DateRange', () => {
    it('should create a valid date range', () => {
      const startDate = new Date('2023-01-01');
      const endDate = new Date('2023-12-31');
      const dateRange = new DateRange(startDate, endDate);
      
      expect(dateRange.startDate).toBe(startDate);
      expect(dateRange.endDate).toBe(endDate);
    });

    it('should throw error for invalid date range', () => {
      const startDate = new Date('2023-12-31');
      const endDate = new Date('2023-01-01');
      expect(() => new DateRange(startDate, endDate)).toThrow();
    });

    it('should check if date is contained in range', () => {
      const startDate = new Date('2023-01-01');
      const endDate = new Date('2023-12-31');
      const dateRange = new DateRange(startDate, endDate);
      
      expect(dateRange.contains(new Date('2023-06-15'))).toBe(true);
      expect(dateRange.contains(new Date('2022-12-31'))).toBe(false);
    });
  });

  describe('Branded Types', () => {
    it('should create branded types', () => {
      const userId = createUserId('user-123');
      const tenantId = createTenantId('tenant-456');
      
      expect(userId).toBe('user-123');
      expect(tenantId).toBe('tenant-456');
    });
  });
});


