"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Contract = exports.RenewalType = exports.ContractType = exports.ContractStatus = void 0;
const crypto_1 = require("crypto");
var ContractStatus;
(function (ContractStatus) {
    ContractStatus["DRAFT"] = "draft";
    ContractStatus["PENDING_APPROVAL"] = "pending_approval";
    ContractStatus["APPROVED"] = "approved";
    ContractStatus["ACTIVE"] = "active";
    ContractStatus["EXPIRED"] = "expired";
    ContractStatus["TERMINATED"] = "terminated";
    ContractStatus["RENEWED"] = "renewed";
    ContractStatus["AMENDED"] = "amended";
})(ContractStatus || (exports.ContractStatus = ContractStatus = {}));
var ContractType;
(function (ContractType) {
    ContractType["FRAMEWORK"] = "framework";
    ContractType["MASTER"] = "master";
    ContractType["PURCHASE"] = "purchase";
    ContractType["SERVICE"] = "service";
    ContractType["MAINTENANCE"] = "maintenance";
    ContractType["LICENSE"] = "license";
    ContractType["LEASE"] = "lease"; // Equipment lease
})(ContractType || (exports.ContractType = ContractType = {}));
var RenewalType;
(function (RenewalType) {
    RenewalType["AUTOMATIC"] = "automatic";
    RenewalType["MANUAL"] = "manual";
    RenewalType["NEGOTIATION_REQUIRED"] = "negotiation_required";
    RenewalType["NO_RENEWAL"] = "no_renewal";
})(RenewalType || (exports.RenewalType = RenewalType = {}));
class Contract {
    id;
    contractNumber;
    title;
    description;
    type;
    status;
    // Parties
    buyer;
    supplier;
    // Dates
    effectiveDate;
    expiryDate;
    signedDate;
    // Items and terms
    items;
    terms;
    // Amendments and renewals
    amendments;
    renewalHistory;
    // Performance tracking
    performanceHistory;
    // Metadata
    tenantId;
    department;
    costCenter;
    project;
    tags;
    attachments;
    // System fields
    createdAt;
    updatedAt;
    createdBy;
    lastModifiedBy;
    version;
    constructor(props) {
        this.id = props.id || (0, crypto_1.randomUUID)();
        this.contractNumber = props.contractNumber || this.generateContractNumber();
        this.title = props.title;
        this.description = props.description;
        this.type = props.type;
        this.status = ContractStatus.DRAFT;
        this.buyer = props.buyer;
        this.supplier = props.supplier;
        this.effectiveDate = props.effectiveDate;
        this.expiryDate = props.expiryDate;
        this.items = props.items;
        this.terms = props.terms;
        this.amendments = [];
        this.renewalHistory = [];
        this.performanceHistory = [];
        this.tenantId = props.tenantId;
        this.department = props.department;
        this.costCenter = props.costCenter;
        this.project = props.project;
        this.tags = props.tags || [];
        this.attachments = props.attachments || [];
        this.createdAt = new Date();
        this.updatedAt = new Date();
        this.createdBy = props.createdBy;
        this.lastModifiedBy = props.createdBy;
        this.version = 1;
    }
    // Business Logic Methods
    submitForApproval() {
        if (this.status !== ContractStatus.DRAFT) {
            throw new Error('Only draft contracts can be submitted for approval');
        }
        this.status = ContractStatus.PENDING_APPROVAL;
        this.updatedAt = new Date();
        this.version++;
    }
    approve(approvedBy) {
        if (this.status !== ContractStatus.PENDING_APPROVAL) {
            throw new Error('Contract must be pending approval');
        }
        this.status = ContractStatus.APPROVED;
        this.signedDate = new Date();
        this.updatedAt = new Date();
        this.version++;
    }
    activate() {
        if (this.status !== ContractStatus.APPROVED) {
            throw new Error('Contract must be approved before activation');
        }
        const now = new Date();
        if (now < this.effectiveDate) {
            throw new Error('Contract cannot be activated before effective date');
        }
        this.status = ContractStatus.ACTIVE;
        this.updatedAt = new Date();
        this.version++;
    }
    amend(amendment) {
        if (this.status !== ContractStatus.ACTIVE) {
            throw new Error('Only active contracts can be amended');
        }
        const amendmentNumber = this.amendments.length + 1;
        const fullAmendment = {
            amendmentId: (0, crypto_1.randomUUID)(),
            amendmentNumber,
            ...amendment
        };
        this.amendments.push(fullAmendment);
        this.status = ContractStatus.AMENDED;
        this.updatedAt = new Date();
        this.version++;
    }
    renew(newExpiryDate, changes, approvedBy) {
        if (this.status !== ContractStatus.ACTIVE && this.status !== ContractStatus.AMENDED) {
            throw new Error('Only active contracts can be renewed');
        }
        this.renewalHistory.push({
            renewalDate: new Date(),
            newExpiryDate,
            changes,
            approvedBy
        });
        this.expiryDate = newExpiryDate;
        this.status = ContractStatus.RENEWED;
        this.updatedAt = new Date();
        this.version++;
    }
    terminate(reason, terminatedBy) {
        if (this.status === ContractStatus.TERMINATED || this.status === ContractStatus.EXPIRED) {
            return;
        }
        this.status = ContractStatus.TERMINATED;
        this.updatedAt = new Date();
        this.version++;
    }
    recordPerformance(performance) {
        this.performanceHistory.push(performance);
        this.updatedAt = new Date();
    }
    // Analysis and Reporting Methods
    getContractValue() {
        const totalValue = this.terms.totalContractValue;
        const spentToDate = this.performanceHistory.reduce((sum, p) => sum + p.actualSpend, 0);
        const remainingValue = totalValue - spentToDate;
        const utilizationRate = totalValue > 0 ? (spentToDate / totalValue) * 100 : 0;
        return {
            totalValue,
            currency: this.terms.currency,
            spentToDate,
            remainingValue,
            utilizationRate
        };
    }
    getPerformanceSummary() {
        if (this.performanceHistory.length === 0) {
            return {
                overallScore: 0,
                slaCompliance: 0,
                costSavings: 0,
                deliveryPerformance: 0,
                qualityScore: 0,
                riskLevel: 'medium'
            };
        }
        const latest = this.performanceHistory[this.performanceHistory.length - 1];
        if (!latest)
            return {
                overallScore: 0,
                slaCompliance: 0,
                costSavings: 0,
                deliveryPerformance: 0,
                qualityScore: 0,
                riskLevel: 'low'
            };
        const slaCompliance = latest.slaCompliance.reduce((sum, sla) => sum + (sla.actual >= sla.target ? 100 : (sla.actual / sla.target) * 100), 0) / latest.slaCompliance.length;
        const deliveryPerformance = latest.ordersFulfilled > 0 ?
            (latest.onTimeDelivery / latest.ordersFulfilled) * 100 : 0;
        const qualityScore = Math.max(0, 100 - (latest.qualityIncidents * 5)); // Deduct 5 points per incident
        const overallScore = (slaCompliance + deliveryPerformance + qualityScore) / 3;
        let riskLevel = 'low';
        if (overallScore < 50)
            riskLevel = 'critical';
        else if (overallScore < 70)
            riskLevel = 'high';
        else if (overallScore < 85)
            riskLevel = 'medium';
        return {
            overallScore,
            slaCompliance,
            costSavings: latest.savings,
            deliveryPerformance,
            qualityScore,
            riskLevel
        };
    }
    getExpiryStatus() {
        const now = new Date();
        const daysToExpiry = Math.ceil((this.expiryDate.getTime() - now.getTime()) / (24 * 60 * 60 * 1000));
        let renewalStatus = 'not_due';
        let isExpiringSoon = false;
        let requiresRenewalAction = false;
        if (daysToExpiry < 0) {
            renewalStatus = 'expired';
            requiresRenewalAction = true;
        }
        else if (daysToExpiry <= 30) {
            renewalStatus = 'overdue';
            requiresRenewalAction = true;
            isExpiringSoon = true;
        }
        else if (daysToExpiry <= 90) {
            renewalStatus = 'due_soon';
            requiresRenewalAction = true;
            isExpiringSoon = true;
        }
        return {
            daysToExpiry,
            isExpiringSoon,
            requiresRenewalAction,
            renewalStatus
        };
    }
    getSpendUnderManagement() {
        const committedSpend = this.terms.totalContractValue;
        const actualSpend = this.performanceHistory.reduce((sum, p) => sum + p.actualSpend, 0);
        const variance = actualSpend - committedSpend;
        const variancePercentage = committedSpend > 0 ? (variance / committedSpend) * 100 : 0;
        let status = 'on_track';
        if (Math.abs(variancePercentage) > 10) {
            status = variance > 0 ? 'over_spend' : 'under_spend';
        }
        return {
            committedSpend,
            actualSpend,
            variance,
            variancePercentage,
            status
        };
    }
    // Validation Methods
    validateForActivation() {
        const errors = [];
        const warnings = [];
        const now = new Date();
        // Basic validations
        if (!this.title.trim()) {
            errors.push('Contract title is required');
        }
        if (this.items.length === 0) {
            errors.push('Contract must have at least one item');
        }
        if (this.expiryDate <= this.effectiveDate) {
            errors.push('Expiry date must be after effective date');
        }
        if (this.effectiveDate > now) {
            warnings.push('Effective date is in the future');
        }
        // Party validations
        if (!this.buyer.contactEmail) {
            errors.push('Buyer contact email is required');
        }
        if (!this.supplier.contactEmail) {
            errors.push('Supplier contact email is required');
        }
        // Financial validations
        if (this.terms.totalContractValue <= 0) {
            errors.push('Total contract value must be greater than 0');
        }
        // Item validations
        for (let i = 0; i < this.items.length; i++) {
            const item = this.items[i];
            if (item && item.unitPrice <= 0) {
                errors.push(`Item ${i + 1}: Unit price must be greater than 0`);
            }
            if (item && item.effectiveTo <= item.effectiveFrom) {
                errors.push(`Item ${i + 1}: Effective to date must be after effective from date`);
            }
        }
        return {
            isValid: errors.length === 0,
            errors,
            warnings
        };
    }
    // Private helper methods
    generateContractNumber() {
        const timestamp = Date.now().toString().slice(-6);
        const random = Math.random().toString(36).substring(2, 5).toUpperCase();
        return `CTR-${timestamp}-${random}`;
    }
    updateTimestamp() {
        this.updatedAt = new Date();
        this.version++;
    }
}
exports.Contract = Contract;
