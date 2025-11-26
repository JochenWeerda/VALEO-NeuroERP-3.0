/**
 * Commodity Contract Service
 * Complete Commodity Contract Management for Forward Contracts
 * Based on OCA purchase_agriculture Forward Contracts pattern
 */

import { CommodityContract, CommodityContractItem, CreateCommodityContractInput, UpdateCommodityContractInput, CommodityContractStatus } from '../entities/commodity-contract';
import { CommodityContractRepository, CommodityContractFilter, CommodityContractSort, PaginatedCommodityContractResult } from '../../infra/repositories/commodity-contract-repository';

export interface CommodityContractServiceDependencies {
  commodityContractRepository: CommodityContractRepository;
}

export class CommodityContractService {
  constructor(private deps: CommodityContractServiceDependencies) {}

  // ======================================
  // CORE CRUD OPERATIONS
  // ======================================

  async createCommodityContract(
    input: CreateCommodityContractInput,
    createdBy: string
  ): Promise<CommodityContract> {
    // Convert items to full CommodityContractItem objects
    const contractItems: CommodityContractItem[] = input.items.map(item => ({
      ...item,
      id: '', // Will be set by entity constructor
      fulfilledQuantity: 0,
      createdAt: new Date(),
      updatedAt: new Date()
    }));

    const contract = new CommodityContract(
      input.contractNumber,
      input.contractType,
      input.supplierId,
      contractItems,
      input.contractDate,
      input.deliveryPeriodStart,
      input.deliveryPeriodEnd,
      input.paymentTerms,
      input.currency,
      createdBy,
      {
        hedgingStrategy: input.hedgingStrategy,
        notes: input.notes
      }
    );

    return await this.deps.commodityContractRepository.create(contract);
  }

  async getCommodityContractById(id: string): Promise<CommodityContract | null> {
    return await this.deps.commodityContractRepository.findById(id);
  }

  async getCommodityContractByNumber(contractNumber: string): Promise<CommodityContract | null> {
    return await this.deps.commodityContractRepository.findByContractNumber(contractNumber);
  }

  async updateCommodityContract(
    id: string,
    updates: UpdateCommodityContractInput,
    updatedBy: string
  ): Promise<CommodityContract> {
    const contract = await this.getCommodityContractById(id);
    if (!contract) {
      throw new Error('Commodity contract not found');
    }

    contract.updateBasicInfo(updates, updatedBy);
    return await this.deps.commodityContractRepository.update(contract);
  }

  async deleteCommodityContract(id: string): Promise<boolean> {
    const contract = await this.getCommodityContractById(id);
    if (!contract) {
      return false;
    }

    if (!['DRAFT', 'CANCELLED'].includes(contract.status)) {
      throw new Error('Can only delete draft or cancelled contracts');
    }

    return await this.deps.commodityContractRepository.delete(id);
  }

  // ======================================
  // STATUS WORKFLOWS
  // ======================================

  async startNegotiation(contractId: string, updatedBy: string): Promise<CommodityContract> {
    const contract = await this.getCommodityContractById(contractId);
    if (!contract) {
      throw new Error('Commodity contract not found');
    }

    contract.startNegotiation(updatedBy);
    return await this.deps.commodityContractRepository.update(contract);
  }

  async signContract(contractId: string, signedBy: string): Promise<CommodityContract> {
    const contract = await this.getCommodityContractById(contractId);
    if (!contract) {
      throw new Error('Commodity contract not found');
    }

    contract.sign(signedBy);
    return await this.deps.commodityContractRepository.update(contract);
  }

  async activateContract(contractId: string, activatedBy: string): Promise<CommodityContract> {
    const contract = await this.getCommodityContractById(contractId);
    if (!contract) {
      throw new Error('Commodity contract not found');
    }

    contract.activate(activatedBy);
    return await this.deps.commodityContractRepository.update(contract);
  }

  async recordFulfillment(
    contractId: string,
    itemId: string,
    fulfilledQuantity: number,
    updatedBy: string
  ): Promise<CommodityContract> {
    const contract = await this.getCommodityContractById(contractId);
    if (!contract) {
      throw new Error('Commodity contract not found');
    }

    contract.recordFulfillment(itemId, fulfilledQuantity, updatedBy);
    return await this.deps.commodityContractRepository.update(contract);
  }

  async cancelContract(
    contractId: string,
    cancelledBy: string,
    reason: string
  ): Promise<CommodityContract> {
    const contract = await this.getCommodityContractById(contractId);
    if (!contract) {
      throw new Error('Commodity contract not found');
    }

    contract.cancel(cancelledBy, reason);
    return await this.deps.commodityContractRepository.update(contract);
  }

  // ======================================
  // ITEM MANAGEMENT
  // ======================================

  async addItemToContract(
    contractId: string,
    item: Omit<CommodityContractItem, 'id' | 'createdAt' | 'updatedAt' | 'fulfilledQuantity'>
  ): Promise<CommodityContract> {
    const contract = await this.getCommodityContractById(contractId);
    if (!contract) {
      throw new Error('Commodity contract not found');
    }

    contract.addItem(item);
    return await this.deps.commodityContractRepository.update(contract);
  }

  async updateContractItem(
    contractId: string,
    itemId: string,
    updates: Partial<Omit<CommodityContractItem, 'id' | 'createdAt' | 'updatedAt'>>
  ): Promise<CommodityContract> {
    const contract = await this.getCommodityContractById(contractId);
    if (!contract) {
      throw new Error('Commodity contract not found');
    }

    contract.updateItem(itemId, updates);
    return await this.deps.commodityContractRepository.update(contract);
  }

  async removeItemFromContract(
    contractId: string,
    itemId: string
  ): Promise<CommodityContract> {
    const contract = await this.getCommodityContractById(contractId);
    if (!contract) {
      throw new Error('Commodity contract not found');
    }

    contract.removeItem(itemId);
    return await this.deps.commodityContractRepository.update(contract);
  }

  // ======================================
  // QUERY METHODS
  // ======================================

  async listCommodityContracts(
    filter: CommodityContractFilter = {},
    sort: CommodityContractSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedCommodityContractResult> {
    return await this.deps.commodityContractRepository.list(filter, sort, page, pageSize);
  }

  async getCommodityContractsBySupplier(supplierId: string): Promise<CommodityContract[]> {
    return await this.deps.commodityContractRepository.findBySupplierId(supplierId);
  }

  async getCommodityContractsByStatus(status: CommodityContractStatus): Promise<CommodityContract[]> {
    return await this.deps.commodityContractRepository.findByStatus(status);
  }

  async getActiveContracts(): Promise<CommodityContract[]> {
    return await this.deps.commodityContractRepository.findActiveContracts();
  }

  async getExpiredContracts(): Promise<CommodityContract[]> {
    return await this.deps.commodityContractRepository.findExpiredContracts();
  }

  // ======================================
  // BUSINESS INTELLIGENCE & ANALYTICS
  // ======================================

  async getCommodityContractStatistics(): Promise<{
    total: number;
    byStatus: Record<CommodityContractStatus, number>;
    byType: Record<string, number>;
    totalContractValue: number;
    fulfilledValue: number;
    remainingValue: number;
    activeCount: number;
    expiredCount: number;
  }> {
    return await this.deps.commodityContractRepository.getStatistics();
  }
}
