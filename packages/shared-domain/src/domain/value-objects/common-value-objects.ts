/**
 * Common Value Objects for VALEO NeuroERP 3.0
 * Reusable value objects across all domains
 */

import { z } from 'zod';

// Email Value Object
export class Email {
  private readonly value: string;

  constructor(email: string) {
    const emailSchema = z.string().email();
    const validatedEmail = emailSchema.parse(email);
    this.value = validatedEmail.toLowerCase();
  }

  getValue(): string {
    return this.value;
  }

  equals(other: Email): boolean {
    return this.value === other.value;
  }

  toString(): string {
    return this.value;
  }
}

// Phone Number Value Object
export class PhoneNumber {
  private readonly value: string;

  constructor(phone: string) {
    // Basic phone validation - can be enhanced based on requirements
    const phoneSchema = z.string().min(10).max(15).regex(/^[\+]?[0-9\s\-\(\)]+$/);
    this.value = phoneSchema.parse(phone);
  }

  getValue(): string {
    return this.value;
  }

  equals(other: PhoneNumber): boolean {
    return this.value === other.value;
  }

  toString(): string {
    return this.value;
  }
}

// Address Value Object
export class Address {
  constructor(
    public readonly street: string,
    public readonly city: string,
    public readonly postalCode: string,
    public readonly country: string,
    public readonly state?: string
  ) {
    this.validate();
  }

  private validate(): void {
    const addressSchema = z.object({
      street: z.string().min(1).max(200),
      city: z.string().min(1).max(100),
      postalCode: z.string().min(1).max(20),
      country: z.string().min(2).max(100),
      state: z.string().min(1).max(100).optional()
    });

    addressSchema.parse({
      street: this.street,
      city: this.city,
      postalCode: this.postalCode,
      country: this.country,
      state: this.state
    });
  }

  getFullAddress(): string {
    const parts = [this.street, this.city, this.postalCode];
    if (this.state) {
      parts.push(this.state);
    }
    parts.push(this.country);
    return parts.join(', ');
  }

  equals(other: Address): boolean {
    return (
      this.street === other.street &&
      this.city === other.city &&
      this.postalCode === other.postalCode &&
      this.country === other.country &&
      this.state === other.state
    );
  }
}

// Money Value Object
export class Money {
  constructor(
    public readonly amount: number,
    public readonly currency: string = 'EUR'
  ) {
    this.validate();
  }

  private validate(): void {
    const moneySchema = z.object({
      amount: z.number().finite().min(0),
      currency: z.string().length(3).toUpperCase()
    });

    moneySchema.parse({
      amount: this.amount,
      currency: this.currency
    });
  }

  add(other: Money): Money {
    this.validateSameCurrency(other);
    return new Money(this.amount + other.amount, this.currency);
  }

  subtract(other: Money): Money {
    this.validateSameCurrency(other);
    return new Money(this.amount - other.amount, this.currency);
  }

  multiply(factor: number): Money {
    return new Money(this.amount * factor, this.currency);
  }

  divide(divisor: number): Money {
    if (divisor === 0) {
      throw new Error('Division by zero is not allowed');
    }
    return new Money(this.amount / divisor, this.currency);
  }

  private validateSameCurrency(other: Money): void {
    if (this.currency !== other.currency) {
      throw new Error(`Currency mismatch: ${this.currency} vs ${other.currency}`);
    }
  }

  equals(other: Money): boolean {
    return this.amount === other.amount && this.currency === other.currency;
  }

  toString(): string {
    return `${this.amount.toFixed(2)} ${this.currency}`;
  }
}

// Percentage Value Object
export class Percentage {
  private readonly value: number;

  constructor(value: number) {
    const percentageSchema = z.number().min(0).max(100);
    this.value = percentageSchema.parse(value);
  }

  getValue(): number {
    return this.value;
  }

  getDecimal(): number {
    return this.value / 100;
  }

  equals(other: Percentage): boolean {
    return this.value === other.value;
  }

  toString(): string {
    return `${this.value}%`;
  }
}

// Date Range Value Object
export class DateRange {
  constructor(
    public readonly startDate: Date,
    public readonly endDate: Date
  ) {
    this.validate();
  }

  private validate(): void {
    if (this.startDate >= this.endDate) {
      throw new Error('Start date must be before end date');
    }
  }

  contains(date: Date): boolean {
    return date >= this.startDate && date <= this.endDate;
  }

  overlaps(other: DateRange): boolean {
    return (
      this.contains(other.startDate) ||
      this.contains(other.endDate) ||
      other.contains(this.startDate) ||
      other.contains(this.endDate)
    );
  }

  getDurationInDays(): number {
    const diffTime = Math.abs(this.endDate.getTime() - this.startDate.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  }

  equals(other: DateRange): boolean {
    return (
      this.startDate.getTime() === other.startDate.getTime() &&
      this.endDate.getTime() === other.endDate.getTime()
    );
  }
}


