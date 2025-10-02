import { jwtVerify, createRemoteJWKSet, JWTPayload } from 'jose';

export interface JWTOptions {
  jwksUrl: string;
  issuer?: string;
  audience?: string;
}

export interface AuthenticatedUser {
  sub: string;
  email?: string;
  roles?: string[];
  permissions?: string[];
  tenantId?: string;
  [key: string]: any;
}

export class JWTService {
  private jwks: ReturnType<typeof createRemoteJWKSet>;

  constructor(private options: JWTOptions) {
    this.jwks = createRemoteJWKSet(new URL(options.jwksUrl));
  }

  async verifyToken(token: string): Promise<AuthenticatedUser> {
    try {
      const { payload } = await jwtVerify(token, this.jwks, {
        issuer: this.options.issuer,
        audience: this.options.audience,
      });

      return this.mapPayloadToUser(payload);
    } catch (error) {
      throw new Error(`Token verification failed: ${error}`);
    }
  }

  private mapPayloadToUser(payload: JWTPayload): AuthenticatedUser {
    return {
      sub: payload.sub as string,
      email: payload.email as string,
      roles: payload.roles as string[] || [],
      permissions: payload.permissions as string[] || [],
      tenantId: payload.tenantId as string,
      ...payload,
    };
  }

  async getUserFromRequest(authHeader: string): Promise<AuthenticatedUser | null> {
    if (!authHeader.startsWith('Bearer ')) {
      return null;
    }

    const token = authHeader.substring(7);
    return this.verifyToken(token);
  }
}

export function createJWTService(options: JWTOptions): JWTService {
  return new JWTService(options);
}

// Global instance
let globalJWTService: JWTService | null = null;

export function getJWTService(): JWTService {
  if (!globalJWTService) {
    const jwksUrl = process.env.JWKS_URL || 'https://auth.example.com/.well-known/jwks.json';
    globalJWTService = createJWTService({ jwksUrl });
  }
  return globalJWTService;
}

// Helper function for backward compatibility
export async function verifyJWT(token: string): Promise<AuthenticatedUser> {
  return getJWTService().verifyToken(token);
}