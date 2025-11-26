/**
 * Quality Certificate Repository
 * Complete CRUD operations for Quality Certificates
 */

import { QualityCertificate, QualityCertificateStatus, QualityCertificateType } from '../../domain/entities/quality-certificate';

export interface QualityCertificateFilter {
  certificateNumber?: string;
  certificateType?: QualityCertificateType;
  productId?: string;
  batchId?: string;
  status?: QualityCertificateStatus;
  issuedBy?: string;
  validUntilFrom?: Date;
  validUntilTo?: Date;
  expired?: boolean;
  expiringSoon?: boolean;
  search?: string; // Search in certificateNumber, notes
}

export interface QualityCertificateSort {
  field: 'createdAt' | 'updatedAt' | 'issuedAt' | 'validUntil' | 'certificateNumber' | 'status';
  direction: 'asc' | 'desc';
}

export interface PaginatedQualityCertificateResult {
  items: QualityCertificate[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export class QualityCertificateRepository {
  private certificates: Map<string, QualityCertificate> = new Map();

  async create(certificate: QualityCertificate): Promise<QualityCertificate> {
    // Check for duplicate certificate number
    const existing = await this.findByCertificateNumber(certificate.certificateNumber);
    if (existing && existing.id !== certificate.id) {
      throw new Error(`Certificate number ${certificate.certificateNumber} already exists`);
    }

    this.certificates.set(certificate.id, certificate);
    return certificate;
  }

  async findById(id: string): Promise<QualityCertificate | null> {
    return this.certificates.get(id) || null;
  }

  async findByCertificateNumber(certificateNumber: string): Promise<QualityCertificate | null> {
    for (const certificate of this.certificates.values()) {
      if (certificate.certificateNumber === certificateNumber) {
        return certificate;
      }
    }
    return null;
  }

  async update(certificate: QualityCertificate): Promise<QualityCertificate> {
    if (!this.certificates.has(certificate.id)) {
      throw new Error('Quality certificate not found');
    }

    // Check for duplicate certificate number (excluding current certificate)
    const existing = await this.findByCertificateNumber(certificate.certificateNumber);
    if (existing && existing.id !== certificate.id) {
      throw new Error(`Certificate number ${certificate.certificateNumber} already exists`);
    }

    this.certificates.set(certificate.id, certificate);
    return certificate;
  }

  async delete(id: string): Promise<boolean> {
    return this.certificates.delete(id);
  }

  async findByProductId(productId: string): Promise<QualityCertificate[]> {
    const certificates: QualityCertificate[] = [];
    for (const certificate of this.certificates.values()) {
      if (certificate.productId === productId) {
        certificates.push(certificate);
      }
    }
    return certificates.sort((a, b) => b.issuedAt.getTime() - a.issuedAt.getTime());
  }

  async findByBatchId(batchId: string): Promise<QualityCertificate[]> {
    const certificates: QualityCertificate[] = [];
    for (const certificate of this.certificates.values()) {
      if (certificate.batchId === batchId) {
        certificates.push(certificate);
      }
    }
    return certificates.sort((a, b) => b.issuedAt.getTime() - a.issuedAt.getTime());
  }

  async findByStatus(status: QualityCertificateStatus): Promise<QualityCertificate[]> {
    const certificates: QualityCertificate[] = [];
    for (const certificate of this.certificates.values()) {
      if (certificate.status === status) {
        certificates.push(certificate);
      }
    }
    return certificates.sort((a, b) => b.issuedAt.getTime() - a.issuedAt.getTime());
  }

  async findExpiredCertificates(): Promise<QualityCertificate[]> {
    const certificates: QualityCertificate[] = [];
    for (const certificate of this.certificates.values()) {
      if (certificate.isExpired()) {
        certificates.push(certificate);
      }
    }
    return certificates.sort((a, b) => a.validUntil.getTime() - b.validUntil.getTime());
  }

  async findExpiringSoonCertificates(days: number = 30): Promise<QualityCertificate[]> {
    const certificates: QualityCertificate[] = [];
    for (const certificate of this.certificates.values()) {
      if (certificate.isExpiringSoon(days)) {
        certificates.push(certificate);
      }
    }
    return certificates.sort((a, b) => a.validUntil.getTime() - b.validUntil.getTime());
  }

  async findValidCertificates(): Promise<QualityCertificate[]> {
    const certificates: QualityCertificate[] = [];
    for (const certificate of this.certificates.values()) {
      if (certificate.isValid()) {
        certificates.push(certificate);
      }
    }
    return certificates.sort((a, b) => b.issuedAt.getTime() - a.issuedAt.getTime());
  }

  async list(
    filter: QualityCertificateFilter = {},
    sort: QualityCertificateSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedQualityCertificateResult> {
    let filteredCertificates = Array.from(this.certificates.values());

    // Apply filters
    if (filter.certificateNumber) {
      filteredCertificates = filteredCertificates.filter(cert => 
        cert.certificateNumber.toLowerCase().includes(filter.certificateNumber!.toLowerCase())
      );
    }

    if (filter.certificateType) {
      filteredCertificates = filteredCertificates.filter(cert => cert.certificateType === filter.certificateType);
    }

    if (filter.productId) {
      filteredCertificates = filteredCertificates.filter(cert => cert.productId === filter.productId);
    }

    if (filter.batchId) {
      filteredCertificates = filteredCertificates.filter(cert => cert.batchId === filter.batchId);
    }

    if (filter.status) {
      filteredCertificates = filteredCertificates.filter(cert => cert.status === filter.status);
    }

    if (filter.issuedBy) {
      filteredCertificates = filteredCertificates.filter(cert => cert.issuedBy === filter.issuedBy);
    }

    if (filter.validUntilFrom) {
      filteredCertificates = filteredCertificates.filter(cert => 
        cert.validUntil >= filter.validUntilFrom!
      );
    }

    if (filter.validUntilTo) {
      filteredCertificates = filteredCertificates.filter(cert => 
        cert.validUntil <= filter.validUntilTo!
      );
    }

    if (filter.expired === true) {
      filteredCertificates = filteredCertificates.filter(cert => cert.isExpired());
    }

    if (filter.expiringSoon === true) {
      filteredCertificates = filteredCertificates.filter(cert => cert.isExpiringSoon());
    }

    if (filter.search) {
      const searchLower = filter.search.toLowerCase();
      filteredCertificates = filteredCertificates.filter(cert => 
        cert.certificateNumber.toLowerCase().includes(searchLower) ||
        (cert.notes && cert.notes.toLowerCase().includes(searchLower))
      );
    }

    // Apply sorting
    filteredCertificates.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sort.field) {
        case 'createdAt':
          aValue = a.createdAt.getTime();
          bValue = b.createdAt.getTime();
          break;
        case 'updatedAt':
          aValue = a.updatedAt.getTime();
          bValue = b.updatedAt.getTime();
          break;
        case 'issuedAt':
          aValue = a.issuedAt.getTime();
          bValue = b.issuedAt.getTime();
          break;
        case 'validUntil':
          aValue = a.validUntil.getTime();
          bValue = b.validUntil.getTime();
          break;
        case 'certificateNumber':
          aValue = a.certificateNumber;
          bValue = b.certificateNumber;
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        default:
          aValue = a.createdAt.getTime();
          bValue = b.createdAt.getTime();
      }

      if (sort.direction === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    // Apply pagination
    const total = filteredCertificates.length;
    const totalPages = Math.ceil(total / pageSize);
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const items = filteredCertificates.slice(startIndex, endIndex);

    return {
      items,
      total,
      page,
      pageSize,
      totalPages,
      hasNext: page < totalPages,
      hasPrev: page > 1
    };
  }

  async getStatistics(): Promise<{
    total: number;
    byStatus: Record<QualityCertificateStatus, number>;
    byType: Record<QualityCertificateType, number>;
    expiredCount: number;
    expiringSoonCount: number;
    validCount: number;
  }> {
    const allCertificates = Array.from(this.certificates.values());
    const total = allCertificates.length;

    const byStatus: Record<QualityCertificateStatus, number> = {
      'DRAFT': 0,
      'ISSUED': 0,
      'VALID': 0,
      'EXPIRED': 0,
      'REVOKED': 0
    };

    const byType: Record<QualityCertificateType, number> = {
      'SEED': 0,
      'FERTILIZER': 0,
      'FEED': 0,
      'CROP': 0
    };

    let expiredCount = 0;
    let expiringSoonCount = 0;
    let validCount = 0;

    for (const certificate of allCertificates) {
      byStatus[certificate.status]++;
      byType[certificate.certificateType]++;
      
      if (certificate.isExpired()) expiredCount++;
      if (certificate.isExpiringSoon()) expiringSoonCount++;
      if (certificate.isValid()) validCount++;
    }

    return {
      total,
      byStatus,
      byType,
      expiredCount,
      expiringSoonCount,
      validCount
    };
  }

  async isCertificateNumberUnique(certificateNumber: string, excludeId?: string): Promise<boolean> {
    for (const certificate of this.certificates.values()) {
      if (certificate.certificateNumber === certificateNumber && certificate.id !== excludeId) {
        return false;
      }
    }
    return true;
  }
}
