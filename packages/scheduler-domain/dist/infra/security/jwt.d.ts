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
export declare class JWTAuthenticator {
    private options;
    private jwks;
    constructor(options: JWTOptions);
    initialize(): Promise<void>;
    authenticate(token: string): Promise<AuthenticatedUser>;
    private extractUserFromPayload;
    private extractRoles;
    private extractPermissions;
    hasRole(user: AuthenticatedUser, requiredRole: string): boolean;
    hasPermission(user: AuthenticatedUser, requiredPermission: string): boolean;
    hasAnyRole(user: AuthenticatedUser, requiredRoles: string[]): boolean;
    hasAnyPermission(user: AuthenticatedUser, requiredPermissions: string[]): boolean;
}
export declare function getJWTAuthenticator(): JWTAuthenticator;
export declare function initializeJWTAuthenticator(): Promise<void>;
//# sourceMappingURL=jwt.d.ts.map