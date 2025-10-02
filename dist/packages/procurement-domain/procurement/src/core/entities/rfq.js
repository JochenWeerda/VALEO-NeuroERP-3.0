"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Rfq = exports.Award = exports.Bid = exports.AwardStatus = exports.BidStatus = exports.RfqStatus = void 0;
const crypto_1 = require("crypto");
var RfqStatus;
(function (RfqStatus) {
    RfqStatus["DRAFT"] = "draft";
    RfqStatus["PUBLISHED"] = "published";
    RfqStatus["BIDDING_OPEN"] = "bidding_open";
    RfqStatus["BIDDING_CLOSED"] = "bidding_closed";
    RfqStatus["EVALUATION"] = "evaluation";
    RfqStatus["AWARDED"] = "awarded";
    RfqStatus["CANCELLED"] = "cancelled";
    RfqStatus["EXPIRED"] = "expired";
})(RfqStatus || (exports.RfqStatus = RfqStatus = {}));
var BidStatus;
(function (BidStatus) {
    BidStatus["SUBMITTED"] = "submitted";
    BidStatus["UNDER_REVIEW"] = "under_review";
    BidStatus["ACCEPTED"] = "accepted";
    BidStatus["REJECTED"] = "rejected";
    BidStatus["WITHDRAWN"] = "withdrawn";
})(BidStatus || (exports.BidStatus = BidStatus = {}));
var AwardStatus;
(function (AwardStatus) {
    AwardStatus["PENDING"] = "pending";
    AwardStatus["APPROVED"] = "approved";
    AwardStatus["REJECTED"] = "rejected";
    AwardStatus["CONTRACT_SIGNED"] = "contract_signed";
})(AwardStatus || (exports.AwardStatus = AwardStatus = {}));
class Bid {
    id;
    rfqId;
    supplierId;
    status;
    items;
    terms;
    totalValue;
    currency;
    submittedBy;
    submittedAt;
    evaluatedAt;
    evaluationScore;
    evaluationNotes;
    attachments; // File references
    createdAt;
    updatedAt;
    constructor(props) {
        this.id = props.id || (0, crypto_1.randomUUID)();
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
    evaluate(score, notes) {
        this.status = BidStatus.UNDER_REVIEW;
        this.evaluationScore = score;
        this.evaluationNotes = notes;
        this.evaluatedAt = new Date();
        this.updatedAt = new Date();
    }
    accept() {
        this.status = BidStatus.ACCEPTED;
        this.updatedAt = new Date();
    }
    reject() {
        this.status = BidStatus.REJECTED;
        this.updatedAt = new Date();
    }
    withdraw() {
        this.status = BidStatus.WITHDRAWN;
        this.updatedAt = new Date();
    }
    isValid() {
        return new Date() < new Date(this.submittedAt.getTime() + this.terms.validityPeriod * 24 * 60 * 60 * 1000);
    }
    getDaysUntilExpiry() {
        const expiryDate = new Date(this.submittedAt.getTime() + this.terms.validityPeriod * 24 * 60 * 60 * 1000);
        return Math.ceil((expiryDate.getTime() - Date.now()) / (24 * 60 * 60 * 1000));
    }
}
exports.Bid = Bid;
class Award {
    id;
    rfqId;
    status;
    awardedTo; // supplierId
    totalAwardedValue;
    currency;
    awardedBy;
    awardedAt;
    approvedBy;
    approvedAt;
    rejectionReason;
    contractId;
    items;
    createdAt;
    updatedAt;
    constructor(props) {
        this.id = (0, crypto_1.randomUUID)();
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
    approve(approvedBy) {
        this.status = AwardStatus.APPROVED;
        this.approvedBy = approvedBy;
        this.approvedAt = new Date();
        this.updatedAt = new Date();
    }
    reject(rejectionReason) {
        this.status = AwardStatus.REJECTED;
        this.rejectionReason = rejectionReason;
        this.updatedAt = new Date();
    }
    signContract(contractId) {
        this.status = AwardStatus.CONTRACT_SIGNED;
        this.contractId = contractId;
        this.updatedAt = new Date();
    }
}
exports.Award = Award;
class Rfq {
    id;
    title;
    description;
    category;
    status;
    type;
    // Scope and Requirements
    items;
    totalEstimatedValue;
    currency;
    // Timeline
    biddingStartDate;
    biddingEndDate;
    evaluationDeadline;
    awardDeadline;
    // Participants
    createdBy;
    invitedSuppliers;
    bids;
    awardDecision;
    // Evaluation
    evaluationCriteria;
    // Metadata
    tenantId;
    department;
    costCenter;
    project;
    priority;
    // System
    createdAt;
    updatedAt;
    publishedAt;
    closedAt;
    constructor(props) {
        this.id = props.id || (0, crypto_1.randomUUID)();
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
    publish() {
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
    openBidding() {
        if (this.status !== RfqStatus.PUBLISHED) {
            throw new Error('RFQ must be published before opening bidding');
        }
        if (new Date() < this.biddingStartDate) {
            throw new Error('Cannot open bidding before start date');
        }
        this.status = RfqStatus.BIDDING_OPEN;
        this.updatedAt = new Date();
    }
    closeBidding() {
        if (this.status !== RfqStatus.BIDDING_OPEN) {
            throw new Error('Bidding must be open to close it');
        }
        this.status = RfqStatus.BIDDING_CLOSED;
        this.closedAt = new Date();
        this.updatedAt = new Date();
    }
    startEvaluation() {
        if (this.status !== RfqStatus.BIDDING_CLOSED) {
            throw new Error('Bidding must be closed before evaluation');
        }
        this.status = RfqStatus.EVALUATION;
        this.updatedAt = new Date();
    }
    makeAward(award) {
        if (this.status !== RfqStatus.EVALUATION) {
            throw new Error('RFQ must be in evaluation status to award');
        }
        this.awardDecision = award;
        this.status = RfqStatus.AWARDED;
        this.updatedAt = new Date();
    }
    cancel(reason) {
        if (this.status === RfqStatus.AWARDED || this.status === RfqStatus.CANCELLED) {
            throw new Error('Cannot cancel awarded or already cancelled RFQ');
        }
        this.status = RfqStatus.CANCELLED;
        this.updatedAt = new Date();
        // TODO: Add cancellation reason tracking
    }
    // Supplier Management
    inviteSupplier(supplierId, method = 'email') {
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
    acceptInvitation(supplierId) {
        const invitation = this.invitedSuppliers.find(inv => inv.supplierId === supplierId);
        if (!invitation) {
            throw new Error('Supplier not invited');
        }
        invitation.respondedAt = new Date();
        invitation.responseStatus = 'accepted';
        this.updatedAt = new Date();
    }
    declineInvitation(supplierId) {
        const invitation = this.invitedSuppliers.find(inv => inv.supplierId === supplierId);
        if (!invitation) {
            throw new Error('Supplier not invited');
        }
        invitation.respondedAt = new Date();
        invitation.responseStatus = 'declined';
        this.updatedAt = new Date();
    }
    // Bid Management
    submitBid(bid) {
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
    getBidSummary() {
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
    getResponseRate() {
        const invitedCount = this.invitedSuppliers.length;
        if (invitedCount === 0)
            return 0;
        const respondedCount = this.invitedSuppliers.filter(inv => inv.responseStatus !== 'pending').length;
        return (respondedCount / invitedCount) * 100;
    }
    getBidParticipationRate() {
        const acceptedInvitations = this.invitedSuppliers.filter(inv => inv.responseStatus === 'accepted').length;
        if (acceptedInvitations === 0)
            return 0;
        return (this.bids.length / acceptedInvitations) * 100;
    }
    // Validation Methods
    validateForPublishing() {
        const errors = [];
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
    getDefaultEvaluationCriteria() {
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
    updateTimestamp() {
        this.updatedAt = new Date();
    }
}
exports.Rfq = Rfq;
