export interface User {
    id: string;
    username: string;
    email: string;
    full_name: string;
    role: string;
    disabled: boolean;
}
export interface LoginRequest {
    username: string;
    password: string;
}
export interface AuthService {
    login(credentials: LoginRequest): Promise<{
        user: User;
        token: string;
    }>;
    logout(): Promise<void>;
    getCurrentUser(): Promise<User>;
    isAuthenticated(): boolean;
    refreshToken(): Promise<string>;
}
export declare class AuthServiceImpl implements AuthService {
    private currentUser;
    private token;
    login(credentials: LoginRequest): Promise<{
        user: User;
        token: string;
    }>;
    logout(): Promise<void>;
    getCurrentUser(): Promise<User>;
    isAuthenticated(): boolean;
    refreshToken(): Promise<string>;
}
//# sourceMappingURL=use-auth.d.ts.map