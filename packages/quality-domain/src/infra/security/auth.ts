import { FastifyRequest } from 'fastify';
import { jwtVerify, createRemoteJWKSet, JWTPayload } from 'jose';

const JWKS_URI = process.env.JWKS_URI ?? '';
const JWT_ISSUER = process.env.JWT_ISSUER ?? '';
const JWT_AUDIENCE = process.env.JWT_AUDIENCE ?? 'valeo-neuroerp';

let jwks: ReturnType<typeof createRemoteJWKSet> | null = null;

if (JWKS_URI) {
  jwks = createRemoteJWKSet(new URL(JWKS_URI));
}

export interface AuthContext {
  userId: string;
  tenantId: string;
  roles: string[];
  permissions: string[];
}

/**
 * Verify JWT token
 */
export async function verifyToken(token: string): Promise<JWTPayload> {
  if (jwks === undefined || jwks === null) {
    throw new Error('JWKS not configured');
  }

  const { payload } = await jwtVerify(token, jwks, {
    issuer: JWT_ISSUER,
    audience: JWT_AUDIENCE,
  });

  return payload;
}

/**
 * Extract auth context from request
 */
export async function extractAuthContext(request: FastifyRequest): Promise<AuthContext> {
  const authHeader = request.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    throw new Error('Missing or invalid authorization header');
  }

  const token = authHeader.substring(7);
  const payload = await verifyToken(token);

  const tenantId = request.headers['x-tenant-id'] as string;
  if (tenantId === undefined || tenantId === null) {
    throw new Error('Missing x-tenant-id header');
  }

  return {
    userId: payload.sub as string,
    tenantId,
    roles: (payload.roles as string[]) || [],
    permissions: (payload.permissions as string[]) || [],
  };
}

/**
 * Check if user has required permission
 */
export function hasPermission(context: AuthContext, requiredPermission: string): boolean {
  return context.permissions.includes(requiredPermission) || context.roles.includes('admin');
}

/**
 * Check if user has any of the required permissions
 */
export function hasAnyPermission(context: AuthContext, requiredPermissions: string[]): boolean {
  if (context.roles.includes('admin')) {
    return true;
  }
  
  return requiredPermissions.some(perm => context.permissions.includes(perm));
}

