/**
 * Quality Certificate Service
 * Complete Quality Certificate Management based on Odoo quality module pattern
 */

import { QualityCertificate, QualityTestResult, CreateQualityCertificateInput, UpdateQualityCertificateInput, QualityCertificateStatus } from '../entities/quality-certificate';
import { QualityCertificateRepository, QualityCertificateFilter, QualityCertificateSort, PaginatedQualityCertificateResult } from '../../infra/repositories/quality-certificate-repository';

export interface QualityCertificateServiceDependencies {
  qualityCertificateRepository: QualityCertificateRepository;
}

export class QualityCertificateService {
  constructor(private deps: QualityCertificateServiceDependencies) {}

  // ======================================
  // CORE CRUD OPERATIONS
  // ======================================

  async createQualityCertificate(
    input: CreateQualityCertificateInput,
    createdBy: string
  ): Promise<QualityCertificate> {
    // Convert test results to full QualityTestResult objects
    const testResults: QualityTestResult[] = input.testResults.map(result => ({
      ...result,
      id: '', // Will be set by entity constructor
      createdAt: new Date(),
      updatedAt: new Date()
    }));

    const certificate = new QualityCertificate(
      input.certificateNumber,
      input.certificateType,
      input.productId,
      input.issuedBy,
      input.issuedAt,
      input.validUntil,
      testResults,
      {
        batchId: input.batchId,
        notes: input.notes,
        customFields: input.customFields
      }
    );

    return await this.deps.qualityCertificateRepository.create(certificate);
  }

  async getQualityCertificateById(id: string): Promise<QualityCertificate | null> {
    return await this.deps.qualityCertificateRepository.findById(id);
  }

  async getQualityCertificateByNumber(certificateNumber: string): Promise<QualityCertificate | null> {
    return await this.deps.qualityCertificateRepository.findByCertificateNumber(certificateNumber);
  }

  async updateQualityCertificate(
    id: string,
    updates: UpdateQualityCertificateInput
  ): Promise<QualityCertificate> {
    const certificate = await this.getQualityCertificateById(id);
    if (!certificate) {
      throw new Error('Quality certificate not found');
    }

    certificate.updateBasicInfo(updates);
    return await this.deps.qualityCertificateRepository.update(certificate);
  }

  async deleteQualityCertificate(id: string): Promise<boolean> {
    const certificate = await this.getQualityCertificateById(id);
    if (!certificate) {
      return false;
    }

    if (!['DRAFT', 'REVOKED'].includes(certificate.status)) {
      throw new Error('Can only delete draft or revoked certificates');
    }

    return await this.deps.qualityCertificateRepository.delete(id);
  }

  // ======================================
  // STATUS WORKFLOWS
  // ======================================

  async issueCertificate(certificateId: string, issuedBy: string): Promise<QualityCertificate> {
    const certificate = await this.getQualityCertificateById(certificateId);
    if (!certificate) {
      throw new Error('Quality certificate not found');
    }

    certificate.issue(issuedBy);
    return await this.deps.qualityCertificateRepository.update(certificate);
  }

  async validateCertificate(certificateId: string): Promise<QualityCertificate> {
    const certificate = await this.getQualityCertificateById(certificateId);
    if (!certificate) {
      throw new Error('Quality certificate not found');
    }

    certificate.validateCertificate();
    return await this.deps.qualityCertificateRepository.update(certificate);
  }

  async revokeCertificate(
    certificateId: string,
    revokedBy: string,
    reason: string
  ): Promise<QualityCertificate> {
    const certificate = await this.getQualityCertificateById(certificateId);
    if (!certificate) {
      throw new Error('Quality certificate not found');
    }

    certificate.revoke(revokedBy, reason);
    return await this.deps.qualityCertificateRepository.update(certificate);
  }

  // ======================================
  // TEST RESULT MANAGEMENT
  // ======================================

  async addTestResult(
    certificateId: string,
    testResult: Omit<QualityTestResult, 'id' | 'createdAt' | 'updatedAt'>
  ): Promise<QualityCertificate> {
    const certificate = await this.getQualityCertificateById(certificateId);
    if (!certificate) {
      throw new Error('Quality certificate not found');
    }

    certificate.addTestResult(testResult);
    return await this.deps.qualityCertificateRepository.update(certificate);
  }

  async updateTestResult(
    certificateId: string,
    testResultId: string,
    updates: Partial<Omit<QualityTestResult, 'id' | 'createdAt' | 'updatedAt'>>
  ): Promise<QualityCertificate> {
    const certificate = await this.getQualityCertificateById(certificateId);
    if (!certificate) {
      throw new Error('Quality certificate not found');
    }

    certificate.updateTestResult(testResultId, updates);
    return await this.deps.qualityCertificateRepository.update(certificate);
  }

  async removeTestResult(
    certificateId: string,
    testResultId: string
  ): Promise<QualityCertificate> {
    const certificate = await this.getQualityCertificateById(certificateId);
    if (!certificate) {
      throw new Error('Quality certificate not found');
    }

    certificate.removeTestResult(testResultId);
    return await this.deps.qualityCertificateRepository.update(certificate);
  }

  // ======================================
  // QUERY METHODS
  // ======================================

  async listQualityCertificates(
    filter: QualityCertificateFilter = {},
    sort: QualityCertificateSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedQualityCertificateResult> {
    return await this.deps.qualityCertificateRepository.list(filter, sort, page, pageSize);
  }

  async getQualityCertificatesByProduct(productId: string): Promise<QualityCertificate[]> {
    return await this.deps.qualityCertificateRepository.findByProductId(productId);
  }

  async getQualityCertificatesByBatch(batchId: string): Promise<QualityCertificate[]> {
    return await this.deps.qualityCertificateRepository.findByBatchId(batchId);
  }

  async getQualityCertificatesByStatus(status: QualityCertificateStatus): Promise<QualityCertificate[]> {
    return await this.deps.qualityCertificateRepository.findByStatus(status);
  }

  async getExpiredCertificates(): Promise<QualityCertificate[]> {
    return await this.deps.qualityCertificateRepository.findExpiredCertificates();
  }

  async getExpiringSoonCertificates(days: number = 30): Promise<QualityCertificate[]> {
    return await this.deps.qualityCertificateRepository.findExpiringSoonCertificates(days);
  }

  async getValidCertificates(): Promise<QualityCertificate[]> {
    return await this.deps.qualityCertificateRepository.findValidCertificates();
  }

  // ======================================
  // BUSINESS INTELLIGENCE & ANALYTICS
  // ======================================

  async getQualityCertificateStatistics(): Promise<{
    total: number;
    byStatus: Record<QualityCertificateStatus, number>;
    byType: Record<string, number>;
    expiredCount: number;
    expiringSoonCount: number;
    validCount: number;
  }> {
    return await this.deps.qualityCertificateRepository.getStatistics();
  }
}
