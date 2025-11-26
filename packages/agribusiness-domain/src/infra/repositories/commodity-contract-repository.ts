/**
 * Commodity Contract Repository
 * Complete CRUD operations for Commodity Contracts
 */

import { CommodityContract, CommodityContractStatus, ContractType, CommodityType } from '../../domain/entities/commodity-contract';

export interface CommodityContractFilter {
  contractNumber?: string;
  contractType?: ContractType;
  supplierId?: string;
  status?: CommodityContractStatus;
  commodity?: CommodityType;
  contractDateFrom?: Date;
  contractDateTo?: Date;
  deliveryPeriodStartFrom?: Date;
  deliveryPeriodStartTo?: Date;
  deliveryPeriodEndFrom?: Date;
  deliveryPeriodEndTo?: Date;
  expired?: boolean;
  search?: string; // Search in contractNumber, notes
}

export interface CommodityContractSort {
  field: 'createdAt' | 'updatedAt' | 'contractDate' | 'deliveryPeriodStart' | 'deliveryPeriodEnd' | 'contractNumber' | 'status' | 'totalContractValue';
  direction: 'asc' | 'desc';
}

export interface PaginatedCommodityContractResult {
  items: CommodityContract[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export class CommodityContractRepository {
  private contracts: Map<string, CommodityContract> = new Map();

  async create(contract: CommodityContract): Promise<CommodityContract> {
    // Check for duplicate contract number
    const existing = await this.findByContractNumber(contract.contractNumber);
    if (existing && existing.id !== contract.id) {
      throw new Error(`Contract number ${contract.contractNumber} already exists`);
    }

    this.contracts.set(contract.id, contract);
    return contract;
  }

  async findById(id: string): Promise<CommodityContract | null> {
    return this.contracts.get(id) || null;
  }

  async findByContractNumber(contractNumber: string): Promise<CommodityContract | null> {
    for (const contract of this.contracts.values()) {
      if (contract.contractNumber === contractNumber) {
        return contract;
      }
    }
    return null;
  }

  async update(contract: CommodityContract): Promise<CommodityContract> {
    if (!this.contracts.has(contract.id)) {
      throw new Error('Commodity contract not found');
    }

    // Check for duplicate contract number (excluding current contract)
    const existing = await this.findByContractNumber(contract.contractNumber);
    if (existing && existing.id !== contract.id) {
      throw new Error(`Contract number ${contract.contractNumber} already exists`);
    }

    this.contracts.set(contract.id, contract);
    return contract;
  }

  async delete(id: string): Promise<boolean> {
    return this.contracts.delete(id);
  }

  async findBySupplierId(supplierId: string): Promise<CommodityContract[]> {
    const contracts: CommodityContract[] = [];
    for (const contract of this.contracts.values()) {
      if (contract.supplierId === supplierId) {
        contracts.push(contract);
      }
    }
    return contracts.sort((a, b) => b.contractDate.getTime() - a.contractDate.getTime());
  }

  async findByStatus(status: CommodityContractStatus): Promise<CommodityContract[]> {
    const contracts: CommodityContract[] = [];
    for (const contract of this.contracts.values()) {
      if (contract.status === status) {
        contracts.push(contract);
      }
    }
    return contracts.sort((a, b) => b.contractDate.getTime() - a.contractDate.getTime());
  }

  async findExpiredContracts(): Promise<CommodityContract[]> {
    const contracts: CommodityContract[] = [];
    for (const contract of this.contracts.values()) {
      if (contract.isExpired()) {
        contracts.push(contract);
      }
    }
    return contracts.sort((a, b) => a.deliveryPeriodEnd.getTime() - b.deliveryPeriodEnd.getTime());
  }

  async findActiveContracts(): Promise<CommodityContract[]> {
    const contracts: CommodityContract[] = [];
    for (const contract of this.contracts.values()) {
      if (contract.status === 'ACTIVE') {
        contracts.push(contract);
      }
    }
    return contracts.sort((a, b) => a.deliveryPeriodStart.getTime() - b.deliveryPeriodStart.getTime());
  }

  async list(
    filter: CommodityContractFilter = {},
    sort: CommodityContractSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedCommodityContractResult> {
    let filteredContracts = Array.from(this.contracts.values());

    // Apply filters
    if (filter.contractNumber) {
      filteredContracts = filteredContracts.filter(contract => 
        contract.contractNumber.toLowerCase().includes(filter.contractNumber!.toLowerCase())
      );
    }

    if (filter.contractType) {
      filteredContracts = filteredContracts.filter(contract => contract.contractType === filter.contractType);
    }

    if (filter.supplierId) {
      filteredContracts = filteredContracts.filter(contract => contract.supplierId === filter.supplierId);
    }

    if (filter.status) {
      filteredContracts = filteredContracts.filter(contract => contract.status === filter.status);
    }

    if (filter.commodity) {
      filteredContracts = filteredContracts.filter(contract => 
        contract.items.some(item => item.commodity === filter.commodity)
      );
    }

    if (filter.contractDateFrom) {
      filteredContracts = filteredContracts.filter(contract => contract.contractDate >= filter.contractDateFrom!);
    }

    if (filter.contractDateTo) {
      filteredContracts = filteredContracts.filter(contract => contract.contractDate <= filter.contractDateTo!);
    }

    if (filter.deliveryPeriodStartFrom) {
      filteredContracts = filteredContracts.filter(contract => 
        contract.deliveryPeriodStart >= filter.deliveryPeriodStartFrom!
      );
    }

    if (filter.deliveryPeriodStartTo) {
      filteredContracts = filteredContracts.filter(contract => 
        contract.deliveryPeriodStart <= filter.deliveryPeriodStartTo!
      );
    }

    if (filter.deliveryPeriodEndFrom) {
      filteredContracts = filteredContracts.filter(contract => 
        contract.deliveryPeriodEnd >= filter.deliveryPeriodEndFrom!
      );
    }

    if (filter.deliveryPeriodEndTo) {
      filteredContracts = filteredContracts.filter(contract => 
        contract.deliveryPeriodEnd <= filter.deliveryPeriodEndTo!
      );
    }

    if (filter.expired === true) {
      filteredContracts = filteredContracts.filter(contract => contract.isExpired());
    }

    if (filter.search) {
      const searchLower = filter.search.toLowerCase();
      filteredContracts = filteredContracts.filter(contract => 
        contract.contractNumber.toLowerCase().includes(searchLower) ||
        (contract.notes && contract.notes.toLowerCase().includes(searchLower))
      );
    }

    // Apply sorting
    filteredContracts.sort((a, b) => {
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
        case 'contractDate':
          aValue = a.contractDate.getTime();
          bValue = b.contractDate.getTime();
          break;
        case 'deliveryPeriodStart':
          aValue = a.deliveryPeriodStart.getTime();
          bValue = b.deliveryPeriodStart.getTime();
          break;
        case 'deliveryPeriodEnd':
          aValue = a.deliveryPeriodEnd.getTime();
          bValue = b.deliveryPeriodEnd.getTime();
          break;
        case 'contractNumber':
          aValue = a.contractNumber;
          bValue = b.contractNumber;
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        case 'totalContractValue':
          aValue = a.totalContractValue;
          bValue = b.totalContractValue;
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
    const total = filteredContracts.length;
    const totalPages = Math.ceil(total / pageSize);
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const items = filteredContracts.slice(startIndex, endIndex);

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
    byStatus: Record<CommodityContractStatus, number>;
    byType: Record<ContractType, number>;
    totalContractValue: number;
    fulfilledValue: number;
    remainingValue: number;
    activeCount: number;
    expiredCount: number;
  }> {
    const allContracts = Array.from(this.contracts.values());
    const total = allContracts.length;

    const byStatus: Record<CommodityContractStatus, number> = {
      'DRAFT': 0,
      'NEGOTIATING': 0,
      'SIGNED': 0,
      'ACTIVE': 0,
      'FULFILLED': 0,
      'EXPIRED': 0,
      'CANCELLED': 0
    };

    const byType: Record<ContractType, number> = {
      'FORWARD': 0,
      'FUTURES': 0,
      'OPTION': 0
    };

    let totalContractValue = 0;
    let fulfilledValue = 0;
    let activeCount = 0;
    let expiredCount = 0;

    for (const contract of allContracts) {
      byStatus[contract.status]++;
      byType[contract.contractType]++;
      
      totalContractValue += contract.totalContractValue;
      fulfilledValue += contract.fulfilledValue;
      
      if (contract.status === 'ACTIVE') activeCount++;
      if (contract.isExpired()) expiredCount++;
    }

    return {
      total,
      byStatus,
      byType,
      totalContractValue,
      fulfilledValue,
      remainingValue: totalContractValue - fulfilledValue,
      activeCount,
      expiredCount
    };
  }

  async isContractNumberUnique(contractNumber: string, excludeId?: string): Promise<boolean> {
    for (const contract of this.contracts.values()) {
      if (contract.contractNumber === contractNumber && contract.id !== excludeId) {
        return false;
      }
    }
    return true;
  }
}
