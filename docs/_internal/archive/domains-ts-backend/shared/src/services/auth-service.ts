/**
 * VALEO NeuroERP 3.0 - Authentication Service
 */

import { injectable } from 'inversify';
import * as bcrypt from 'bcrypt';
import * as jwt from 'jsonwebtoken';

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

@injectable()
export class AuthService {
  private readonly JWT_SECRET = process.env.JWT_SECRET || 'default-secret';
  private readonly SALT_ROUNDS = 10;

  async authenticate(email: string, password: string): Promise<AuthResult | null> {
    // Simplified authentication logic
    // In production, validate against database
    const user: User = {
      id: '1',
      email,
      password: await bcrypt.hash(password, this.SALT_ROUNDS),
      role: 'user',
      tenantId: 'default'
    };

    const isValid = await bcrypt.compare(password, user.password);
    if (!isValid) {
      return null;
    }

    const token = jwt.sign(
      { userId: user.id, email: user.email, role: user.role },
      this.JWT_SECRET,
      { expiresIn: '24h' }
    );

    return {
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
        tenantId: user.tenantId
      },
      token
    };
  }

  async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, this.SALT_ROUNDS);
  }

  async verifyToken(token: string): Promise<any> {
    try {
      return jwt.verify(token, this.JWT_SECRET);
    } catch {
      return null;
    }
  }
}
