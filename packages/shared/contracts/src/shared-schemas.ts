import { z } from 'zod';

// Common schemas used across all domains

export const UUID = z.string().uuid();
export const Email = z.string().email();
export const PhoneNumber = z.string().regex(/^\+?[1-9]\d{1,14}$/);
export const URL = z.string().url();

// Address schema (used by multiple domains)
export const Address = z.object({
  street: z.string().min(1),
  city: z.string().min(1),
  postalCode: z.string().min(1),
  country: z.string().length(2), // ISO 3166-1 alpha-2
  coordinates: z.object({
    lat: z.number().min(-90).max(90),
    lon: z.number().min(-180).max(180)
  }).optional(),
  gln: z.string().optional(), // Global Location Number
  name: z.string().optional()
});

export type Address = z.infer<typeof Address>;

// Contact information (used by CRM, Procurement, etc.)
export const ContactInfo = z.object({
  name: z.string().min(1),
  email: Email.optional(),
  phone: PhoneNumber.optional(),
  address: Address.optional()
});

export type ContactInfo = z.infer<typeof ContactInfo>;

// Currency and Money
export const Currency = z.enum(['EUR', 'USD', 'GBP', 'CHF']);
export const Money = z.object({
  amount: z.number().nonnegative(),
  currency: Currency
});

export type Money = z.infer<typeof Money>;

// Time and Date
export const ISODateString = z.string().datetime();
export const TimeWindow = z.object({
  from: ISODateString,
  to: ISODateString
});

export type TimeWindow = z.infer<typeof TimeWindow>;

// Pagination
export const PaginationParams = z.object({
  page: z.number().int().positive().default(1),
  limit: z.number().int().min(1).max(100).default(20)
});

export type PaginationParams = z.infer<typeof PaginationParams>;

export const PaginatedResponse = <T extends z.ZodType>(itemSchema: T) => z.object({
  items: z.array(itemSchema),
  total: z.number().int().nonnegative(),
  page: z.number().int().positive(),
  limit: z.number().int().positive(),
  hasNext: z.boolean(),
  hasPrev: z.boolean()
});

export type PaginatedResponse<T> = {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
};

// Tenant context (for multi-tenancy)
export const TenantContext = z.object({
  tenantId: z.string().min(1),
  userId: z.string().optional(),
  roles: z.array(z.string()).default([])
});

export type TenantContext = z.infer<typeof TenantContext>;

// Generic response wrapper
export const ApiResponse = <T extends z.ZodType>(dataSchema: T) => z.object({
  success: z.boolean(),
  data: dataSchema.optional(),
  error: z.object({
    code: z.string(),
    message: z.string(),
    details: z.any().optional()
  }).optional(),
  timestamp: ISODateString,
  requestId: z.string().optional()
});

export type ApiResponse<T> = {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: string;
  requestId?: string;
};