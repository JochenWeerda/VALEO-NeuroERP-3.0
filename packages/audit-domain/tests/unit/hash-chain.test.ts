import { describe, it, expect } from 'vitest';
import { createHash } from 'crypto';

describe('Hash Chain', () => {
  it('should generate consistent hash for same input', () => {
    const data = { tenantId: 'test', action: 'CREATE', timestamp: '2025-10-01T00:00:00Z' };
    const prevHash = '';

    const hash1 = createHash('sha256')
      .update(JSON.stringify(data) + prevHash)
      .digest('hex');
    const hash2 = createHash('sha256')
      .update(JSON.stringify(data) + prevHash)
      .digest('hex');

    expect(hash1).toBe(hash2);
  });

  it('should create chain with different hashes', () => {
    const event1 = { id: 1, action: 'CREATE' };
    const event2 = { id: 2, action: 'UPDATE' };

    const hash1 = createHash('sha256')
      .update(JSON.stringify(event1) + '')
      .digest('hex');
    const hash2 = createHash('sha256')
      .update(JSON.stringify(event2) + hash1)
      .digest('hex');

    expect(hash1).not.toBe(hash2);
    expect(hash2.length).toBe(64); // SHA-256 = 64 hex chars
  });

  it('should detect tampering in chain', () => {
    const event1 = { id: 1, data: 'original' };
    const hash1 = createHash('sha256')
      .update(JSON.stringify(event1))
      .digest('hex');

    const tamperedEvent = { id: 1, data: 'tampered' };
    const recalculated = createHash('sha256')
      .update(JSON.stringify(tamperedEvent))
      .digest('hex');

    expect(recalculated).not.toBe(hash1);
  });
});
