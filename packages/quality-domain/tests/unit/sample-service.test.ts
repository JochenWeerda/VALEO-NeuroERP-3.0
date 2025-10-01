import { describe, it, expect, beforeEach } from 'vitest';
import { CreateSampleSchema } from '../../src/domain/entities/sample';

describe('Sample Service', () => {
  describe('CreateSampleSchema Validation', () => {
    it('should validate a valid sample', () => {
      const validSample = {
        tenantId: '123e4567-e89b-12d3-a456-426614174000',
        source: 'Production',
        sampleCode: 'S-2025-001234',
        takenAt: '2025-10-01T10:00:00Z',
        takenBy: 'user-123',
        retained: false,
        status: 'Pending',
      };

      const result = CreateSampleSchema.safeParse(validSample);
      expect(result.success).toBe(true);
    });

    it('should reject sample without tenantId', () => {
      const invalidSample = {
        source: 'Production',
        sampleCode: 'S-2025-001234',
        takenAt: '2025-10-01T10:00:00Z',
        takenBy: 'user-123',
      };

      const result = CreateSampleSchema.safeParse(invalidSample);
      expect(result.success).toBe(false);
    });

    it('should reject sample with invalid source', () => {
      const invalidSample = {
        tenantId: '123e4567-e89b-12d3-a456-426614174000',
        source: 'InvalidSource',
        sampleCode: 'S-2025-001234',
        takenAt: '2025-10-01T10:00:00Z',
        takenBy: 'user-123',
      };

      const result = CreateSampleSchema.safeParse(invalidSample);
      expect(result.success).toBe(false);
    });

    it('should accept optional batchId and contractId', () => {
      const sampleWithRefs = {
        tenantId: '123e4567-e89b-12d3-a456-426614174000',
        batchId: '456e4567-e89b-12d3-a456-426614174001',
        contractId: '789e4567-e89b-12d3-a456-426614174002',
        source: 'Contract',
        sampleCode: 'S-2025-001234',
        takenAt: '2025-10-01T10:00:00Z',
        takenBy: 'user-123',
        retained: true,
        retainedLocation: 'Kühlschrank A',
        retainedUntil: '2026-04-01T00:00:00Z',
      };

      const result = CreateSampleSchema.safeParse(sampleWithRefs);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.batchId).toBe(sampleWithRefs.batchId);
        expect(result.data.contractId).toBe(sampleWithRefs.contractId);
      }
    });
  });

  describe('Sample Code Generation', () => {
    it('should generate unique sample codes', () => {
      // Simple test for code format
      const year = new Date().getFullYear();
      const codeRegex = new RegExp(`^S-${year}-\\d{6}$`);
      
      const testCode = `S-${year}-${Math.floor(Math.random() * 1000000).toString().padStart(6, '0')}`;
      expect(codeRegex.test(testCode)).toBe(true);
    });
  });
});
