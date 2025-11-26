/**
 * Contract Service
 * ISO 27001 Communications Security Compliant
 * Contract Lifecycle Management Engine
 */

import { randomUUID } from 'crypto';
import { Contract, ContractEntity, ContractStatus, ContractType, CommodityType } from '../entities/contract';
import { Amendment, AmendmentEntity, AmendmentType, AmendmentStatus } from '../entities/amendment';
import { Fulfilment, FulfilmentEntity } from '../entities/fulfilment';
import { CallOff, CallOffEntity } from '../entities/call-off';

export interface CreateContractInput {
  tenantId: string;
  contractNo: string;
  type: typeof ContractType.BUY | typeof ContractType.SELL;
  commodity: typeof CommodityType.WHEAT | typeof CommodityType.BARLEY | typeof CommodityType.RAPESEED | typeof CommodityType.SOYMEAL | typeof CommodityType.COMPOUND_FEED | typeof CommodityType.FERTILIZER;
  counterpartyId: string;
  incoterm?: string;
  deliveryWindow: {
    from: Date;
    to: Date;
  };
  qty: {
    unit: 't' | 'mt';
    contracted: number;
    tolerance?: number;
  };
  pricing: {
    mode: string;
    referenceMarket?: 'CME' | 'EURONEXT' | 'CASH_INDEX';
    futuresMonth?: string;
    basis?: number;
    fees?: {
      elevator?: number;
      optionPremium?: number;
    };
    fx?: {
      pair: string;
      method: 'SPOT' | 'FIXING';
    };
  };
  delivery: {
    shipmentType: string;
    parity?: string;
    storage?: {
      allowed: boolean;
      tariff?: number;
      titleTransfer?: string;
    };
    qualitySpecs?: Record<string, any>;
  };
  createdBy: string;
}

export interface UpdateContractInput {
  incoterm?: string;
  deliveryWindow?: {
    from: Date;
    to: Date;
  };
  qty?: {
    unit: 't' | 'mt';
    contracted: number;
    tolerance?: number;
  };
  pricing?: Partial<CreateContractInput['pricing']>;
  delivery?: Partial<CreateContractInput['delivery']>;
}

export interface CreateAmendmentInput {
  contractId: string;
  tenantId: string;
  type: typeof AmendmentType.QTY_CHANGE | typeof AmendmentType.WINDOW_CHANGE | typeof AmendmentType.PRICE_RULE_CHANGE | typeof AmendmentType.COUNTERPARTY_CHANGE | typeof AmendmentType.DELIVERY_TERMS_CHANGE | typeof AmendmentType.OTHER;
  reason: string;
  changes: Record<string, any>;
  notes?: string;
  createdBy: string;
}

export interface ContractFilter {
  tenantId: string;
  type?: typeof ContractType.BUY | typeof ContractType.SELL;
  commodity?: typeof CommodityType.WHEAT | typeof CommodityType.BARLEY | typeof CommodityType.RAPESEED | typeof CommodityType.SOYMEAL | typeof CommodityType.COMPOUND_FEED | typeof CommodityType.FERTILIZER;
  counterpartyId?: string;
  status?: typeof ContractStatus.DRAFT | typeof ContractStatus.ACTIVE | typeof ContractStatus.PARTIALLY_FULFILLED | typeof ContractStatus.FULFILLED | typeof ContractStatus.CANCELLED | typeof ContractStatus.DEFAULTED;
  dateFrom?: Date;
  dateTo?: Date;
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
}

export class ContractService {
  constructor(
    private contractRepository: any, // Will be properly typed later
    private auditLogger?: any,
    private eventPublisher?: any,
    private documentService?: any // Document domain service
  ) {}


  private contractToRecord(contract: Contract): Record<string, any> {
    return {
      id: contract.id,
      contractNo: contract.contractNo,
      type: contract.type,
      commodity: contract.commodity,
      counterpartyId: contract.counterpartyId,
      status: contract.status,
      incoterm: contract.incoterm,
    };
  }

  // Helper method to get repository methods
  private getAmendmentRepository() {
    return this.contractRepository; // For now, use same repository
  }

  private getFulfilmentRepository() {
    return this.contractRepository; // For now, use same repository
  }

  /**
   * Generate contract document using document-domain
   */
  async generateContractDocument(
    contractId: string,
    templateKey: string = 'contract-template',
    userId: string,
    tenantId: string
  ): Promise<any> {
    const contract = await this.contractRepository.findById(contractId, tenantId);
    if (!contract) {
      throw new Error('Contract not found');
    }

    if (!this.documentService) {
      throw new Error('Document service not available');
    }

    // Prepare document payload
    const documentPayload = {
      contractId: contract.id,
      contractNo: contract.contractNo,
      type: contract.type,
      commodity: contract.commodity,
      counterpartyId: contract.counterpartyId,
      incoterm: contract.incoterm,
      deliveryWindow: contract.deliveryWindow,
      qty: contract.qty,
      pricing: contract.pricing,
      delivery: contract.delivery,
      status: contract.status,
      createdAt: contract.createdAt.toISOString(),
      updatedAt: contract.updatedAt.toISOString()
    };

    // Create document via document-domain
    const document = await this.documentService.createDocument(tenantId, {
      docType: 'certificate', // Using certificate as contract document type
      templateKey: templateKey,
      payload: documentPayload,
      locale: 'de-DE',
      options: {
        sign: 'timestamp',
        qr: true
      }
    }, userId);

    // Update contract with document reference
    contract.documentId = document.id;
    await this.contractRepository.update(contractId, contract);

    // Audit logging
    if (this.auditLogger) {
      await this.auditLogger.logSecureEvent('CONTRACT_DOCUMENT_GENERATED', {
        contractId,
        documentId: document.id,
        templateKey,
        userId
      }, tenantId, userId);
    }

    return document;
  }

  /**
   * Get contract document URL
   */
  async getContractDocumentUrl(
    contractId: string,
    tenantId: string
  ): Promise<string | null> {
    const contract = await this.contractRepository.findById(contractId, tenantId);
    if (!contract || !contract.documentId) {
      return null;
    }

    if (!this.documentService) {
      throw new Error('Document service not available');
    }

    return await this.documentService.getDocumentFileUrl(tenantId, contract.documentId);
  }

  /**
   * Creates a new contract with validation and business rules
   */
  async createContract(input: CreateContractInput): Promise<Contract> {
    // Validate business rules
    await this.validateContractCreation(input);

    // Generate contract number if not provided
    const contractNo = input.contractNo || await this.generateContractNumber(input.tenantId, input.type);

    const contractData: ContractEntity = {
      id: randomUUID(),
      tenantId: input.tenantId,
      contractNo,
      type: input.type,
      commodity: input.commodity,
      counterpartyId: input.counterpartyId,
      incoterm: input.incoterm,
      deliveryWindow: input.deliveryWindow,
      qty: input.qty,
      pricing: input.pricing as any,
      delivery: input.delivery as any,
      status: ContractStatus.DRAFT,
      createdAt: new Date(),
      updatedAt: new Date(),
      version: 1
    };

      const contract = new Contract(contractData);
      const savedContract = await this.contractRepository.create(contract);

      // Audit logging
      if (this.auditLogger) {
        await this.auditLogger.logSecureEvent('CONTRACT_CREATED', {
          contractId: savedContract.id,
          contractNo: savedContract.contractNo,
          type: savedContract.type,
          commodity: savedContract.commodity,
          counterpartyId: savedContract.counterpartyId,
          quantity: savedContract.qty.contracted,
          value: await this.calculateContractValue(savedContract)
        }, input.tenantId, input.createdBy);
      }


    // Publish event
    if (this.eventPublisher) {
      const event = {
        eventId: `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        eventType: 'contract.created',
        aggregateId: savedContract.id,
        tenantId: input.tenantId,
        timestamp: new Date(),
        actor: { userId: input.createdBy },
        payload: {
          contractNo: savedContract.contractNo,
          type: savedContract.type,
          commodity: savedContract.commodity,
          counterpartyId: savedContract.counterpartyId,
          quantity: savedContract.qty.contracted,
          deliveryWindow: savedContract.deliveryWindow
        },
        metadata: { version: 1, source: 'contracts-domain' }
      };
      await this.eventPublisher.publish(event);
    }

    return savedContract;
  }

  /**
   * Activates a contract after approval
   */
  async activateContract(contractId: string, activatedBy: string, tenantId: string): Promise<Contract> {
    const contract = await this.contractRepository.findById(contractId, tenantId);

    if (!contract) {
      throw new Error('Contract not found');
    }

    if (contract.status !== ContractStatus.DRAFT) {
      throw new Error('Only draft contracts can be activated');
    }

    contract.activate();
    const savedContract = await this.contractRepository.update(contractId, contract);

    // Audit logging
    if (this.auditLogger) {
      await this.auditLogger.logSecureEvent('CONTRACT_ACTIVATED', {
        contractId: savedContract.id,
        contractNo: savedContract.contractNo,
        activatedBy
      }, tenantId, activatedBy);
    }

    // Publish event
    if (this.eventPublisher) {
      const event = {
        eventId: `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        eventType: 'contract.activated',
        aggregateId: savedContract.id,
        tenantId,
        timestamp: new Date(),
        actor: { userId: activatedBy },
        payload: {
          contractNo: savedContract.contractNo,
          type: savedContract.type,
          commodity: savedContract.commodity,
          quantity: savedContract.qty.contracted
        },
        metadata: { version: 1, source: 'contracts-domain' }
      };
      await this.eventPublisher.publish(event);
    }

    return savedContract;
  }

  /**
   * Cancels a contract
   */
  async cancelContract(
    contractId: string,
    cancelledBy: string,
    tenantId: string,
    reason: string,
    options?: { userName?: string; userEmail?: string; ipAddress?: string; userAgent?: string }
  ): Promise<Contract> {
      const contract = await this.contractRepository.findById(contractId, tenantId);

      if (!contract) {
        throw new Error('Contract not found');
      }

      if (!reason || reason.trim().length < 10) {
        throw new Error('Cancel reason is required and must be at least 10 characters');
      }

      const oldValue = this.contractToRecord(contract);
      contract.cancel();
      const savedContract = await this.contractRepository.update(contractId, contract);

      // Audit logging
      if (this.auditLogger) {
        await this.auditLogger.logSecureEvent('CONTRACT_CANCELLED', {
          contractId: savedContract.id,
          contractNo: savedContract.contractNo,
          cancelledBy,
          reason
        }, tenantId, cancelledBy);
      }


    // Publish event
    if (this.eventPublisher) {
      const event = {
        eventId: `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        eventType: 'contract.cancelled',
        aggregateId: savedContract.id,
        tenantId,
        timestamp: new Date(),
        actor: { userId: cancelledBy },
        payload: {
          contractNo: savedContract.contractNo,
          reason
        },
        metadata: { version: 1, source: 'contracts-domain' }
      };
      await this.eventPublisher.publish(event);
    }

    return savedContract;
  }

  /**
   * Creates a contract amendment
   */
  async createAmendment(input: CreateAmendmentInput): Promise<Amendment> {
    // Validate that contract exists and can be amended
    const contract = await this.contractRepository.findById(input.contractId, input.tenantId);
    if (!contract) {
      throw new Error('Contract not found');
    }

    if (!contract.canBeAmended()) {
      throw new Error('Contract cannot be amended in current status');
    }

    const amendmentData: AmendmentEntity = {
      id: randomUUID(),
      contractId: input.contractId,
      tenantId: input.tenantId,
      type: input.type,
      reason: input.reason,
      changes: input.changes,
      status: AmendmentStatus.PENDING,
      notes: input.notes,
      createdAt: new Date(),
      updatedAt: new Date(),
      version: 1
    };

      const amendment = new Amendment(amendmentData);
      const savedAmendment = await this.getAmendmentRepository().createAmendment(amendment);

      // Get contract for change log
      const contractForLog = await this.contractRepository.findById(input.contractId, input.tenantId);
      const oldValue = contractForLog ? this.contractToRecord(contractForLog) : {};
      const newValue = contractForLog ? this.contractToRecord(contractForLog) : {};


      // Audit logging
      if (this.auditLogger) {
        await this.auditLogger.logSecureEvent('AMENDMENT_CREATED', {
        amendmentId: savedAmendment.id,
        contractId: savedAmendment.contractId,
        type: savedAmendment.type,
        reason: savedAmendment.reason
      }, input.tenantId, input.createdBy);
    }

    // Publish amendment event
    if (this.eventPublisher) {
      const event = {
        eventId: `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        eventType: 'contract.amendment.created',
        aggregateId: savedAmendment.contractId,
        tenantId: input.tenantId,
        timestamp: new Date(),
        actor: { userId: input.createdBy },
        payload: {
          amendmentId: savedAmendment.id,
          amendmentType: savedAmendment.type,
          reason: savedAmendment.reason,
          changes: savedAmendment.changes,
          status: savedAmendment.status
        },
        metadata: { version: 1, source: 'contracts-domain' }
      };
      await this.eventPublisher.publish(event);
    }

    return savedAmendment;
  }

  /**
   * Approves a contract amendment
   */
  async approveAmendment(amendmentId: string, approvedBy: string, tenantId: string): Promise<Amendment> {
    const amendment = await this.getAmendmentRepository().findAmendmentsByContractId(amendmentId, tenantId).then((amendments: Amendment[]) => amendments.find((a: Amendment) => a.id === amendmentId));

    if (!amendment) {
      throw new Error('Amendment not found');
    }

    amendment.approve(approvedBy);
    const savedAmendment = await this.getAmendmentRepository().updateAmendment(amendmentId, amendment);

    // Apply changes to contract
    await this.applyAmendmentToContract(savedAmendment);

    // Audit logging
    if (this.auditLogger) {
      await this.auditLogger.logSecureEvent('AMENDMENT_APPROVED', {
        amendmentId: savedAmendment.id,
        contractId: savedAmendment.contractId,
        approvedBy
      }, tenantId, approvedBy);
    }

    // Publish amendment approval event
    if (this.eventPublisher) {
      const event = {
        eventId: `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        eventType: 'contract.amendment.approved',
        aggregateId: savedAmendment.contractId,
        tenantId,
        timestamp: new Date(),
        actor: { userId: approvedBy },
        payload: {
          amendmentId: savedAmendment.id,
          amendmentType: savedAmendment.type,
          approvedBy,
          changes: savedAmendment.changes
        },
        metadata: { version: 1, source: 'contracts-domain' }
      };
      await this.eventPublisher.publish(event);
    }

    return savedAmendment;
  }

  /**
   * Publishes delayed delivery alerts
   */
  async publishDelayedDeliveryAlerts(tenantId: string): Promise<void> {
    if (!this.eventPublisher) return;

    // Get all contracts with pending deliveries
    const contracts = await this.contractRepository.findMany({ tenantId, status: 'ACTIVE' }, undefined, 1, 1000);

    for (const contract of contracts.items) {
      const fulfilments = await this.getContractFulfilments(contract.id, tenantId);
      const fulfilment = fulfilments[0];

      if (fulfilment) {
        const delayedDeliveries = fulfilment.getDelayedDeliveries();

        for (const delay of delayedDeliveries) {
          const event = {
            eventId: `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            eventType: 'contract.delivery.delayed',
            aggregateId: contract.id,
            tenantId,
            timestamp: new Date(),
            actor: { userId: 'system' },
            payload: {
              contractNo: contract.contractNo,
              plannedDate: delay.plannedDate.toISOString(),
              delayDays: delay.delayDays,
              remainingQty: fulfilment.openQty
            },
            metadata: { version: 1, source: 'contracts-domain', severity: 'warning' }
          };
          await this.eventPublisher.publish(event);
        }
      }
    }
  }

  /**
   * Publishes contract status change events
   */
  private async publishContractStatusChange(
    contract: Contract,
    previousStatus: string,
    userId: string,
    tenantId: string,
    reason?: string
  ): Promise<void> {
    if (!this.eventPublisher || contract.status === previousStatus) return;

    const eventType = `contract.${contract.status.toLowerCase()}`;

    const event = {
      eventId: `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      eventType,
      aggregateId: contract.id,
      tenantId,
      timestamp: new Date(),
      actor: { userId },
      payload: {
        contractNo: contract.contractNo,
        previousStatus,
        newStatus: contract.status,
        reason,
        commodity: contract.commodity,
        counterpartyId: contract.counterpartyId,
        quantity: contract.qty.contracted
      },
      metadata: { version: 1, source: 'contracts-domain' }
    };

    await this.eventPublisher.publish(event);
  }

  /**
   * Gets contracts with filtering and pagination
   */
  async getContracts(
    filter: ContractFilter,
    sort?: ContractSort,
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResult<Contract>> {
    return this.contractRepository.findMany(filter, sort, page, pageSize);
  }

  /**
   * Gets a specific contract by ID
   */
  async getContractById(contractId: string, tenantId: string): Promise<Contract | null> {
    return this.contractRepository.findById(contractId, tenantId);
  }

  /**
   * Gets amendments for a contract
   */
  async getContractAmendments(contractId: string, tenantId: string): Promise<Amendment[]> {
    return this.getAmendmentRepository().findAmendmentsByContractId(contractId, tenantId);
  }

  /**
   * Gets fulfilments for a contract
   */
  async getContractFulfilments(contractId: string, tenantId: string): Promise<Fulfilment[]> {
    return this.getFulfilmentRepository().findFulfilmentsByContractId(contractId, tenantId);
  }

  /**
   * Records a delivery against a contract
   */
  async recordDelivery(
    contractId: string,
    deliveryData: {
      qty: number;
      deliveryNote?: string;
      batchNumbers?: string[];
      storageLocation?: string;
      qualityData?: {
        score?: number;
        issues?: string[];
      };
    },
    userId: string,
    tenantId: string
  ): Promise<Fulfilment> {
    const contract = await this.contractRepository.findById(contractId, tenantId);
    if (!contract) {
      throw new Error('Contract not found');
    }

    if (contract.status !== ContractStatus.ACTIVE && contract.status !== ContractStatus.PARTIALLY_FULFILLED) {
      throw new Error('Contract must be active to record deliveries');
    }

    // Get or create fulfilment record
    let fulfilments = await this.getContractFulfilments(contractId, tenantId);
    let fulfilment = fulfilments[0];

    if (!fulfilment) {
      // Create new fulfilment record
      const fulfilmentData: FulfilmentEntity = {
        contractId,
        tenantId,
        deliveredQty: 0,
        pricedQty: 0,
        invoicedQty: 0,
        openQty: contract.qty.contracted,
        deliverySchedule: [],
        timeline: [],
        lastUpdated: new Date()
      };
      fulfilment = new Fulfilment(fulfilmentData);
    }

    // Record the delivery
    const deliveryInfo: any = {};
    if (deliveryData.deliveryNote) deliveryInfo.deliveryNote = deliveryData.deliveryNote;
    if (deliveryData.batchNumbers) deliveryInfo.batchNumbers = deliveryData.batchNumbers;
    if (deliveryData.storageLocation) deliveryInfo.storageLocation = deliveryData.storageLocation;
    if (deliveryData.qualityData) deliveryInfo.qualityData = deliveryData.qualityData;

    fulfilment.addDelivery(deliveryData.qty, deliveryInfo);

    // Update contract status if fully fulfilled
    const previousStatus = contract.status;
    if (fulfilment.isFullyFulfilled()) {
      contract.status = ContractStatus.FULFILLED;
      await this.contractRepository.update(contractId, contract);
      await this.publishContractStatusChange(contract, previousStatus, userId, tenantId, 'Fully fulfilled');
    } else if (contract.status === ContractStatus.ACTIVE) {
      contract.status = ContractStatus.PARTIALLY_FULFILLED;
      await this.contractRepository.update(contractId, contract);
      await this.publishContractStatusChange(contract, previousStatus, userId, tenantId, 'Partially fulfilled');
    }

    // Save fulfilment
    await this.getFulfilmentRepository().updateFulfilment(fulfilment.contractId, fulfilment);

    // Audit logging
    if (this.auditLogger) {
      await this.auditLogger.logSecureEvent('DELIVERY_RECORDED', {
        contractId,
        deliveryQty: deliveryData.qty,
        remainingQty: fulfilment.openQty,
        fullyFulfilled: fulfilment.isFullyFulfilled(),
        userId
      }, tenantId, userId);
    }

    return fulfilment;
  }

  /**
   * Records a delivery and publishes fulfilment events
   */
  async recordDeliveryWithEvents(
    contractId: string,
    deliveryData: {
      qty: number;
      deliveryNote?: string;
      batchNumbers?: string[];
      storageLocation?: string;
      qualityData?: {
        score?: number;
        issues?: string[];
      };
    },
    userId: string,
    tenantId: string
  ): Promise<Fulfilment> {
    const fulfilment = await this.recordDelivery(contractId, deliveryData, userId, tenantId);

    // Publish delivery event
    if (this.eventPublisher) {
      const event = {
        eventId: `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        eventType: 'contract.delivery.recorded',
        aggregateId: contractId,
        tenantId,
        timestamp: new Date(),
        actor: { userId },
        payload: {
          deliveryQty: deliveryData.qty,
          remainingQty: fulfilment.openQty,
          fullyFulfilled: fulfilment.isFullyFulfilled(),
          qualityScore: deliveryData.qualityData?.score,
          batchNumbers: deliveryData.batchNumbers,
          storageLocation: deliveryData.storageLocation
        },
        metadata: { version: 1, source: 'contracts-domain' }
      };
      await this.eventPublisher.publish(event);

      // Publish contract status change if fully fulfilled
      if (fulfilment.isFullyFulfilled()) {
        const contractFulfilledEvent = {
          eventId: `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          eventType: 'contract.fulfilled',
          aggregateId: contractId,
          tenantId,
          timestamp: new Date(),
          actor: { userId },
          payload: {
            totalDelivered: fulfilment.deliveredQty,
            fulfilmentRate: fulfilment.getFulfilmentSummary().fulfilmentRate,
            qualityScore: fulfilment.qualityScore
          },
          metadata: { version: 1, source: 'contracts-domain' }
        };
        await this.eventPublisher.publish(contractFulfilledEvent);
      }
    }

    return fulfilment;
  }

  /**
   * Adds a delivery schedule item to a contract
   */
  async addDeliverySchedule(
    contractId: string,
    scheduleItem: {
      plannedDate: Date;
      qty: number;
    },
    userId: string,
    tenantId: string
  ): Promise<Fulfilment> {
    // Get or create fulfilment record
    let fulfilments = await this.getContractFulfilments(contractId, tenantId);
    let fulfilment = fulfilments[0];

    if (!fulfilment) {
      const contract = await this.contractRepository.findById(contractId, tenantId);
      if (!contract) {
        throw new Error('Contract not found');
      }

      const fulfilmentData: FulfilmentEntity = {
        contractId,
        tenantId,
        deliveredQty: 0,
        pricedQty: 0,
        invoicedQty: 0,
        openQty: contract.qty.contracted,
        deliverySchedule: [],
        timeline: [],
        lastUpdated: new Date()
      };
      fulfilment = new Fulfilment(fulfilmentData);
    }

    fulfilment.addDeliveryScheduleItem(scheduleItem.plannedDate, scheduleItem.qty);
    await this.getFulfilmentRepository().updateFulfilment(fulfilment.contractId, fulfilment);

    return fulfilment;
  }

  /**
   * Gets contract fulfilment summary
   */
  async getContractFulfilmentSummary(contractId: string, tenantId: string): Promise<any> {
    const fulfilments = await this.getContractFulfilments(contractId, tenantId);
    const fulfilment = fulfilments[0];

    if (!fulfilment) {
      return null;
    }

    return {
      summary: fulfilment.getFulfilmentSummary(),
      delayedDeliveries: fulfilment.getDelayedDeliveries(),
      upcomingDeliveries: fulfilment.getUpcomingDeliveries(),
      timeline: fulfilment.timeline.slice(-10) // Last 10 events
    };
  }

  /**
   * Updates a contract
   */
  async updateContract(
    contractId: string,
    updates: any,
    updatedBy: string,
    options?: { reason?: string; userName?: string; userEmail?: string; ipAddress?: string; userAgent?: string }
  ): Promise<Contract> {
      const contract = await this.contractRepository.findById(contractId, updates.tenantId || 'default-tenant');
      if (!contract) {
        throw new Error('Contract not found');
      }

      const oldValue = this.contractToRecord(contract);
      // Apply updates
      Object.assign(contract, updates);
      contract.updatedAt = new Date();
      contract.version++;

      const savedContract = await this.contractRepository.update(contractId, contract);


      return savedContract;
    }

  /**
   * Deletes a contract
   */
  async deleteContract(
    contractId: string,
    tenantId: string,
    reason: string,
    deletedBy: string,
    options?: { userName?: string; userEmail?: string; ipAddress?: string; userAgent?: string }
  ): Promise<boolean> {
      const contract = await this.contractRepository.findById(contractId, tenantId);
      if (!contract) {
        throw new Error('Contract not found');
      }

      if (!reason || reason.trim().length < 10) {
        throw new Error('Delete reason is required and must be at least 10 characters');
      }

      const oldValue = this.contractToRecord(contract);


      return this.contractRepository.delete(contractId, tenantId);
    }


  // Private helper methods

  private async validateContractCreation(input: CreateContractInput): Promise<void> {
    // Validate counterparty exists
    const counterpartyExists = await this.validateCounterparty(input.counterpartyId, input.tenantId);
    if (!counterpartyExists) {
      throw new Error('Invalid counterparty');
    }

    // Validate delivery window
    if (input.deliveryWindow.from >= input.deliveryWindow.to) {
      throw new Error('Invalid delivery window');
    }

    // Validate quantity
    if (input.qty.contracted <= 0) {
      throw new Error('Contracted quantity must be positive');
    }

    // Validate pricing
    await this.validatePricing(input.pricing);
  }

  private async generateContractNumber(tenantId: string, type: string): Promise<string> {
    const year = new Date().getFullYear();
    const prefix = type === ContractType.BUY ? 'BUY' : 'SELL';
    const sequence = await this.getNextContractSequence(tenantId, year);
    return `${prefix}-${year}-${sequence.toString().padStart(4, '0')}`;
  }

  private async calculateContractValue(contract: Contract): Promise<number> {
    // Simplified calculation - would integrate with pricing service
    return contract.qty.contracted * 100; // Mock value
  }

  private async validateCounterparty(counterpartyId: string, tenantId: string): Promise<boolean> {
    // Would validate against CRM or counterparty service
    return true; // Mock validation
  }

  private async validatePricing(pricing: any): Promise<void> {
    // Would validate pricing rules and market data
    if (!pricing.mode) {
      throw new Error('Pricing mode is required');
    }
  }

  private async getNextContractSequence(tenantId: string, year: number): Promise<number> {
    // Would query database for next sequence number
    return Math.floor(Math.random() * 1000) + 1; // Mock sequence
  }

  private async applyAmendmentToContract(amendment: Amendment): Promise<void> {
    const contract = await this.contractRepository.findById(amendment.contractId, amendment.tenantId);
    if (!contract) return;

    // Apply changes based on amendment type
    switch (amendment.type) {
      case AmendmentType.QTY_CHANGE:
        if (amendment.changes.qty) {
          contract.qty = { ...contract.qty, ...amendment.changes.qty };
        }
        break;
      case AmendmentType.WINDOW_CHANGE:
        if (amendment.changes.deliveryWindow) {
          contract.deliveryWindow = amendment.changes.deliveryWindow;
        }
        break;
      // Add other amendment types...
    }

    contract.updatedAt = new Date();
    contract.version++;
    await this.contractRepository.update(contract.id, contract);
  }
}