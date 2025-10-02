/**
 * Common Value Objects for VALEO NeuroERP 3.0
 * Reusable value objects across all domains
 */
import { z } from 'zod';
// Email Value Object
export class Email {
    value;
    constructor(email) {
        const emailSchema = z.string().email();
        const validatedEmail = emailSchema.parse(email);
        this.value = validatedEmail.toLowerCase();
    }
    getValue() {
        return this.value;
    }
    equals(other) {
        return this.value === other.value;
    }
    toString() {
        return this.value;
    }
}
// Phone Number Value Object
export class PhoneNumber {
    value;
    constructor(phone) {
        // Basic phone validation - can be enhanced based on requirements
        const phoneSchema = z.string().min(10).max(15).regex(/^[\+]?[0-9\s\-\(\)]+$/);
        this.value = phoneSchema.parse(phone);
    }
    getValue() {
        return this.value;
    }
    equals(other) {
        return this.value === other.value;
    }
    toString() {
        return this.value;
    }
}
// Address Value Object
export class Address {
    street;
    city;
    postalCode;
    country;
    state;
    constructor(street, city, postalCode, country, state) {
        this.street = street;
        this.city = city;
        this.postalCode = postalCode;
        this.country = country;
        this.state = state;
        this.validate();
    }
    validate() {
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
    getFullAddress() {
        const parts = [this.street, this.city, this.postalCode];
        if (this.state) {
            parts.push(this.state);
        }
        parts.push(this.country);
        return parts.join(', ');
    }
    equals(other) {
        return (this.street === other.street &&
            this.city === other.city &&
            this.postalCode === other.postalCode &&
            this.country === other.country &&
            this.state === other.state);
    }
}
// Money Value Object
export class Money {
    amount;
    currency;
    constructor(amount, currency = 'EUR') {
        this.amount = amount;
        this.currency = currency;
        this.validate();
    }
    validate() {
        const moneySchema = z.object({
            amount: z.number().finite().min(0),
            currency: z.string().length(3).toUpperCase()
        });
        moneySchema.parse({
            amount: this.amount,
            currency: this.currency
        });
    }
    add(other) {
        this.validateSameCurrency(other);
        return new Money(this.amount + other.amount, this.currency);
    }
    subtract(other) {
        this.validateSameCurrency(other);
        return new Money(this.amount - other.amount, this.currency);
    }
    multiply(factor) {
        return new Money(this.amount * factor, this.currency);
    }
    divide(divisor) {
        if (divisor === 0) {
            throw new Error('Division by zero is not allowed');
        }
        return new Money(this.amount / divisor, this.currency);
    }
    validateSameCurrency(other) {
        if (this.currency !== other.currency) {
            throw new Error(`Currency mismatch: ${this.currency} vs ${other.currency}`);
        }
    }
    equals(other) {
        return this.amount === other.amount && this.currency === other.currency;
    }
    toString() {
        return `${this.amount.toFixed(2)} ${this.currency}`;
    }
}
// Percentage Value Object
export class Percentage {
    value;
    constructor(value) {
        const percentageSchema = z.number().min(0).max(100);
        this.value = percentageSchema.parse(value);
    }
    getValue() {
        return this.value;
    }
    getDecimal() {
        return this.value / 100;
    }
    equals(other) {
        return this.value === other.value;
    }
    toString() {
        return `${this.value}%`;
    }
}
// Date Range Value Object
export class DateRange {
    startDate;
    endDate;
    constructor(startDate, endDate) {
        this.startDate = startDate;
        this.endDate = endDate;
        this.validate();
    }
    validate() {
        if (this.startDate >= this.endDate) {
            throw new Error('Start date must be before end date');
        }
    }
    contains(date) {
        return date >= this.startDate && date <= this.endDate;
    }
    overlaps(other) {
        return (this.contains(other.startDate) ||
            this.contains(other.endDate) ||
            other.contains(this.startDate) ||
            other.contains(this.endDate));
    }
    getDurationInDays() {
        const diffTime = Math.abs(this.endDate.getTime() - this.startDate.getTime());
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }
    equals(other) {
        return (this.startDate.getTime() === other.startDate.getTime() &&
            this.endDate.getTime() === other.endDate.getTime());
    }
}
//# sourceMappingURL=common-value-objects.js.map