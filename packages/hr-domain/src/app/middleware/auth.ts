/**
 * Authentication Middleware for VALEO NeuroERP 3.0 HR Domain
 * JWT validation with JWKS
 */

import { FastifyReply, FastifyRequest } from 'fastify';
import { type JWTPayload as JoseJWTPayload, createRemoteJWKSet, jwtVerify } from 'jose';
import pino from 'pino';

interface AuthenticatedJWTPayload extends JoseJWTPayload {
  sub: string;
  iss: string;
  aud: string | string[];
  exp: number;
  iat: number;
  roles?: string[];
  permissions?: string[];
  tenantId?: string;
}

export interface AuthContext {
  userId: string;
  tenantId: string;
  roles: string[];
  permissions: string[];
  token: string;
}

declare module 'fastify' {
  interface FastifyRequest {
    auth?: AuthContext;
  }
}

const DEFAULT_JWKS_URL = 'https://auth.example.com/.well-known/jwks.json';
const DEFAULT_JWT_ISSUER = 'https://auth.example.com';
const DEFAULT_JWT_AUDIENCE = 'hr-domain';
const BEARER_PREFIX = 'Bearer ';
const MILLISECONDS_PER_SECOND = 1000;

const HTTP_STATUS = {
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403
} as const;

const logger = pino({ name: 'auth-middleware' });

const JWKS_URL = process.env.JWKS_URL ?? DEFAULT_JWKS_URL;
const JWT_ISSUER = process.env.JWT_ISSUER ?? DEFAULT_JWT_ISSUER;
const JWT_AUDIENCE = process.env.JWT_AUDIENCE ?? DEFAULT_JWT_AUDIENCE;

let jwks: ReturnType<typeof createRemoteJWKSet> | null = null;

export async function initializeAuth(): Promise<void> {
  try {
    jwks = createRemoteJWKSet(new URL(JWKS_URL));
    logger.info({ jwksUrl: JWKS_URL }, 'Auth middleware initialized');
  } catch (error) {
    logger.error({ err: error }, 'Failed to initialize auth middleware');
    throw error;
  }
}

async function ensureJwks(): Promise<ReturnType<typeof createRemoteJWKSet>> {
  if (!jwks) {
    await initializeAuth();
  }
  return jwks ?? createRemoteJWKSet(new URL(JWKS_URL));
}

function resolveTenantId(request: FastifyRequest, jwtPayload: AuthenticatedJWTPayload): string | undefined {
  if (typeof jwtPayload.tenantId === 'string' && jwtPayload.tenantId.length > 0) {
    return jwtPayload.tenantId;
  }

  const tenantHeader = request.headers['x-tenant-id'];
  if (Array.isArray(tenantHeader)) {
    return tenantHeader[0];
  }

  return typeof tenantHeader === 'string' ? tenantHeader : undefined;
}

export async function authMiddleware(request: FastifyRequest, reply: FastifyReply): Promise<void> {
  try {
    const authHeader = request.headers.authorization;

    if (authHeader?.startsWith(BEARER_PREFIX) !== true) {
      reply.code(HTTP_STATUS.UNAUTHORIZED).send({ error: 'Missing or invalid authorization header' });
      return;
    }

    const token = authHeader.slice(BEARER_PREFIX.length);

    const keySet = await ensureJwks();
    const { payload } = await jwtVerify(token, keySet, {
      issuer: JWT_ISSUER,
      audience: JWT_AUDIENCE,
      algorithms: ['RS256', 'RS384', 'RS512']
    });

    const jwtPayload = payload as AuthenticatedJWTPayload;

    if (typeof jwtPayload.exp === 'number') {
      const currentEpochSeconds = Math.floor(Date.now() / MILLISECONDS_PER_SECOND);
      if (jwtPayload.exp < currentEpochSeconds) {
        reply.code(HTTP_STATUS.UNAUTHORIZED).send({ error: 'Token expired' });
        return;
      }
    }

    const tenantId = resolveTenantId(request, jwtPayload);
    if (typeof tenantId !== 'string' || tenantId.length === 0) {
      reply.code(HTTP_STATUS.BAD_REQUEST).send({ error: 'Tenant ID required' });
      return;
    }

    request.auth = {
      userId: jwtPayload.sub,
      tenantId,
      roles: jwtPayload.roles ?? [],
      permissions: jwtPayload.permissions ?? [],
      token
    };
  } catch (error) {
    logger.error({ err: error }, 'Auth middleware error');
    reply.code(HTTP_STATUS.UNAUTHORIZED).send({ error: 'Invalid token' });
  }
}

export async function requireAuth(request: FastifyRequest, reply: FastifyReply): Promise<void> {
  if (!request.auth) {
    reply.code(HTTP_STATUS.UNAUTHORIZED).send({ error: 'Authentication required' });
  }
}

type FastifyAuthHandler = (request: FastifyRequest, reply: FastifyReply) => Promise<void>;

export function requireRole(roles: string[]): FastifyAuthHandler {
  return async (request: FastifyRequest, reply: FastifyReply): Promise<void> => {
    const { auth } = request;
    if (!auth) {
      reply.code(HTTP_STATUS.UNAUTHORIZED).send({ error: 'Authentication required' });
      return;
    }

    const hasRole = roles.some(role => auth.roles.includes(role));
    if (!hasRole) {
      reply.code(HTTP_STATUS.FORBIDDEN).send({ error: 'Insufficient permissions' });
    }
  };
}

export function requirePermission(permissions: string[]): FastifyAuthHandler {
  return async (request: FastifyRequest, reply: FastifyReply): Promise<void> => {
    const { auth } = request;
    if (!auth) {
      reply.code(HTTP_STATUS.UNAUTHORIZED).send({ error: 'Authentication required' });
      return;
    }

    const hasPermission = permissions.some(permission =>
      auth.permissions.includes(permission) || auth.permissions.includes('*')
    );

    if (!hasPermission) {
      reply.code(HTTP_STATUS.FORBIDDEN).send({ error: 'Insufficient permissions' });
    }
  };
}

export const hrPermissions = {
  EMPLOYEE_READ: 'hr:employee:read',
  EMPLOYEE_WRITE: 'hr:employee:write',
  EMPLOYEE_DELETE: 'hr:employee:delete',
  TIME_READ: 'hr:time:read',
  TIME_WRITE: 'hr:time:write',
  TIME_APPROVE: 'hr:time:approve',
  LEAVE_READ: 'hr:leave:read',
  LEAVE_WRITE: 'hr:leave:write',
  LEAVE_APPROVE: 'hr:leave:approve',
  SHIFT_READ: 'hr:shift:read',
  SHIFT_WRITE: 'hr:shift:write',
  PAYROLL_READ: 'hr:payroll:read',
  PAYROLL_WRITE: 'hr:payroll:write',
  PAYROLL_EXPORT: 'hr:payroll:export',
  ROLE_READ: 'hr:role:read',
  ROLE_WRITE: 'hr:role:write'
} as const;

export function requireHrPermission(permission: string): FastifyAuthHandler {
  return async (request: FastifyRequest, reply: FastifyReply): Promise<void> => {
    const { auth } = request;
    if (!auth) {
      reply.code(HTTP_STATUS.UNAUTHORIZED).send({ error: 'Authentication required' });
      return;
    }

    const hasPermission = auth.permissions.includes(permission) || auth.permissions.includes('*');
    if (!hasPermission) {
      reply.code(HTTP_STATUS.FORBIDDEN).send({ error: 'Insufficient permissions' });
    }
  };
}
