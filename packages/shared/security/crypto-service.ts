/**
 * Cryptography Service
 * ISO 27001 A.10 Cryptography Compliance
 * Secure encryption/decryption for Communications Security
 */

import { createCipheriv, createDecipheriv, randomBytes, scrypt, createHash, createHmac } from 'crypto';
import { promisify } from 'util';

const scryptAsync = promisify(scrypt);

export interface EncryptionResult {
  encrypted: string;
  iv: string;
  salt: string;
  algorithm: string;
  keyId: string;
}

export interface KeyMetadata {
  keyId: string;
  algorithm: string;
  keySize: number;
  purpose: 'ENCRYPTION' | 'SIGNING' | 'KEY_EXCHANGE';
  createdAt: Date;
  expiresAt: Date;
  status: 'ACTIVE' | 'EXPIRED' | 'REVOKED';
  tenantId: string;
}

export class CryptoService {
  private readonly algorithm = 'aes-256-gcm';
  private readonly keySize = 32; // 256 bits
  private readonly ivSize = 16; // 128 bits
  private readonly saltSize = 32; // 256 bits
  private readonly tagSize = 16; // 128 bits

  /**
   * Encrypts data using AES-256-GCM (ISO 27001 A.10.1.1)
   * Provides confidentiality and authenticity
   */
  async encrypt(plaintext: string, keyId?: string): Promise<EncryptionResult> {
    try {
      const salt = randomBytes(this.saltSize);
      const iv = randomBytes(this.ivSize);
      
      // Derive key using PBKDF2 (A.10.1.2 Key management)
      const key = await this.deriveKey(keyId || 'default', salt);
      
      const cipher = createCipheriv(this.algorithm, key, iv);
      
      let encrypted = cipher.update(plaintext, 'utf8', 'hex');
      encrypted += cipher.final('hex');
      
      const authTag = cipher.getAuthTag();
      const encryptedWithTag = encrypted + ':' + authTag.toString('hex');
      
      return {
        encrypted: encryptedWithTag,
        iv: iv.toString('hex'),
        salt: salt.toString('hex'),
        algorithm: this.algorithm,
        keyId: keyId || 'default'
      };
      
    } catch (error) {
      throw new Error(`Encryption failed: ${error.message}`);
    }
  }

  /**
   * Decrypts data using AES-256-GCM (ISO 27001 A.10.1.1)
   * Verifies authenticity and provides confidentiality
   */
  async decrypt(encryptionResult: EncryptionResult): Promise<string> {
    try {
      const salt = Buffer.from(encryptionResult.salt, 'hex');
      const iv = Buffer.from(encryptionResult.iv, 'hex');
      
      // Split encrypted data and auth tag
      const [encryptedData, authTagHex] = encryptionResult.encrypted.split(':');
      const authTag = Buffer.from(authTagHex, 'hex');
      
      // Derive the same key
      const key = await this.deriveKey(encryptionResult.keyId, salt);
      
      const decipher = createDecipheriv(this.algorithm, key, iv);
      decipher.setAuthTag(authTag);
      
      let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      
      return decrypted;
      
    } catch (error) {
      throw new Error(`Decryption failed: ${error.message}`);
    }
  }

  /**
   * Creates HMAC for data integrity (A.10.1.1)
   * Ensures data has not been tampered with
   */
  async createHmac(data: string, keyId: string = 'default'): Promise<string> {
    try {
      const key = await this.getHmacKey(keyId);
      const hmac = createHmac('sha256', key);
      hmac.update(data, 'utf8');
      return hmac.digest('hex');
    } catch (error) {
      throw new Error(`HMAC creation failed: ${error.message}`);
    }
  }

  /**
   * Verifies HMAC for data integrity (A.10.1.1)
   */
  async verifyHmac(data: string, expectedHmac: string, keyId: string = 'default'): Promise<boolean> {
    try {
      const computedHmac = await this.createHmac(data, keyId);
      
      // Constant-time comparison to prevent timing attacks
      return this.constantTimeCompare(computedHmac, expectedHmac);
    } catch (error) {
      throw new Error(`HMAC verification failed: ${error.message}`);
    }
  }

  /**
   * Hashes data using SHA-256 (A.10.1.1)
   * For one-way hashing of passwords, etc.
   */
  async hash(data: string, salt?: string): Promise<{ hash: string; salt: string }> {
    try {
      const actualSalt = salt || randomBytes(this.saltSize).toString('hex');
      const hash = createHash('sha256');
      hash.update(data + actualSalt);
      
      return {
        hash: hash.digest('hex'),
        salt: actualSalt
      };
    } catch (error) {
      throw new Error(`Hashing failed: ${error.message}`);
    }
  }

  /**
   * Generates cryptographically secure random data
   * For tokens, IDs, etc. (A.10.1.2)
   */
  async generateSecureRandom(size: number = 32): Promise<string> {
    try {
      return randomBytes(size).toString('hex');
    } catch (error) {
      throw new Error(`Random generation failed: ${error.message}`);
    }
  }

  /**
   * Key rotation functionality (A.10.1.2 Key management)
   * Regularly rotates encryption keys for security
   */
  async rotateKey(keyId: string, tenantId: string): Promise<KeyMetadata> {
    try {
      const newKeyMetadata: KeyMetadata = {
        keyId: `${keyId}-${Date.now()}`,
        algorithm: this.algorithm,
        keySize: this.keySize,
        purpose: 'ENCRYPTION',
        createdAt: new Date(),
        expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000), // 1 year
        status: 'ACTIVE',
        tenantId
      };
      
      // In real implementation, would store in secure key management system
      console.log(`Key rotated: ${newKeyMetadata.keyId} for tenant ${tenantId}`);
      
      return newKeyMetadata;
    } catch (error) {
      throw new Error(`Key rotation failed: ${error.message}`);
    }
  }

  /**
   * Validates encryption strength meets ISO 27001 requirements
   */
  validateEncryptionStandards(algorithm: string, keySize: number): boolean {
    const approvedAlgorithms = [
      'aes-256-gcm', 'aes-256-cbc', 'aes-192-gcm', 
      'chacha20-poly1305'
    ];
    
    const minimumKeySizes = {
      'aes-256-gcm': 256,
      'aes-256-cbc': 256,
      'aes-192-gcm': 192,
      'chacha20-poly1305': 256
    };
    
    return approvedAlgorithms.includes(algorithm) && 
           keySize >= minimumKeySizes[algorithm];
  }

  // Private helper methods

  private async deriveKey(keyId: string, salt: Buffer): Promise<Buffer> {
    // In real implementation, would retrieve master key from secure key store
    const masterKey = await this.getMasterKey(keyId);
    
    // Use PBKDF2 for key derivation (A.10.1.2)
    const derivedKey = await scryptAsync(masterKey, salt, this.keySize) as Buffer;
    return derivedKey;
  }

  private async getMasterKey(keyId: string): Promise<string> {
    // In real implementation, would retrieve from Hardware Security Module (HSM)
    // or secure key management service
    const masterKeys = {
      'default': process.env.CRYPTO_MASTER_KEY || 'default-master-key-for-dev-only',
      'sales': process.env.SALES_CRYPTO_KEY || 'sales-master-key-for-dev-only',
      'delivery': process.env.DELIVERY_CRYPTO_KEY || 'delivery-master-key-for-dev-only'
    };
    
    return masterKeys[keyId] || masterKeys['default'];
  }

  private async getHmacKey(keyId: string): Promise<string> {
    // In real implementation, would retrieve HMAC key from secure storage
    const hmacKeys = {
      'default': process.env.HMAC_KEY || 'default-hmac-key-for-dev-only'
    };
    
    return hmacKeys[keyId] || hmacKeys['default'];
  }

  private constantTimeCompare(a: string, b: string): boolean {
    if (a.length !== b.length) {
      return false;
    }
    
    let result = 0;
    for (let i = 0; i < a.length; i++) {
      result |= a.charCodeAt(i) ^ b.charCodeAt(i);
    }
    
    return result === 0;
  }
}
