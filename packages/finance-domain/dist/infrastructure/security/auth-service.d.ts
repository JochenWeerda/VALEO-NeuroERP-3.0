export interface User {
    id: string;
    email: string;
    roles: string[];
    permissions: string[];
    tenantId: string;
    isActive: boolean;
    lastLogin?: Date;
    mfaEnabled: boolean;
}
export interface AuthToken {
    accessToken: string;
    refreshToken: string;
    expiresIn: number;
    tokenType: string;
}
export interface LoginCredentials {
    email: string;
    password: string;
    mfaCode?: string;
}
export interface Permission {
    resource: string;
    action: string;
    conditions?: Record<string, any>;
}
export declare enum UserRole {
    ADMIN = "admin",
    ACCOUNTANT = "accountant",
    AUDITOR = "auditor",
    MANAGER = "manager",
    VIEWER = "viewer"
}
export declare enum PermissionAction {
    CREATE = "create",
    READ = "read",
    UPDATE = "update",
    DELETE = "delete",
    APPROVE = "approve",
    EXPORT = "export"
}
export declare class AuthService {
    private readonly jwtSecret;
    private readonly jwtRefreshSecret;
    private readonly bcryptRounds;
    private readonly metrics;
    private readonly users;
    private readonly refreshTokens;
    constructor();
    private initializeDefaultUsers;
    private getPermissionsForRoles;
    authenticate(credentials: LoginCredentials): Promise<AuthToken>;
    refreshToken(refreshToken: string): Promise<AuthToken>;
    logout(refreshToken: string): Promise<void>;
    verifyAccessToken(token: string): User | null;
    hasPermission(user: User, resource: string, action: string): boolean;
    hasRole(user: User, role: string): boolean;
    private generateAccessToken;
    private generateRefreshToken;
    private verifyMFACode;
    createUser(userData: Omit<User, 'id' | 'permissions'>): Promise<User>;
    getUserById(id: string): User | null;
    getUserByEmail(email: string): User | null;
    updateUser(id: string, updates: Partial<User>): Promise<User | null>;
    deleteUser(id: string): Promise<boolean>;
}
export default AuthService;
//# sourceMappingURL=auth-service.d.ts.map