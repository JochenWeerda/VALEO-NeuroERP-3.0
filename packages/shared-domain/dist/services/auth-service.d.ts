/**
 * VALEO NeuroERP 3.0 - Authentication Service
 */
export interface User {
    id: string;
    email: string;
    password: string;
    role: string;
    tenantId: string;
}
export interface AuthResult {
    user: Omit<User, 'password'>;
    token: string;
}
export declare class AuthService {
    private readonly JWT_SECRET;
    private readonly SALT_ROUNDS;
    authenticate(email: string, password: string): Promise<AuthResult | null>;
    hashPassword(password: string): Promise<string>;
    verifyToken(token: string): Promise<any>;
}
//# sourceMappingURL=auth-service.d.ts.map