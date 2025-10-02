import jwt from 'jsonwebtoken';
import jwkToPem from 'jwk-to-pem';
import axios from 'axios';
import { JWTPayload, JWKS, UserContext } from '../types/auth-types';

export interface JWTValidationOptions {
  jwksUrl?: string;
  issuer: string;
  audience: string;
  algorithms?: string[];
}

export class JWTValidator {
  private jwksUrl?: string;
  private issuer: string;
  private audience: string;
  private algorithms: string[];
  private jwksCache: Map<string, any> = new Map();
  private cacheExpiry: Map<string, number> = new Map();

  constructor(options: JWTValidationOptions) {
    this.jwksUrl = options.jwksUrl;
    this.issuer = options.issuer;
    this.audience = options.audience;
    this.algorithms = options.algorithms || ['RS256'];
  }

  /**
   * Validate JWT token and return user context
   */
  async validateToken(token: string): Promise<UserContext> {
    try {
      // Decode token without verification first
      const decoded = jwt.decode(token) as any;
      if (!decoded) {
        throw new Error('Invalid token format');
      }

      // Verify token with JWKS if URL provided
      if (this.jwksUrl) {
        await this.verifyWithJWKS(token, decoded);
      } else {
        // Verify with local secret (for development/testing)
        await this.verifyWithSecret(token);
      }

      // Validate payload structure
      const payload = JWTPayload.parse(decoded);

      // Check expiration
      if (payload.exp * 1000 < Date.now()) {
        throw new Error('Token expired');
      }

      // Check issuer and audience
      if (payload.iss !== this.issuer) {
        throw new Error('Invalid token issuer');
      }

      if (payload.aud !== this.audience) {
        throw new Error('Invalid token audience');
      }

      return {
        userId: payload.sub,
        tenantId: payload.tenantId,
        email: payload.email,
        roles: payload.roles,
        permissions: payload.permissions,
        token,
        expiresAt: payload.exp * 1000
      };

    } catch (error) {
      throw new Error(`JWT validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Verify token using JWKS (production)
   */
  private async verifyWithJWKS(token: string, decoded: any): Promise<void> {
    const kid = decoded.header?.kid;
    if (!kid) {
      throw new Error('Token missing key ID (kid)');
    }

    // Get JWKS
    const jwks = await this.fetchJWKS();

    // Find the key
    const key = jwks.keys.find(k => k.kid === kid);
    if (!key) {
      throw new Error('Signing key not found in JWKS');
    }

    // Convert JWK to PEM
    const pem = jwkToPem(key as any);

    // Verify token
    jwt.verify(token, pem, {
      issuer: this.issuer,
      audience: this.audience,
      algorithms: this.algorithms as any[]
    });
  }

  /**
   * Verify token using local secret (development)
   */
  private async verifyWithSecret(token: string): Promise<void> {
    const secret = process.env.JWT_SECRET;
    if (!secret) {
      throw new Error('JWT_SECRET not configured');
    }

    jwt.verify(token, secret, {
      issuer: this.issuer,
      audience: this.audience,
      algorithms: this.algorithms as any[]
    });
  }

  /**
   * Fetch JWKS with caching
   */
  private async fetchJWKS(): Promise<JWKS> {
    if (this.jwksCache.size > 0) {
      // Return cached JWKS if still valid
      const cacheKey = this.jwksUrl!;
      const expiry = this.cacheExpiry.get(cacheKey);
      if (expiry && expiry > Date.now()) {
        return this.jwksCache.get(cacheKey);
      }
    }

    try {
      const response = await axios.get(this.jwksUrl!);
      const jwks = JWKS.parse(response.data);

      // Cache JWKS for 1 hour
      this.jwksCache.set(this.jwksUrl!, jwks);
      this.cacheExpiry.set(this.jwksUrl!, Date.now() + 60 * 60 * 1000);

      return jwks;
    } catch (error) {
      throw new Error(`Failed to fetch JWKS: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Generate JWT token (for testing/development)
   */
  generateToken(payload: Omit<JWTPayload, 'iat' | 'exp' | 'iss' | 'aud'>): string {
    const secret = process.env.JWT_SECRET;
    if (!secret) {
      throw new Error('JWT_SECRET not configured');
    }

    const fullPayload: JWTPayload = {
      ...payload,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60), // 24 hours
      iss: this.issuer,
      aud: this.audience
    };

    return jwt.sign(fullPayload, secret, {
      algorithm: 'HS256'
    });
  }

  /**
   * Refresh JWKS cache
   */
  async refreshJWKS(): Promise<void> {
    if (this.jwksUrl) {
      this.jwksCache.delete(this.jwksUrl);
      this.cacheExpiry.delete(this.jwksUrl);
      await this.fetchJWKS();
    }
  }
}