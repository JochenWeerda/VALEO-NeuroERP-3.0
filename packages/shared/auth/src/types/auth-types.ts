import { z } from 'zod';

// Authentication and Authorization Types

// JWT Payload structure
export const JWTPayload = z.object({
  sub: z.string(), // Subject (user ID)
  tenantId: z.string(),
  email: z.string().email(),
  roles: z.array(z.string()),
  permissions: z.array(z.string()),
  iat: z.number(), // Issued at
  exp: z.number(), // Expires at
  iss: z.string(), // Issuer
  aud: z.string()  // Audience
});

export type JWTPayload = z.infer<typeof JWTPayload>;

// User context for authenticated requests
export const UserContext = z.object({
  userId: z.string(),
  tenantId: z.string(),
  email: z.string().email(),
  roles: z.array(z.string()),
  permissions: z.array(z.string()),
  token: z.string(),
  expiresAt: z.number()
});

export type UserContext = z.infer<typeof UserContext>;

// Role definition
export const Role = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string().optional(),
  permissions: z.array(z.string()),
  isActive: z.boolean().default(true)
});

export type Role = z.infer<typeof Role>;

// Permission structure
export const Permission = z.object({
  resource: z.string(), // e.g., "shipment", "order", "customer"
  action: z.enum(['create', 'read', 'update', 'delete', 'manage']),
  scope: z.string().optional(), // e.g., "own", "tenant", "all"
  conditions: z.record(z.any()).optional() // Additional conditions
});

export type Permission = z.infer<typeof Permission>;

// Policy evaluation result
export const PolicyResult = z.object({
  allowed: z.boolean(),
  reason: z.string().optional(),
  conditions: z.record(z.any()).optional()
});

export type PolicyResult = z.infer<typeof PolicyResult>;

// Authentication error types
export const AuthErrorType = z.enum([
  'INVALID_TOKEN',
  'EXPIRED_TOKEN',
  'INSUFFICIENT_PERMISSIONS',
  'TENANT_MISMATCH',
  'USER_NOT_FOUND',
  'ROLE_NOT_FOUND'
]);

export type AuthErrorType = z.infer<typeof AuthErrorType>;

// JWKS (JSON Web Key Set) structure
export const JWKS = z.object({
  keys: z.array(z.object({
    kty: z.string(),
    use: z.string(),
    kid: z.string(),
    n: z.string(),
    e: z.string(),
    alg: z.string()
  }))
});

export type JWKS = z.infer<typeof JWKS>;

// Authentication middleware options
export const AuthMiddlewareOptions = z.object({
  requireAuth: z.boolean().default(true),
  requireRoles: z.array(z.string()).optional(),
  requirePermissions: z.array(z.string()).optional(),
  requireTenant: z.boolean().default(true),
  tokenHeader: z.string().default('authorization'),
  tenantHeader: z.string().default('x-tenant-id')
});

export type AuthMiddlewareOptions = z.infer<typeof AuthMiddlewareOptions>;