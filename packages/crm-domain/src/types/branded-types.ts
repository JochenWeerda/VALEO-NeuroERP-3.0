/**
 * Branded type helpers for CRM Domain
 */

export type Brand<TValue, TBrand extends string> = TValue & { readonly __brand: TBrand };

// Domain specific identifiers
export type CustomerId = Brand<string, 'CustomerId'>;
export type Email = Brand<string, 'Email'>;
export type PhoneNumber = Brand<string, 'PhoneNumber'>;

/**
 * Utility used by repositories/services to generate strongly typed identifiers.
 */
export function createId<TBrand extends string>(brand: TBrand): Brand<string, TBrand> {
  const value = typeof globalThis.crypto?.randomUUID === 'function'
    ? globalThis.crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return value as Brand<string, TBrand>;
}
