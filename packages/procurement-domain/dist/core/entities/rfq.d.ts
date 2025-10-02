export type RfqId = string & {
    readonly __brand: 'RfqId';
};
export type BidId = string & {
    readonly __brand: 'BidId';
};
export declare enum RfqStatus {
    DRAFT = "draft",
    PUBLISHED = "published",
    BIDDING_OPEN = "bidding_open",
    BIDDING_CLOSED = "bidding_closed",
    EVALUATION = "evaluation",
    AWARDED = "awarded",
    CANCELLED = "cancelled",
    EXPIRED = "expired"
}
export declare enum BidStatus {
    SUBMITTED = "submitted",
    UNDER_REVIEW = "under_review",
    ACCEPTED = "accepted",
    REJECTED = "rejected",
    WITHDRAWN = "withdrawn"
}
export declare enum AwardStatus {
    PENDING = "pending",
    APPROVED = "approved",
    REJECTED = "rejected",
    CONTRACT_SIGNED = "contract_signed"
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
    alternatives?: string[];
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
    leadTime: number;
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
    validityPeriod: number;
    minimumOrderQuantity?: number;
    packaging?: string;
    shipping?: string;
    insurance?: string;
}
export declare class Bid {
    readonly id: BidId;
    readonly rfqId: RfqId;
    readonly supplierId: string;
    status: BidStatus;
    items: BidItem[];
    terms: BidTerms;
    totalValue: number;
    currency: string;
    submittedBy: string;
    readonly submittedAt: Date;
    evaluatedAt?: Date;
    evaluationScore?: number;
    evaluationNotes: string | undefined;
    attachments: string[];
    readonly createdAt: Date;
    updatedAt: Date;
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
    });
    evaluate(score: number, notes?: string): void;
    accept(): void;
    reject(): void;
    withdraw(): void;
    isValid(): boolean;
    getDaysUntilExpiry(): number;
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
export declare class Award {
    readonly id: string;
    readonly rfqId: RfqId;
    status: AwardStatus;
    awardedTo: string;
    totalAwardedValue: number;
    currency: string;
    awardedBy: string;
    readonly awardedAt: Date;
    approvedBy?: string;
    approvedAt?: Date;
    rejectionReason?: string;
    contractId?: string;
    items: Array<{
        rfqItemId: string;
        bidId: BidId;
        awardedQuantity: number;
        awardedPrice: number;
        deliveryDate: Date;
    }>;
    readonly createdAt: Date;
    updatedAt: Date;
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
    });
    approve(approvedBy: string): void;
    reject(rejectionReason: string): void;
    signContract(contractId: string): void;
}
export declare class Rfq {
    readonly id: RfqId;
    title: string;
    description: string;
    category: string;
    status: RfqStatus;
    type: 'rfq' | 'rfp' | 'rfq' | 'auction';
    items: RfqItem[];
    totalEstimatedValue: number;
    currency: string;
    biddingStartDate: Date;
    biddingEndDate: Date;
    evaluationDeadline?: Date;
    awardDeadline?: Date;
    createdBy: string;
    invitedSuppliers: RfqInvitation[];
    bids: Bid[];
    awardDecision: Award | undefined;
    evaluationCriteria: Array<{
        criterion: string;
        weight: number;
        description: string;
    }>;
    tenantId: string;
    department: string | undefined;
    costCenter: string | undefined;
    project: string | undefined;
    priority: 'low' | 'medium' | 'high' | 'critical';
    readonly createdAt: Date;
    updatedAt: Date;
    publishedAt?: Date;
    closedAt?: Date;
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
    });
    publish(): void;
    openBidding(): void;
    closeBidding(): void;
    startEvaluation(): void;
    makeAward(award: Award): void;
    cancel(reason?: string): void;
    inviteSupplier(supplierId: string, method?: 'email' | 'portal' | 'api'): void;
    acceptInvitation(supplierId: string): void;
    declineInvitation(supplierId: string): void;
    submitBid(bid: Bid): void;
    getBidSummary(): {
        totalBids: number;
        averageBidValue: number;
        lowestBid: number;
        highestBid: number;
        bidDistribution: Array<{
            range: string;
            count: number;
        }>;
    };
    getResponseRate(): number;
    getBidParticipationRate(): number;
    validateForPublishing(): {
        isValid: boolean;
        errors: string[];
    };
    private getDefaultEvaluationCriteria;
    updateTimestamp(): void;
}
//# sourceMappingURL=rfq.d.ts.map