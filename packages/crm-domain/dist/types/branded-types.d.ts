/**
 * Branded type helpers for CRM Domain
 */
export type Brand<TValue, TBrand extends string> = TValue & {
    readonly __brand: TBrand;
};
export type CustomerId = Brand<string, 'CustomerId'>;
export type Email = Brand<string, 'Email'>;
export type PhoneNumber = Brand<string, 'PhoneNumber'>;
/**
 * Utility used by repositories/services to generate strongly typed identifiers.
 */
export declare function createId<TBrand extends string>(brand: TBrand): Brand<string, TBrand>;
//# sourceMappingURL=branded-types.d.ts.map