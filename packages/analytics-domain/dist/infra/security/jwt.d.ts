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
export declare class JWTService {
    private options;
    private jwks;
    constructor(options: JWTOptions);
    verifyToken(token: string): Promise<AuthenticatedUser>;
    private mapPayloadToUser;
    getUserFromRequest(authHeader: string): Promise<AuthenticatedUser | null>;
}
export declare function createJWTService(options: JWTOptions): JWTService;
export declare function getJWTService(): JWTService;
//# sourceMappingURL=jwt.d.ts.map