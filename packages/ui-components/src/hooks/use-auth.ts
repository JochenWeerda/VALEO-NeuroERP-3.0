// domains/shared/src/services/auth-service.ts
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
  login(credentials: LoginRequest): Promise<{ user: User; token: string }>;
  logout(): Promise<void>;
  getCurrentUser(): Promise<User>;
  isAuthenticated(): boolean;
  refreshToken(): Promise<string>;
}

export class AuthServiceImpl implements AuthService {
  private currentUser: User | null = null;
  private token: string | null = null;

  async login(credentials: LoginRequest): Promise<{ user: User; token: string }> {
    // Implementation
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });

    if (response.ok === undefined || response.ok === null) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    this.currentUser = data.user;
    this.token = data.token;
    
    return { user: data.user, token: data.token };
  }

  async logout(): Promise<void> {
    this.currentUser = null;
    this.token = null;
    // Clear token from storage (browser environment only)
    if (typeof globalThis !== 'undefined' && 'localStorage' in globalThis) {
      (globalThis as { localStorage: Storage }).localStorage.removeItem('auth_token');
    }
  }

  async getCurrentUser(): Promise<User> {
    if (this.currentUser === undefined || this.currentUser === null) {
      throw new Error('User not authenticated');
    }
    return this.currentUser;
  }

  isAuthenticated(): boolean {
    return this.currentUser !== null && this.token !== null;
  }

  async refreshToken(): Promise<string> {
    // Implementation
    return this.token ?? '';
  }
}

// Register Auth Service (commented out for now due to module resolution issues)
// import { serviceLocator } from '@valero-neuroerp/utilities';

const _authService = new AuthServiceImpl();
// serviceLocator.register<AuthService>('authService', _authService);


