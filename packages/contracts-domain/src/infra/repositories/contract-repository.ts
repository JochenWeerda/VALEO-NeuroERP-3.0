/**
 * Contract Repository
 * ISO 27001 Communications Security Compliant
 */

import { Contract, ContractStatus, ContractType, CommodityType } from '../../domain/entities/contract';
import { Amendment } from '../../domain/entities/amendment';
import { Fulfilment } from '../../domain/entities/fulfilment';
import { CallOff } from '../../domain/entities/call-off';

export interface ContractFilter {
  tenantId: string;
  type?: typeof ContractType.BUY | typeof ContractType.SELL;
  commodity?: typeof CommodityType.WHEAT | typeof CommodityType.BARLEY | typeof CommodityType.RAPESEED | typeof CommodityType.SOYMEAL | typeof CommodityType.COMPOUND_FEED | typeof CommodityType.FERTILIZER;
  counterpartyId?: string;
  status?: typeof ContractStatus.DRAFT | typeof ContractStatus.ACTIVE | typeof ContractStatus.PARTIALLY_FULFILLED | typeof ContractStatus.FULFILLED | typeof ContractStatus.CANCELLED | typeof ContractStatus.DEFAULTED;
  dateFrom?: Date;
  dateTo?: Date;
  deliveryFrom?: Date;
  deliveryTo?: Date;
}

export interface ContractSort {
  field: 'createdAt' | 'updatedAt' | 'contractNo' | 'deliveryWindow.from' | 'deliveryWindow.to';
  direction: 'asc' | 'desc';
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export class ContractRepository {
  private readonly tenantId: string;

  constructor(tenantId: string) {
    this.tenantId = tenantId;
  }

  private contracts: Map<string, Contract> = new Map();
  private amendments: Map<string, Amendment[]> = new Map();
  private fulfilments: Map<string, Fulfilment[]> = new Map();
  private callOffs: Map<string, CallOff[]> = new Map();

  /**
   * Create a new contract
   */
  async create(contract: Contract): Promise<Contract> {
    this.validateContract(contract);
    this.contracts.set(contract.id, contract);
    return contract;
  }

  /**
   * Update an existing contract
   */
  async update(id: string, contract: Contract): Promise<Contract> {
    if (!this.contracts.has(id)) {
      throw new Error(`Contract with id ${id} not found`);
    }

    this.validateContract(contract);
    this.contracts.set(id, contract);
    return contract;
  }

  /**
   * Find contract by ID
   */
  async findById(id: string, tenantId: string): Promise<Contract | null> {
    const contract = this.contracts.get(id);
    return contract && contract.tenantId === tenantId ? contract : null;
  }

  /**
   * Find contract by contract number
   */
  async findByContractNumber(contractNo: string, tenantId: string): Promise<Contract | null> {
    for (const contract of Array.from(this.contracts.values())) {
      if (contract.contractNo === contractNo && contract.tenantId === tenantId) {
        return contract;
      }
    }
    return null;
  }

  /**
   * Find contracts by counterparty ID
   */
  async findByCounterpartyId(counterpartyId: string, tenantId: string): Promise<Contract[]> {
    const result: Contract[] = [];
    for (const contract of Array.from(this.contracts.values())) {
      if (contract.counterpartyId === counterpartyId && contract.tenantId === tenantId) {
        result.push(contract);
      }
    }
    return result;
  }

  /**
   * Find contracts with filtering and pagination
   */
  async findMany(
    filter: ContractFilter,
    sort?: ContractSort,
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResult<Contract>> {
    let contracts = Array.from(this.contracts.values()).filter(c => c.tenantId === filter.tenantId);

    // Apply filters
    contracts = this.applyFilters(contracts, filter);

    // Apply sorting
    if (sort) {
      contracts = this.applySorting(contracts, sort);
    }

    // Apply pagination
    const total = contracts.length;
    const totalPages = Math.ceil(total / pageSize);
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const paginatedContracts = contracts.slice(startIndex, endIndex);

    return {
      items: paginatedContracts,
      total,
      page,
      pageSize,
      totalPages,
      hasNext: page < totalPages,
      hasPrev: page > 1
    };
  }

  /**
   * Find expired contracts
   */
  async findExpired(tenantId: string): Promise<Contract[]> {
    const now = new Date();
    const result: Contract[] = [];

    for (const contract of Array.from(this.contracts.values())) {
      if (contract.tenantId === tenantId && contract.isExpired()) {
        result.push(contract);
      }
    }

    return result;
  }

  /**
   * Find contracts requiring amendment approval
   */
  async findPendingAmendments(tenantId: string): Promise<Amendment[]> {
    const result: Amendment[] = [];

    for (const amendments of Array.from(this.amendments.values())) {
      for (const amendment of amendments) {
        if (amendment.tenantId === tenantId && amendment.status === 'Pending') {
          result.push(amendment);
        }
      }
    }

    return result;
  }

  /**
   * Delete contract by ID
   */
  async delete(id: string, tenantId: string): Promise<boolean> {
    const contract = this.contracts.get(id);
    if (!contract || contract.tenantId !== tenantId) {
      return false;
    }

    this.contracts.delete(id);
    this.amendments.delete(id);
    this.fulfilments.delete(id);
    this.callOffs.delete(id);
    return true;
  }

  /**
   * Get contract statistics
   */
  async getStatistics(tenantId: string): Promise<{
    total: number;
    byStatus: Record<string, number>;
    byType: Record<string, number>;
    byCommodity: Record<string, number>;
    totalValue: number;
    expiredCount: number;
    pendingAmendmentsCount: number;
  }> {
    const contracts = Array.from(this.contracts.values()).filter(c => c.tenantId === tenantId);

    const byStatus: Record<string, number> = {};
    const byType: Record<string, number> = {};
    const byCommodity: Record<string, number> = {};

    let totalValue = 0;
    let expiredCount = 0;
    let pendingAmendmentsCount = 0;

    for (const contract of contracts) {
      byStatus[contract.status] = (byStatus[contract.status] || 0) + 1;
      byType[contract.type] = (byType[contract.type] || 0) + 1;
      byCommodity[contract.commodity] = (byCommodity[contract.commodity] || 0) + 1;

      totalValue += contract.qty.contracted * 100; // Mock calculation

      if (contract.isExpired()) {
        expiredCount++;
      }
    }

    // Count pending amendments
    for (const amendments of Array.from(this.amendments.values())) {
      for (const amendment of amendments) {
        if (amendment.tenantId === tenantId && amendment.status === 'Pending') {
          pendingAmendmentsCount++;
        }
      }
    }

    return {
      total: contracts.length,
      byStatus,
      byType,
      byCommodity,
      totalValue,
      expiredCount,
      pendingAmendmentsCount
    };
  }

  /**
   * Check if contract exists
   */
  async exists(id: string, tenantId: string): Promise<boolean> {
    const contract = this.contracts.get(id);
    return contract !== undefined && contract.tenantId === tenantId;
  }

  // Amendment methods
  async createAmendment(amendment: Amendment): Promise<Amendment> {
    const contractAmendments = this.amendments.get(amendment.contractId) || [];
    contractAmendments.push(amendment);
    this.amendments.set(amendment.contractId, contractAmendments);
    return amendment;
  }

  async updateAmendment(amendmentId: string, amendment: Amendment): Promise<Amendment> {
    const contractAmendments = this.amendments.get(amendment.contractId) || [];
    const index = contractAmendments.findIndex(a => a.id === amendmentId);
    if (index === -1) {
      throw new Error('Amendment not found');
    }
    contractAmendments[index] = amendment;
    this.amendments.set(amendment.contractId, contractAmendments);
    return amendment;
  }

  async findAmendmentsByContractId(contractId: string, tenantId: string): Promise<Amendment[]> {
    const contract = this.contracts.get(contractId);
    if (!contract || contract.tenantId !== tenantId) {
      return [];
    }
    return this.amendments.get(contractId) || [];
  }

  // Fulfilment methods
  async createFulfilment(fulfilment: Fulfilment): Promise<Fulfilment> {
    const contractFulfilments = this.fulfilments.get(fulfilment.contractId) || [];
    contractFulfilments.push(fulfilment);
    this.fulfilments.set(fulfilment.contractId, contractFulfilments);
    return fulfilment;
  }

  async findFulfilmentsByContractId(contractId: string, tenantId: string): Promise<Fulfilment[]> {
    const contract = this.contracts.get(contractId);
    if (!contract || contract.tenantId !== tenantId) {
      return [];
    }
    return this.fulfilments.get(contractId) || [];
  }

  // Call-off methods
  async createCallOff(callOff: CallOff): Promise<CallOff> {
    const contractCallOffs = this.callOffs.get(callOff.contractId) || [];
    contractCallOffs.push(callOff);
    this.callOffs.set(callOff.contractId, contractCallOffs);
    return callOff;
  }

  async findCallOffsByContractId(contractId: string, tenantId: string): Promise<CallOff[]> {
    const contract = this.contracts.get(contractId);
    if (!contract || contract.tenantId !== tenantId) {
      return [];
    }
    return this.callOffs.get(contractId) || [];
  }

  private validateContract(contract: Contract): void {
    if (!contract.tenantId) {
      throw new Error('Tenant ID is required');
    }

    if (!contract.contractNo) {
      throw new Error('Contract number is required');
    }

    if (!contract.counterpartyId) {
      throw new Error('Counterparty ID is required');
    }

    if (!contract.deliveryWindow || !contract.deliveryWindow.from || !contract.deliveryWindow.to) {
      throw new Error('Delivery window is required');
    }

    if (contract.deliveryWindow.from >= contract.deliveryWindow.to) {
      throw new Error('Invalid delivery window');
    }

    if (!contract.qty || contract.qty.contracted <= 0) {
      throw new Error('Valid quantity is required');
    }
  }

  private applyFilters(contracts: Contract[], filter: ContractFilter): Contract[] {
    return contracts.filter(contract => {
      if (filter.type && contract.type !== filter.type) {
        return false;
      }

      if (filter.commodity && contract.commodity !== filter.commodity) {
        return false;
      }

      if (filter.counterpartyId && contract.counterpartyId !== filter.counterpartyId) {
        return false;
      }

      if (filter.status && contract.status !== filter.status) {
        return false;
      }

      if (filter.dateFrom && contract.createdAt < filter.dateFrom) {
        return false;
      }

      if (filter.dateTo && contract.createdAt > filter.dateTo) {
        return false;
      }

      if (filter.deliveryFrom && contract.deliveryWindow.from < filter.deliveryFrom) {
        return false;
      }

      if (filter.deliveryTo && contract.deliveryWindow.to > filter.deliveryTo) {
        return false;
      }

      return true;
    });
  }

  private applySorting(contracts: Contract[], sort: ContractSort): Contract[] {
    return contracts.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sort.field) {
        case 'createdAt':
          aValue = a.createdAt;
          bValue = b.createdAt;
          break;
        case 'updatedAt':
          aValue = a.updatedAt;
          bValue = b.updatedAt;
          break;
        case 'contractNo':
          aValue = a.contractNo;
          bValue = b.contractNo;
          break;
        case 'deliveryWindow.from':
          aValue = a.deliveryWindow.from;
          bValue = b.deliveryWindow.from;
          break;
        case 'deliveryWindow.to':
          aValue = a.deliveryWindow.to;
          bValue = b.deliveryWindow.to;
          break;
        default:
          return 0;
      }

      if (aValue < bValue) {
        return sort.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sort.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }
}