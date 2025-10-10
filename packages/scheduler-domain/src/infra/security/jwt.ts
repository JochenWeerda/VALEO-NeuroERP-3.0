import { JWTPayload, createRemoteJWKSet, jwtVerify } from 'jose';

export interface JWTOptions {
  jwksUrl: string;
  issuer?: string;
  audience?: string;
}

export interface AuthenticatedUser {
  sub: string;
  email?: string;
  name?: string;
  roles?: string[];
  tenantId?: string;
  permissions?: string[];
}

export interface AuthContext {
  user: AuthenticatedUser;
  token: string;
  tenantId: string;
}

export class JWTAuthenticator {
  private jwks: ReturnType<typeof createRemoteJWKSet> | null = null;

  constructor(private readonly options: JWTOptions) {}

  async initialize(): Promise<void> {
    this.jwks = createRemoteJWKSet(new URL(this.options.jwksUrl));
  }

  async authenticate(token: string): Promise<AuthenticatedUser> {
    if (!this.jwks) {
      throw new Error('JWT authenticator not initialized');
    }

    try {
      const { payload } = await jwtVerify(token, this.jwks, {
        issuer: this.options.issuer,
        audience: this.options.audience,
      });

      return this.extractUserFromPayload(payload);
    } catch (error) {
      throw new Error(`JWT verification failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private extractUserFromPayload(payload: JWTPayload): AuthenticatedUser {
    const sub = payload.sub;
    if (!sub) {
      throw new Error('JWT missing subject claim');
    }

    return {
      sub,
      email: payload.email as string,
      name: payload.name as string,
      roles: this.extractRoles(payload),
      tenantId: payload.tenant_id as string || payload['x-tenant-id'] as string,
      permissions: this.extractPermissions(payload),
    };
  }

  private extractRoles(payload: JWTPayload): string[] {
    const roles = payload.roles || payload['cognito:groups'] || payload.groups || [];
    if (Array.isArray(roles)) {
      return roles.filter((role): role is string => typeof role === 'string');
    }
    if (typeof roles === 'string') {
      return [roles];
    }
    return [];
  }

  private extractPermissions(payload: JWTPayload): string[] {
    const permissions = payload.permissions;
    if (Array.isArray(permissions)) {
      return permissions.filter((perm): perm is string => typeof perm === 'string');
    }

    const scope = payload.scope;
    if (typeof scope === 'string') {
      return scope.split(' ').filter(Boolean);
    }

    return [];
  }

  hasRole(user: AuthenticatedUser, requiredRole: string): boolean {
    return user.roles?.includes(requiredRole) ?? false;
  }

  hasPermission(user: AuthenticatedUser, requiredPermission: string): boolean {
    return user.permissions?.includes(requiredPermission) ?? false;
  }

  hasAnyRole(user: AuthenticatedUser, requiredRoles: string[]): boolean {
    return requiredRoles.some(role => this.hasRole(user, role));
  }

  hasAnyPermission(user: AuthenticatedUser, requiredPermissions: string[]): boolean {
    return requiredPermissions.some(permission => this.hasPermission(user, permission));
  }
}

// Global authenticator instance
let globalAuthenticator: JWTAuthenticator | null = null;

export function getJWTAuthenticator(): JWTAuthenticator {
  if (!globalAuthenticator) {
    const jwksUrl = process.env.JWKS_URL || 'https://auth.example.com/.well-known/jwks.json';
    globalAuthenticator = new JWTAuthenticator({
      jwksUrl,
      issuer: process.env.JWT_ISSUER,
      audience: process.env.JWT_AUDIENCE,
    });
  }
  return globalAuthenticator;
}

export async function initializeJWTAuthenticator(): Promise<void> {
  const authenticator = getJWTAuthenticator();
  await authenticator.initialize();
}