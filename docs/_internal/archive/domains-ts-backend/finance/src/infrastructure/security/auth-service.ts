import { injectable } from 'inversify';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';
import crypto from 'crypto';
import { MetricsService } from '../observability/metrics-service';

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

export enum UserRole {
  ADMIN = 'admin',
  ACCOUNTANT = 'accountant',
  AUDITOR = 'auditor',
  MANAGER = 'manager',
  VIEWER = 'viewer'
}

export enum PermissionAction {
  CREATE = 'create',
  READ = 'read',
  UPDATE = 'update',
  DELETE = 'delete',
  APPROVE = 'approve',
  EXPORT = 'export'
}

@injectable()
export class AuthService {
  private readonly jwtSecret: string;
  private readonly jwtRefreshSecret: string;
  private readonly bcryptRounds: number;
  private readonly metrics = MetricsService.getInstance();

  // In-memory user store (in production, use database)
  private readonly users = new Map<string, User>();
  private readonly refreshTokens = new Set<string>();

  constructor() {
    this.jwtSecret = process.env.JWT_SECRET || 'your-secret-key';
    this.jwtRefreshSecret = process.env.JWT_REFRESH_SECRET || 'your-refresh-secret';
    this.bcryptRounds = parseInt(process.env.BCRYPT_ROUNDS || '12');

    // Initialize with default admin user
    this.initializeDefaultUsers();
  }

  private async initializeDefaultUsers(): Promise<void> {
    const adminUser: User = {
      id: 'admin-001',
      email: 'admin@finance.valero-neuroerp.com',
      roles: [UserRole.ADMIN],
      permissions: this.getPermissionsForRoles([UserRole.ADMIN]),
      tenantId: 'default',
      isActive: true,
      mfaEnabled: false
    };

    const hashedPassword = await bcrypt.hash('Admin123!', this.bcryptRounds);
    this.users.set(adminUser.email, adminUser);
    // In production, store hashed password in database
  }

  private getPermissionsForRoles(roles: string[]): string[] {
    const permissions: string[] = [];

    for (const role of roles) {
      switch (role) {
        case UserRole.ADMIN:
          permissions.push(
            'ledger:*',
            'invoice:*',
            'tax:*',
            'audit:*',
            'forecast:*',
            'user:*',
            'system:*'
          );
          break;
        case UserRole.ACCOUNTANT:
          permissions.push(
            'ledger:create',
            'ledger:read',
            'ledger:update',
            'invoice:create',
            'invoice:read',
            'invoice:update',
            'tax:read',
            'forecast:read'
          );
          break;
        case UserRole.AUDITOR:
          permissions.push(
            'ledger:read',
            'invoice:read',
            'tax:read',
            'audit:read',
            'audit:export'
          );
          break;
        case UserRole.MANAGER:
          permissions.push(
            'ledger:read',
            'invoice:read',
            'invoice:approve',
            'tax:read',
            'forecast:read',
            'report:read'
          );
          break;
        case UserRole.VIEWER:
          permissions.push(
            'ledger:read',
            'invoice:read',
            'tax:read',
            'forecast:read'
          );
          break;
      }
    }

    return [...new Set(permissions)]; // Remove duplicates
  }

  async authenticate(credentials: LoginCredentials): Promise<AuthToken> {
    const startTime = Date.now();

    try {
      const user = this.users.get(credentials.email);
      if (!user || !user.isActive) {
        this.metrics.incrementErrorCount('authentication', 'invalid_credentials');
        throw new Error('Invalid credentials');
      }

      // In production, verify password hash from database
      const isValidPassword = await bcrypt.compare(credentials.password, 'hashed-password-placeholder');
      if (!isValidPassword) {
        this.metrics.incrementErrorCount('authentication', 'invalid_credentials');
        throw new Error('Invalid credentials');
      }

      // Check MFA if enabled
      if (user.mfaEnabled) {
        if (!credentials.mfaCode) {
          throw new Error('MFA code required');
        }
        // Verify MFA code (implementation depends on MFA provider)
        const isValidMFA = await this.verifyMFACode(user.id, credentials.mfaCode);
        if (!isValidMFA) {
          this.metrics.incrementErrorCount('authentication', 'invalid_mfa');
          throw new Error('Invalid MFA code');
        }
      }

      // Update last login
      user.lastLogin = new Date();

      // Generate tokens
      const token = this.generateAccessToken(user);
      const refreshToken = this.generateRefreshToken(user);

      this.refreshTokens.add(refreshToken);

      this.metrics.recordApiResponseTime('POST', '/auth/login', 200, (Date.now() - startTime) / 1000);

      return {
        accessToken: token,
        refreshToken,
        expiresIn: 3600, // 1 hour
        tokenType: 'Bearer'
      };
    } catch (error) {
      this.metrics.incrementErrorCount('authentication', 'login_failed');
      throw error;
    }
  }

  async refreshToken(refreshToken: string): Promise<AuthToken> {
    try {
      if (!this.refreshTokens.has(refreshToken)) {
        throw new Error('Invalid refresh token');
      }

      const decoded = jwt.verify(refreshToken, this.jwtRefreshSecret) as any;
      const user = this.users.get(decoded.email);

      if (!user || !user.isActive) {
        throw new Error('User not found or inactive');
      }

      // Remove old refresh token
      this.refreshTokens.delete(refreshToken);

      // Generate new tokens
      const newToken = this.generateAccessToken(user);
      const newRefreshToken = this.generateRefreshToken(user);

      this.refreshTokens.add(newRefreshToken);

      return {
        accessToken: newToken,
        refreshToken: newRefreshToken,
        expiresIn: 3600,
        tokenType: 'Bearer'
      };
    } catch (error) {
      this.metrics.incrementErrorCount('authentication', 'token_refresh_failed');
      throw error;
    }
  }

  async logout(refreshToken: string): Promise<void> {
    this.refreshTokens.delete(refreshToken);
  }

  verifyAccessToken(token: string): User | null {
    try {
      const decoded = jwt.verify(token, this.jwtSecret) as any;
      const user = this.users.get(decoded.email);
      return user || null;
    } catch (error) {
      return null;
    }
  }

  hasPermission(user: User, resource: string, action: string): boolean {
    // Check if user has wildcard permission for resource
    if (user.permissions.includes(`${resource}:*`)) {
      return true;
    }

    // Check specific permission
    return user.permissions.includes(`${resource}:${action}`);
  }

  hasRole(user: User, role: string): boolean {
    return user.roles.includes(role);
  }

  private generateAccessToken(user: User): string {
    return jwt.sign(
      {
        sub: user.id,
        email: user.email,
        roles: user.roles,
        permissions: user.permissions,
        tenantId: user.tenantId
      },
      this.jwtSecret,
      { expiresIn: '1h' }
    );
  }

  private generateRefreshToken(user: User): string {
    return jwt.sign(
      {
        sub: user.id,
        email: user.email
      },
      this.jwtRefreshSecret,
      { expiresIn: '7d' }
    );
  }

  private async verifyMFACode(userId: string, code: string): Promise<boolean> {
    // Implementation depends on MFA provider (e.g., TOTP, SMS, etc.)
    // For now, return true for any 6-digit code
    return /^\d{6}$/.test(code);
  }

  // User management methods
  async createUser(userData: Omit<User, 'id' | 'permissions'>): Promise<User> {
    const user: User = {
      ...userData,
      id: crypto.randomUUID(),
      permissions: this.getPermissionsForRoles(userData.roles)
    };

    this.users.set(user.email, user);
    return user;
  }

  getUserById(id: string): User | null {
    for (const user of this.users.values()) {
      if (user.id === id) {
        return user;
      }
    }
    return null;
  }

  getUserByEmail(email: string): User | null {
    return this.users.get(email) || null;
  }

  async updateUser(id: string, updates: Partial<User>): Promise<User | null> {
    const user = this.getUserById(id);
    if (!user) {
      return null;
    }

    Object.assign(user, updates);

    // Recalculate permissions if roles changed
    if (updates.roles) {
      user.permissions = this.getPermissionsForRoles(updates.roles);
    }

    return user;
  }

  async deleteUser(id: string): Promise<boolean> {
    const user = this.getUserById(id);
    if (!user) {
      return false;
    }

    this.users.delete(user.email);
    return true;
  }
}

export default AuthService;