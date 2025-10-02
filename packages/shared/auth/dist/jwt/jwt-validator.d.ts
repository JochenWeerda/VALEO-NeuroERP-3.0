import { JWTPayload, UserContext } from '../types/auth-types';
export interface JWTValidationOptions {
    jwksUrl?: string;
    issuer: string;
    audience: string;
    algorithms?: string[];
}
export declare class JWTValidator {
    private jwksUrl?;
    private issuer;
    private audience;
    private algorithms;
    private jwksCache;
    private cacheExpiry;
    constructor(options: JWTValidationOptions);
    /**
     * Validate JWT token and return user context
     */
    validateToken(token: string): Promise<UserContext>;
    /**
     * Verify token using JWKS (production)
     */
    private verifyWithJWKS;
    /**
     * Verify token using local secret (development)
     */
    private verifyWithSecret;
    /**
     * Fetch JWKS with caching
     */
    private fetchJWKS;
    /**
     * Generate JWT token (for testing/development)
     */
    generateToken(payload: Omit<JWTPayload, 'iat' | 'exp' | 'iss' | 'aud'>): string;
    /**
     * Refresh JWKS cache
     */
    refreshJWKS(): Promise<void>;
}
//# sourceMappingURL=jwt-validator.d.ts.map