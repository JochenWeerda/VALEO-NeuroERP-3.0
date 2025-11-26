/**
 * Quality Certificate Entity
 * Complete Quality Certificate Management for Agribusiness
 * Based on Odoo quality module pattern
 */

import { randomUUID } from 'crypto';

export type QualityCertificateType = 
  | 'SEED'             // Saatgut-Qualität
  | 'FERTILIZER'       // Düngemittel-Analyse
  | 'FEED'             // Futtermittel-Qualität
  | 'CROP';            // Ernte-Qualität

export type QualityCertificateStatus = 
  | 'DRAFT'            // Entwurf
  | 'ISSUED'           // Ausgestellt
  | 'VALID'            // Gültig
  | 'EXPIRED'          // Abgelaufen
  | 'REVOKED';         // Widerrufen

export interface QualityTestResult {
  id: string;
  testName: string;
  testMethod?: string;
  testValue: number | string;
  unit?: string;
  minValue?: number;
  maxValue?: number;
  passed: boolean;
  notes?: string;
  testedAt: Date;
  testedBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateQualityCertificateInput {
  certificateNumber: string;
  certificateType: QualityCertificateType;
  productId: string;
  batchId?: string;
  issuedBy: string;
  issuedAt: Date;
  validUntil: Date;
  testResults: Omit<QualityTestResult, 'id' | 'createdAt' | 'updatedAt'>[];
  notes?: string;
  customFields?: Record<string, unknown>;
}

export interface UpdateQualityCertificateInput {
  certificateNumber?: string;
  validUntil?: Date;
  notes?: string;
  customFields?: Record<string, unknown>;
}

export class QualityCertificate {
  public readonly id: string;
  public certificateNumber: string;
  public certificateType: QualityCertificateType;
  public productId: string;
  public batchId?: string;
  public status: QualityCertificateStatus;
  public issuedBy: string;
  public issuedAt: Date;
  public validUntil: Date;
  public testResults: QualityTestResult[];
  public notes?: string;
  public customFields?: Record<string, unknown>;
  public version: number;
  public readonly createdAt: Date;
  public updatedAt: Date;
  public revokedAt?: Date;
  public revokedBy?: string;
  public revocationReason?: string;

  constructor(
    certificateNumber: string,
    certificateType: QualityCertificateType,
    productId: string,
    issuedBy: string,
    issuedAt: Date,
    validUntil: Date,
    testResults: QualityTestResult[],
    options: {
      id?: string;
      batchId?: string;
      notes?: string;
      customFields?: Record<string, unknown>;
    } = {}
  ) {
    this.id = options.id || randomUUID();
    this.certificateNumber = certificateNumber;
    this.certificateType = certificateType;
    this.productId = productId;
    this.batchId = options.batchId;
    this.status = 'DRAFT';
    this.issuedBy = issuedBy;
    this.issuedAt = issuedAt;
    this.validUntil = validUntil;
    this.testResults = testResults;
    this.notes = options.notes;
    this.customFields = options.customFields;
    this.version = 1;
    this.createdAt = new Date();
    this.updatedAt = new Date();

    this.validate();
  }

  private validate(): void {
    if (!this.certificateNumber || this.certificateNumber.trim() === '') {
      throw new Error('Certificate number is required');
    }

    if (!this.productId || this.productId.trim() === '') {
      throw new Error('Product ID is required');
    }

    if (this.issuedAt >= this.validUntil) {
      throw new Error('Issue date must be before valid until date');
    }

    if (this.testResults.length === 0) {
      throw new Error('At least one test result is required');
    }
  }

  public issue(issuedBy: string): void {
    if (this.status !== 'DRAFT') {
      throw new Error('Can only issue draft certificates');
    }

    // Validate all test results passed
    const allPassed = this.testResults.every(result => result.passed);
    if (!allPassed) {
      throw new Error('Cannot issue certificate with failed test results');
    }

    this.status = 'ISSUED';
    this.issuedBy = issuedBy;
    this.issuedAt = new Date();
    this.updatedAt = new Date();
    this.version++;
  }

  public validateCertificate(): void {
    if (this.status !== 'ISSUED') {
      throw new Error('Can only validate issued certificates');
    }

    if (this.isExpired()) {
      this.status = 'EXPIRED';
    } else {
      this.status = 'VALID';
    }

    this.updatedAt = new Date();
    this.version++;
  }

  public revoke(revokedBy: string, reason: string): void {
    if (['REVOKED', 'EXPIRED'].includes(this.status)) {
      throw new Error('Cannot revoke already revoked or expired certificate');
    }

    this.status = 'REVOKED';
    this.revokedAt = new Date();
    this.revokedBy = revokedBy;
    this.revocationReason = reason;
    this.updatedAt = new Date();
    this.version++;
  }

  public updateBasicInfo(updates: UpdateQualityCertificateInput): void {
    if (!['DRAFT', 'ISSUED'].includes(this.status)) {
      throw new Error('Can only update draft or issued certificates');
    }

    if (updates.certificateNumber !== undefined) this.certificateNumber = updates.certificateNumber;
    if (updates.validUntil !== undefined) {
      if (updates.validUntil <= this.issuedAt) {
        throw new Error('Valid until date must be after issue date');
      }
      this.validUntil = updates.validUntil;
    }
    if (updates.notes !== undefined) this.notes = updates.notes;
    if (updates.customFields !== undefined) {
      this.customFields = {
        ...this.customFields,
        ...updates.customFields
      };
    }

    this.updatedAt = new Date();
    this.version++;
    this.validate();
  }

  public addTestResult(testResult: Omit<QualityTestResult, 'id' | 'createdAt' | 'updatedAt'>): QualityTestResult {
    if (!['DRAFT', 'ISSUED'].includes(this.status)) {
      throw new Error('Can only add test results to draft or issued certificates');
    }

    const newTestResult: QualityTestResult = {
      ...testResult,
      id: randomUUID(),
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.testResults.push(newTestResult);
    this.updatedAt = new Date();
    this.version++;

    return newTestResult;
  }

  public updateTestResult(testResultId: string, updates: Partial<Omit<QualityTestResult, 'id' | 'createdAt' | 'updatedAt'>>): void {
    if (!['DRAFT', 'ISSUED'].includes(this.status)) {
      throw new Error('Can only update test results in draft or issued certificates');
    }

    const testResultIndex = this.testResults.findIndex(tr => tr.id === testResultId);
    if (testResultIndex === -1) {
      throw new Error('Test result not found');
    }

    Object.assign(this.testResults[testResultIndex], updates, { updatedAt: new Date() });
    this.updatedAt = new Date();
    this.version++;
  }

  public removeTestResult(testResultId: string): void {
    if (!['DRAFT'].includes(this.status)) {
      throw new Error('Can only remove test results from draft certificates');
    }

    const testResultIndex = this.testResults.findIndex(tr => tr.id === testResultId);
    if (testResultIndex === -1) {
      throw new Error('Test result not found');
    }

    this.testResults.splice(testResultIndex, 1);
    this.updatedAt = new Date();
    this.version++;
  }

  public isExpired(): boolean {
    return new Date() > this.validUntil;
  }

  public isExpiringSoon(days: number = 30): boolean {
    const now = new Date();
    const daysUntilExpiry = Math.ceil((this.validUntil.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry <= days && daysUntilExpiry > 0;
  }

  public isValid(): boolean {
    return this.status === 'VALID' && !this.isExpired();
  }

  public getDaysUntilExpiry(): number {
    const now = new Date();
    return Math.ceil((this.validUntil.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  }

  public getAllTestResultsPassed(): boolean {
    return this.testResults.every(result => result.passed);
  }

  public getFailedTestResults(): QualityTestResult[] {
    return this.testResults.filter(result => !result.passed);
  }

  public toJSON(): any {
    return {
      id: this.id,
      certificateNumber: this.certificateNumber,
      certificateType: this.certificateType,
      productId: this.productId,
      batchId: this.batchId,
      status: this.status,
      issuedBy: this.issuedBy,
      issuedAt: this.issuedAt.toISOString(),
      validUntil: this.validUntil.toISOString(),
      testResults: this.testResults.map(tr => ({
        ...tr,
        testedAt: tr.testedAt.toISOString(),
        createdAt: tr.createdAt.toISOString(),
        updatedAt: tr.updatedAt.toISOString()
      })),
      notes: this.notes,
      customFields: this.customFields,
      isExpired: this.isExpired(),
      isExpiringSoon: this.isExpiringSoon(),
      isValid: this.isValid(),
      daysUntilExpiry: this.getDaysUntilExpiry(),
      allTestsPassed: this.getAllTestResultsPassed(),
      failedTests: this.getFailedTestResults().length,
      version: this.version,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      revokedAt: this.revokedAt?.toISOString(),
      revokedBy: this.revokedBy,
      revocationReason: this.revocationReason
    };
  }
}
