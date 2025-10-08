import { jwtVerify, createRemoteJWKSet, JWTPayload } from 'jose';

interface JWKSConfig {
  jwksUrl: string;
  issuer?: string;
  audience?: string;
}

class JWKSManager {
  private jwksClient: ReturnType<typeof createRemoteJWKSet> | null = null;
  private config: JWKSConfig;

  constructor(config: JWKSConfig) {
    this.config = config;
  }

  private getJWKSClient() {
    if (this.jwksClient === undefined || this.jwksClient === null) {
      this.jwksClient = createRemoteJWKSet(new URL(this.config.jwksUrl));
    }
    return this.jwksClient;
  }

  async verifyToken(token: string): Promise<JWTPayload> {
    const client = this.getJWKSClient();

    const options: any = {};
    if (this.config.issuer) options.issuer = this.config.issuer;
    if (this.config.audience) options.audience = this.config.audience;

    const { payload } = await jwtVerify(token, client, options);

    return payload;
  }
}

// Global JWKS manager instance
let jwksManager: JWKSManager | null = null;

function getJWKSManager(): JWKSManager {
  if (jwksManager === undefined || jwksManager === null) {
    const jwksUrl = process.env.JWKS_URL ?? 'https://auth.example.com/.well-known/jwks.json';
    const issuer = process.env.JWT_ISSUER;
    const audience = process.env.JWT_AUDIENCE;

    const config: JWKSConfig = { jwksUrl };
    if (issuer) config.issuer = issuer;
    if (audience) config.audience = audience;

    jwksManager = new JWKSManager(config);
  }
  return jwksManager;
}

export async function verifyJWT(token: string): Promise<JWTPayload> {
  const manager = getJWKSManager();
  return manager.verifyToken(token);
}

export function createJWT(payload: JWTPayload, expiresIn: string = '1h'): string {
  // Note: This is a simplified implementation
  // In production, you would use a proper JWT library to sign tokens
  // For now, we'll just return a mock token for development
  return `mock.jwt.token.${Date.now()}`;
}

