import { z } from 'zod';
export declare const JWTPayload: z.ZodObject<{
    sub: z.ZodString;
    tenantId: z.ZodString;
    email: z.ZodString;
    roles: z.ZodArray<z.ZodString, "many">;
    permissions: z.ZodArray<z.ZodString, "many">;
    iat: z.ZodNumber;
    exp: z.ZodNumber;
    iss: z.ZodString;
    aud: z.ZodString;
}, "strip", z.ZodTypeAny, {
    sub: string;
    tenantId: string;
    email: string;
    roles: string[];
    permissions: string[];
    iat: number;
    exp: number;
    iss: string;
    aud: string;
}, {
    sub: string;
    tenantId: string;
    email: string;
    roles: string[];
    permissions: string[];
    iat: number;
    exp: number;
    iss: string;
    aud: string;
}>;
export type JWTPayload = z.infer<typeof JWTPayload>;
export declare const UserContext: z.ZodObject<{
    userId: z.ZodString;
    tenantId: z.ZodString;
    email: z.ZodString;
    roles: z.ZodArray<z.ZodString, "many">;
    permissions: z.ZodArray<z.ZodString, "many">;
    token: z.ZodString;
    expiresAt: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    email: string;
    roles: string[];
    permissions: string[];
    userId: string;
    token: string;
    expiresAt: number;
}, {
    tenantId: string;
    email: string;
    roles: string[];
    permissions: string[];
    userId: string;
    token: string;
    expiresAt: number;
}>;
export type UserContext = z.infer<typeof UserContext>;
export declare const Role: z.ZodObject<{
    id: z.ZodString;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    permissions: z.ZodArray<z.ZodString, "many">;
    isActive: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    permissions: string[];
    id: string;
    name: string;
    isActive: boolean;
    description?: string | undefined;
}, {
    permissions: string[];
    id: string;
    name: string;
    description?: string | undefined;
    isActive?: boolean | undefined;
}>;
export type Role = z.infer<typeof Role>;
export declare const Permission: z.ZodObject<{
    resource: z.ZodString;
    action: z.ZodEnum<["create", "read", "update", "delete", "manage"]>;
    scope: z.ZodOptional<z.ZodString>;
    conditions: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
}, "strip", z.ZodTypeAny, {
    resource: string;
    action: "create" | "read" | "update" | "delete" | "manage";
    scope?: string | undefined;
    conditions?: Record<string, any> | undefined;
}, {
    resource: string;
    action: "create" | "read" | "update" | "delete" | "manage";
    scope?: string | undefined;
    conditions?: Record<string, any> | undefined;
}>;
export type Permission = z.infer<typeof Permission>;
export declare const PolicyResult: z.ZodObject<{
    allowed: z.ZodBoolean;
    reason: z.ZodOptional<z.ZodString>;
    conditions: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
}, "strip", z.ZodTypeAny, {
    allowed: boolean;
    conditions?: Record<string, any> | undefined;
    reason?: string | undefined;
}, {
    allowed: boolean;
    conditions?: Record<string, any> | undefined;
    reason?: string | undefined;
}>;
export type PolicyResult = z.infer<typeof PolicyResult>;
export declare const AuthErrorType: z.ZodEnum<["INVALID_TOKEN", "EXPIRED_TOKEN", "INSUFFICIENT_PERMISSIONS", "TENANT_MISMATCH", "USER_NOT_FOUND", "ROLE_NOT_FOUND"]>;
export type AuthErrorType = z.infer<typeof AuthErrorType>;
export declare const JWKS: z.ZodObject<{
    keys: z.ZodArray<z.ZodObject<{
        kty: z.ZodString;
        use: z.ZodString;
        kid: z.ZodString;
        n: z.ZodString;
        e: z.ZodString;
        alg: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        kty: string;
        use: string;
        kid: string;
        n: string;
        e: string;
        alg: string;
    }, {
        kty: string;
        use: string;
        kid: string;
        n: string;
        e: string;
        alg: string;
    }>, "many">;
}, "strip", z.ZodTypeAny, {
    keys: {
        kty: string;
        use: string;
        kid: string;
        n: string;
        e: string;
        alg: string;
    }[];
}, {
    keys: {
        kty: string;
        use: string;
        kid: string;
        n: string;
        e: string;
        alg: string;
    }[];
}>;
export type JWKS = z.infer<typeof JWKS>;
export declare const AuthMiddlewareOptions: z.ZodObject<{
    requireAuth: z.ZodDefault<z.ZodBoolean>;
    requireRoles: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    requirePermissions: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    requireTenant: z.ZodDefault<z.ZodBoolean>;
    tokenHeader: z.ZodDefault<z.ZodString>;
    tenantHeader: z.ZodDefault<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    requireAuth: boolean;
    requireTenant: boolean;
    tokenHeader: string;
    tenantHeader: string;
    requireRoles?: string[] | undefined;
    requirePermissions?: string[] | undefined;
}, {
    requireAuth?: boolean | undefined;
    requireRoles?: string[] | undefined;
    requirePermissions?: string[] | undefined;
    requireTenant?: boolean | undefined;
    tokenHeader?: string | undefined;
    tenantHeader?: string | undefined;
}>;
export type AuthMiddlewareOptions = z.infer<typeof AuthMiddlewareOptions>;
//# sourceMappingURL=auth-types.d.ts.map