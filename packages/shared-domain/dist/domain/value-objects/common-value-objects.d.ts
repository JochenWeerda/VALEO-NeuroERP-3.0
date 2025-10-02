/**
 * Common Value Objects for VALEO NeuroERP 3.0
 * Reusable value objects across all domains
 */
export declare class Email {
    private readonly value;
    constructor(email: string);
    getValue(): string;
    equals(other: Email): boolean;
    toString(): string;
}
export declare class PhoneNumber {
    private readonly value;
    constructor(phone: string);
    getValue(): string;
    equals(other: PhoneNumber): boolean;
    toString(): string;
}
export declare class Address {
    readonly street: string;
    readonly city: string;
    readonly postalCode: string;
    readonly country: string;
    readonly state?: string | undefined;
    constructor(street: string, city: string, postalCode: string, country: string, state?: string | undefined);
    private validate;
    getFullAddress(): string;
    equals(other: Address): boolean;
}
export declare class Money {
    readonly amount: number;
    readonly currency: string;
    constructor(amount: number, currency?: string);
    private validate;
    add(other: Money): Money;
    subtract(other: Money): Money;
    multiply(factor: number): Money;
    divide(divisor: number): Money;
    private validateSameCurrency;
    equals(other: Money): boolean;
    toString(): string;
}
export declare class Percentage {
    private readonly value;
    constructor(value: number);
    getValue(): number;
    getDecimal(): number;
    equals(other: Percentage): boolean;
    toString(): string;
}
export declare class DateRange {
    readonly startDate: Date;
    readonly endDate: Date;
    constructor(startDate: Date, endDate: Date);
    private validate;
    contains(date: Date): boolean;
    overlaps(other: DateRange): boolean;
    getDurationInDays(): number;
    equals(other: DateRange): boolean;
}
//# sourceMappingURL=common-value-objects.d.ts.map