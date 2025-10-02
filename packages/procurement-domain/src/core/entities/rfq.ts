import { randomUUID } from 'crypto';

export type RfqId = string & { readonly __brand: 'RfqId' };
export type BidId = string & { readonly __brand: 'BidId' };

export enum RfqStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  BIDDING_OPEN = 'bidding_open',
  BIDDING_CLOSED = 'bidding_closed',
  EVALUATION = 'evaluation',
  AWARDED = 'awarded',
  CANCELLED = 'cancelled',
  EXPIRED = 'expired'
}

export enum BidStatus {
  SUBMITTED = 'submitted',
  UNDER_REVIEW = 'under_review',
  ACCEPTED = 'accepted',
  REJECTED = 'rejected',
  WITHDRAWN = 'withdrawn'
}

export enum AwardStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  CONTRACT_SIGNED = 'contract_signed'
}

export interface RfqItem {
  id: string;
  sku: string;
  name: string;
  description: string;
  quantity: number;
  uom: string;
  specifications: Record<string, any>;
  category: string;
  estimatedValue?: number;
  requiredDeliveryDate?: Date;
  alternatives?: string[]; // Alternative SKUs
}

export interface RfqInvitation {
  supplierId: string;
  invitedAt: Date;
  respondedAt?: Date;
  responseStatus: 'pending' | 'accepted' | 'declined' | 'no_response';
  invitationMethod: 'email' | 'portal' | 'api';
}

export interface BidItem {
  rfqItemId: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  currency: string;
  deliveryDate: Date;
  leadTime: number; // days
  notes?: string;
  alternatives?: Array<{
    sku: string;
    unitPrice: number;
    notes: string;
  }>;
}

export interface BidTerms {
  paymentTerms: string;
  deliveryTerms: string;
  warranty: string;
  validityPeriod: number; // days
  minimumOrderQuantity?: number;
  packaging?: string;
  shipping?: string;
  insurance?: string;
}

export class Bid {
  public readonly id: BidId;
  public readonly rfqId: RfqId;
  public readonly supplierId: string;
  public status: BidStatus;
  public items: BidItem[];
  public terms: BidTerms;
  public totalValue: number;
  public currency: string;
  public submittedBy: string;
  public readonly submittedAt: Date;
  public evaluatedAt?: Date;
  public evaluationScore?: number;
  public evaluationNotes: string | undefined;
  public attachments: string[]; // File references
  public readonly createdAt: Date;
  public updatedAt: Date;

  constructor(props: {
    id?: BidId;
    rfqId: RfqId;
    supplierId: string;
    items: BidItem[];
    terms: BidTerms;
    totalValue: number;
    currency: string;
    submittedBy: string;
    attachments?: string[];
  }) {
    this.id = props.id || (randomUUID() as BidId);
    this.rfqId = props.rfqId;
    this.supplierId = props.supplierId;
    this.status = BidStatus.SUBMITTED;
    this.items = props.items;
    this.terms = props.terms;
    this.totalValue = props.totalValue;
    this.currency = props.currency;
    this.submittedBy = props.submittedBy;
    this.submittedAt = new Date();
    this.attachments = props.attachments || [];
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }

  public evaluate(score: number, notes?: string): void {
    this.status = BidStatus.UNDER_REVIEW;
    this.evaluationScore = score;
    this.evaluationNotes = notes;
    this.evaluatedAt = new Date();
    this.updatedAt = new Date();
  }

  public accept(): void {
    this.status = BidStatus.ACCEPTED;
    this.updatedAt = new Date();
  }

  public reject(): void {
    this.status = BidStatus.REJECTED;
    this.updatedAt = new Date();
  }

  public withdraw(): void {
    this.status = BidStatus.WITHDRAWN;
    this.updatedAt = new Date();
  }

  public isValid(): boolean {
    return new Date() < new Date(this.submittedAt.getTime() + this.terms.validityPeriod * 24 * 60 * 60 * 1000);
  }

  public getDaysUntilExpiry(): number {
    const expiryDate = new Date(this.submittedAt.getTime() + this.terms.validityPeriod * 24 * 60 * 60 * 1000);
    return Math.ceil((expiryDate.getTime() - Date.now()) / (24 * 60 * 60 * 1000));
  }
}

export interface AwardRecommendation {
  bidId: BidId;
  supplierId: string;
  recommendationReason: string;
  confidence: number;
  totalAwardValue: number;
  items: Array<{
    rfqItemId: string;
    awardedQuantity: number;
    awardedPrice: number;
    reason: string;
  }>;
  risks: string[];
  benefits: string[];
}

export class Award {
  public readonly id: string;
  public readonly rfqId: RfqId;
  public status: AwardStatus;
  public awardedTo: string; // supplierId
  public totalAwardedValue: number;
  public currency: string;
  public awardedBy: string;
  public readonly awardedAt: Date;
  public approvedBy?: string;
  public approvedAt?: Date;
  public rejectionReason?: string;
  public contractId?: string;
  public items: Array<{
    rfqItemId: string;
    bidId: BidId;
    awardedQuantity: number;
    awardedPrice: number;
    deliveryDate: Date;
  }>;
  public readonly createdAt: Date;
  public updatedAt: Date;

  constructor(props: {
    rfqId: RfqId;
    awardedTo: string;
    totalAwardedValue: number;
    currency: string;
    awardedBy: string;
    items: Array<{
      rfqItemId: string;
      bidId: BidId;
      awardedQuantity: number;
      awardedPrice: number;
      deliveryDate: Date;
    }>;
  }) {
    this.id = randomUUID();
    this.rfqId = props.rfqId;
    this.status = AwardStatus.PENDING;
    this.awardedTo = props.awardedTo;
    this.totalAwardedValue = props.totalAwardedValue;
    this.currency = props.currency;
    this.awardedBy = props.awardedBy;
    this.awardedAt = new Date();
    this.items = props.items;
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }

  public approve(approvedBy: string): void {
    this.status = AwardStatus.APPROVED;
    this.approvedBy = approvedBy;
    this.approvedAt = new Date();
    this.updatedAt = new Date();
  }

  public reject(rejectionReason: string): void {
    this.status = AwardStatus.REJECTED;
    this.rejectionReason = rejectionReason;
    this.updatedAt = new Date();
  }

  public signContract(contractId: string): void {
    this.status = AwardStatus.CONTRACT_SIGNED;
    this.contractId = contractId;
    this.updatedAt = new Date();
  }
}

export class Rfq {
  public readonly id: RfqId;
  public title: string;
  public description: string;
  public category: string;
  public status: RfqStatus;
  public type: 'rfq' | 'rfp' | 'rfq' | 'auction';

  // Scope and Requirements
  public items: RfqItem[];
  public totalEstimatedValue: number;
  public currency: string;

  // Timeline
  public biddingStartDate: Date;
  public biddingEndDate: Date;
  public evaluationDeadline?: Date;
  public awardDeadline?: Date;

  // Participants
  public createdBy: string;
  public invitedSuppliers: RfqInvitation[];
  public bids: Bid[];
  public awardDecision: Award | undefined;

  // Evaluation
  public evaluationCriteria: Array<{
    criterion: string;
    weight: number;
    description: string;
  }>;

  // Metadata
  public tenantId: string;
  public department: string | undefined;
  public costCenter: string | undefined;
  public project: string | undefined;
  public priority: 'low' | 'medium' | 'high' | 'critical';

  // System
  public readonly createdAt: Date;
  public updatedAt: Date;
  public publishedAt?: Date;
  public closedAt?: Date;

  constructor(props: {
    id?: RfqId;
    title: string;
    description: string;
    category: string;
    items: RfqItem[];
    totalEstimatedValue: number;
    currency: string;
    biddingStartDate: Date;
    biddingEndDate: Date;
    createdBy: string;
    tenantId: string;
    type?: 'rfq' | 'rfp' | 'rfq' | 'auction';
    department?: string;
    costCenter?: string;
    project?: string;
    priority?: 'low' | 'medium' | 'high' | 'critical';
    evaluationCriteria?: Array<{
      criterion: string;
      weight: number;
      description: string;
    }>;
  }) {
    this.id = props.id || (randomUUID() as RfqId);
    this.title = props.title;
    this.description = props.description;
    this.category = props.category;
    this.status = RfqStatus.DRAFT;
    this.type = props.type || 'rfq';
    this.items = props.items;
    this.totalEstimatedValue = props.totalEstimatedValue;
    this.currency = props.currency;
    this.biddingStartDate = props.biddingStartDate;
    this.biddingEndDate = props.biddingEndDate;
    this.createdBy = props.createdBy;
    this.invitedSuppliers = [];
    this.bids = [];
    this.tenantId = props.tenantId;
    this.department = props.department;
    this.costCenter = props.costCenter;
    this.project = props.project;
    this.priority = props.priority || 'medium';
    this.evaluationCriteria = props.evaluationCriteria || this.getDefaultEvaluationCriteria();
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }

  // Business Logic Methods
  public publish(): void {
    if (this.status !== RfqStatus.DRAFT) {
      throw new Error('Only draft RFQs can be published');
    }
    if (this.invitedSuppliers.length === 0) {
      throw new Error('At least one supplier must be invited before publishing');
    }
    if (this.items.length === 0) {
      throw new Error('RFQ must have at least one item');
    }

    this.status = RfqStatus.PUBLISHED;
    this.publishedAt = new Date();
    this.updatedAt = new Date();
  }

  public openBidding(): void {
    if (this.status !== RfqStatus.PUBLISHED) {
      throw new Error('RFQ must be published before opening bidding');
    }
    if (new Date() < this.biddingStartDate) {
      throw new Error('Cannot open bidding before start date');
    }

    this.status = RfqStatus.BIDDING_OPEN;
    this.updatedAt = new Date();
  }

  public closeBidding(): void {
    if (this.status !== RfqStatus.BIDDING_OPEN) {
      throw new Error('Bidding must be open to close it');
    }

    this.status = RfqStatus.BIDDING_CLOSED;
    this.closedAt = new Date();
    this.updatedAt = new Date();
  }

  public startEvaluation(): void {
    if (this.status !== RfqStatus.BIDDING_CLOSED) {
      throw new Error('Bidding must be closed before evaluation');
    }

    this.status = RfqStatus.EVALUATION;
    this.updatedAt = new Date();
  }

  public makeAward(award: Award): void {
    if (this.status !== RfqStatus.EVALUATION) {
      throw new Error('RFQ must be in evaluation status to award');
    }

    this.awardDecision = award;
    this.status = RfqStatus.AWARDED;
    this.updatedAt = new Date();
  }

  public cancel(reason?: string): void {
    if (this.status === RfqStatus.AWARDED || this.status === RfqStatus.CANCELLED) {
      throw new Error('Cannot cancel awarded or already cancelled RFQ');
    }

    this.status = RfqStatus.CANCELLED;
    this.updatedAt = new Date();
    // TODO: Add cancellation reason tracking
  }

  // Supplier Management
  public inviteSupplier(supplierId: string, method: 'email' | 'portal' | 'api' = 'email'): void {
    const existingInvitation = this.invitedSuppliers.find(inv => inv.supplierId === supplierId);
    if (existingInvitation) {
      throw new Error('Supplier already invited');
    }

    this.invitedSuppliers.push({
      supplierId,
      invitedAt: new Date(),
      responseStatus: 'pending',
      invitationMethod: method
    });

    this.updatedAt = new Date();
  }

  public acceptInvitation(supplierId: string): void {
    const invitation = this.invitedSuppliers.find(inv => inv.supplierId === supplierId);
    if (!invitation) {
      throw new Error('Supplier not invited');
    }

    invitation.respondedAt = new Date();
    invitation.responseStatus = 'accepted';
    this.updatedAt = new Date();
  }

  public declineInvitation(supplierId: string): void {
    const invitation = this.invitedSuppliers.find(inv => inv.supplierId === supplierId);
    if (!invitation) {
      throw new Error('Supplier not invited');
    }

    invitation.respondedAt = new Date();
    invitation.responseStatus = 'declined';
    this.updatedAt = new Date();
  }

  // Bid Management
  public submitBid(bid: Bid): void {
    if (this.status !== RfqStatus.BIDDING_OPEN) {
      throw new Error('Bidding is not open');
    }
    if (new Date() > this.biddingEndDate) {
      throw new Error('Bidding deadline has passed');
    }

    // Check if supplier was invited
    const invitation = this.invitedSuppliers.find(inv => inv.supplierId === bid.supplierId);
    if (!invitation || invitation.responseStatus !== 'accepted') {
      throw new Error('Supplier not eligible to bid');
    }

    // Check for duplicate bids
    const existingBid = this.bids.find(b => b.supplierId === bid.supplierId);
    if (existingBid) {
      throw new Error('Supplier has already submitted a bid');
    }

    this.bids.push(bid);
    this.updatedAt = new Date();
  }

  // Analysis Methods
  public getBidSummary(): {
    totalBids: number;
    averageBidValue: number;
    lowestBid: number;
    highestBid: number;
    bidDistribution: Array<{ range: string; count: number }>;
  } {
    if (this.bids.length === 0) {
      return {
        totalBids: 0,
        averageBidValue: 0,
        lowestBid: 0,
        highestBid: 0,
        bidDistribution: []
      };
    }

    const bidValues = this.bids.map(bid => bid.totalValue);
    const averageBidValue = bidValues.reduce((sum, value) => sum + value, 0) / bidValues.length;
    const lowestBid = Math.min(...bidValues);
    const highestBid = Math.max(...bidValues);

    // Create bid distribution ranges
    const rangeSize = (highestBid - lowestBid) / 5;
    const bidDistribution = [];

    for (let i = 0; i < 5; i++) {
      const minRange = lowestBid + (i * rangeSize);
      const maxRange = minRange + rangeSize;
      const count = bidValues.filter(value => value >= minRange && value < maxRange).length;
      bidDistribution.push({
        range: `${minRange.toFixed(0)}-${maxRange.toFixed(0)}`,
        count
      });
    }

    return {
      totalBids: this.bids.length,
      averageBidValue,
      lowestBid,
      highestBid,
      bidDistribution
    };
  }

  public getResponseRate(): number {
    const invitedCount = this.invitedSuppliers.length;
    if (invitedCount === 0) return 0;

    const respondedCount = this.invitedSuppliers.filter(inv => inv.responseStatus !== 'pending').length;
    return (respondedCount / invitedCount) * 100;
  }

  public getBidParticipationRate(): number {
    const acceptedInvitations = this.invitedSuppliers.filter(inv => inv.responseStatus === 'accepted').length;
    if (acceptedInvitations === 0) return 0;

    return (this.bids.length / acceptedInvitations) * 100;
  }

  // Validation Methods
  public validateForPublishing(): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!this.title.trim()) {
      errors.push('Title is required');
    }

    if (this.items.length === 0) {
      errors.push('At least one item is required');
    }

    if (this.invitedSuppliers.length === 0) {
      errors.push('At least one supplier must be invited');
    }

    if (this.biddingStartDate >= this.biddingEndDate) {
      errors.push('Bidding end date must be after start date');
    }

    if (this.biddingStartDate < new Date()) {
      errors.push('Bidding start date cannot be in the past');
    }

    // Validate evaluation criteria weights sum to 100
    const totalWeight = this.evaluationCriteria.reduce((sum, criterion) => sum + criterion.weight, 0);
    if (Math.abs(totalWeight - 100) > 0.01) {
      errors.push('Evaluation criteria weights must sum to 100%');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  private getDefaultEvaluationCriteria(): Array<{
    criterion: string;
    weight: number;
    description: string;
  }> {
    return [
      {
        criterion: 'price',
        weight: 40,
        description: 'Total bid price and value for money'
      },
      {
        criterion: 'quality',
        weight: 20,
        description: 'Product/service quality and specifications compliance'
      },
      {
        criterion: 'delivery',
        weight: 15,
        description: 'Delivery timeline and reliability'
      },
      {
        criterion: 'experience',
        weight: 10,
        description: 'Supplier experience and track record'
      },
      {
        criterion: 'sustainability',
        weight: 10,
        description: 'Environmental and social responsibility'
      },
      {
        criterion: 'innovation',
        weight: 5,
        description: 'Innovation and value-added services'
      }
    ];
  }

  public updateTimestamp(): void {
    this.updatedAt = new Date();
  }
}