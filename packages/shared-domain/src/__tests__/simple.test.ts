/**
 * Simple test to verify the Shared Domain is working
 */

import { Email, PhoneNumber, Money } from '../domain/value-objects/common-value-objects';

describe('Shared Domain - Basic Functionality', () => {
  it('should create and validate email', () => {
    const email = new Email('test@example.com');
    expect(email.getValue()).toBe('test@example.com');
  });

  it('should create and validate phone number', () => {
    const phone = new PhoneNumber('+1234567890');
    expect(phone.getValue()).toBe('+1234567890');
  });

  it('should create and calculate money', () => {
    const money1 = new Money(100, 'EUR');
    const money2 = new Money(50, 'EUR');
    const result = money1.add(money2);
    
    expect(result.amount).toBe(150);
    expect(result.currency).toBe('EUR');
  });

  it('should throw error for invalid email', () => {
    expect(() => new Email('invalid-email')).toThrow();
  });

  it('should throw error for different currencies', () => {
    const money1 = new Money(100, 'EUR');
    const money2 = new Money(50, 'USD');
    
    expect(() => money1.add(money2)).toThrow();
  });
});


