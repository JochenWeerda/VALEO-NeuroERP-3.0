"use strict";
var __esDecorate = (this && this.__esDecorate) || function (ctor, descriptorIn, decorators, contextIn, initializers, extraInitializers) {
    function accept(f) { if (f !== void 0 && typeof f !== "function") throw new TypeError("Function expected"); return f; }
    var kind = contextIn.kind, key = kind === "getter" ? "get" : kind === "setter" ? "set" : "value";
    var target = !descriptorIn && ctor ? contextIn["static"] ? ctor : ctor.prototype : null;
    var descriptor = descriptorIn || (target ? Object.getOwnPropertyDescriptor(target, contextIn.name) : {});
    var _, done = false;
    for (var i = decorators.length - 1; i >= 0; i--) {
        var context = {};
        for (var p in contextIn) context[p] = p === "access" ? {} : contextIn[p];
        for (var p in contextIn.access) context.access[p] = contextIn.access[p];
        context.addInitializer = function (f) { if (done) throw new TypeError("Cannot add initializers after decoration has completed"); extraInitializers.push(accept(f || null)); };
        var result = (0, decorators[i])(kind === "accessor" ? { get: descriptor.get, set: descriptor.set } : descriptor[key], context);
        if (kind === "accessor") {
            if (result === void 0) continue;
            if (result === null || typeof result !== "object") throw new TypeError("Object expected");
            if (_ = accept(result.get)) descriptor.get = _;
            if (_ = accept(result.set)) descriptor.set = _;
            if (_ = accept(result.init)) initializers.unshift(_);
        }
        else if (_ = accept(result)) {
            if (kind === "field") initializers.unshift(_);
            else descriptor[key] = _;
        }
    }
    if (target) Object.defineProperty(target, contextIn.name, descriptor);
    done = true;
};
var __runInitializers = (this && this.__runInitializers) || function (thisArg, initializers, value) {
    var useValue = arguments.length > 2;
    for (var i = 0; i < initializers.length; i++) {
        value = useValue ? initializers[i].call(thisArg, value) : initializers[i].call(thisArg);
    }
    return useValue ? value : void 0;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ThreeWayMatchEngine = void 0;
const inversify_1 = require("inversify");
let ThreeWayMatchEngine = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var ThreeWayMatchEngine = class {
        static { _classThis = this; }
        static {
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
            __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
            ThreeWayMatchEngine = _classThis = _classDescriptor.value;
            if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
            __runInitializers(_classThis, _classExtraInitializers);
        }
        defaultConfig = {
            tolerance: {
                quantity: 5, // 5%
                price: 2, // 2%
                date: 7 // 7 days
            },
            autoApproval: {
                enabled: true,
                maxVariancePercentage: 5,
                requiresReceipt: true,
                restrictedCategories: ['IT Hardware', 'Software Licenses']
            },
            escalation: {
                lowVarianceApprover: 'Procurement Specialist',
                mediumVarianceApprover: 'Procurement Manager',
                highVarianceApprover: 'Finance Manager',
                criticalVarianceApprover: 'CFO'
            }
        };
        /**
         * Perform 3-way matching between PO, Receipt, and Invoice
         */
        async performThreeWayMatch(purchaseOrder, receipt, invoice, config = {}) {
            const effectiveConfig = { ...this.defaultConfig, ...config };
            // Validate inputs
            this.validateMatchInputs(purchaseOrder, receipt, invoice);
            // Perform detailed matching
            const itemMatches = await this.matchItems(purchaseOrder, receipt, invoice, effectiveConfig);
            const exceptions = this.identifyExceptions(itemMatches, effectiveConfig);
            // Calculate overall results
            const quantityMatch = this.determineQuantityMatch(itemMatches);
            const priceMatch = this.determinePriceMatch(itemMatches, effectiveConfig);
            const qualityMatch = this.determineQualityMatch(receipt);
            const overallStatus = this.determineOverallStatus(quantityMatch, priceMatch, qualityMatch, exceptions);
            const totalVariance = itemMatches.reduce((sum, match) => sum + Math.abs(match.varianceAmount), 0);
            const variancePercentage = purchaseOrder.totalAmount > 0 ? (totalVariance / purchaseOrder.totalAmount) * 100 : 0;
            const autoApprovalEligible = this.checkAutoApprovalEligibility(overallStatus, variancePercentage, exceptions, effectiveConfig);
            return {
                matchId: this.generateMatchId(),
                purchaseOrderId: purchaseOrder.id,
                receiptId: receipt.id,
                invoiceId: invoice.invoiceId,
                matchType: 'three_way',
                overallStatus,
                quantityMatch,
                priceMatch,
                qualityMatch,
                itemMatches,
                totalVariance,
                variancePercentage,
                exceptionsCount: exceptions.length,
                autoApprovalEligible,
                matchedAt: new Date(),
                matchedBy: 'auto'
            };
        }
        /**
         * Perform 2-way matching between PO and Invoice (when no receipt available)
         */
        async performTwoWayMatch(purchaseOrder, invoice, config = {}) {
            const effectiveConfig = { ...this.defaultConfig, ...config };
            // Validate inputs
            this.validateTwoWayInputs(purchaseOrder, invoice);
            // Perform matching without receipt
            const itemMatches = await this.matchItemsTwoWay(purchaseOrder, invoice, effectiveConfig);
            const exceptions = this.identifyExceptions(itemMatches, effectiveConfig);
            // Calculate results
            const quantityMatch = this.determineQuantityMatch(itemMatches);
            const priceMatch = this.determinePriceMatch(itemMatches, effectiveConfig);
            const qualityMatch = 'no_receipt';
            const overallStatus = this.determineOverallStatus(quantityMatch, priceMatch, qualityMatch, exceptions);
            const totalVariance = itemMatches.reduce((sum, match) => sum + Math.abs(match.varianceAmount), 0);
            const variancePercentage = purchaseOrder.totalAmount > 0 ? (totalVariance / purchaseOrder.totalAmount) * 100 : 0;
            const autoApprovalEligible = this.checkAutoApprovalEligibility(overallStatus, variancePercentage, exceptions, effectiveConfig);
            return {
                matchId: this.generateMatchId(),
                purchaseOrderId: purchaseOrder.id,
                invoiceId: invoice.invoiceId,
                matchType: 'two_way',
                overallStatus,
                quantityMatch,
                priceMatch,
                qualityMatch,
                itemMatches,
                totalVariance,
                variancePercentage,
                exceptionsCount: exceptions.length,
                autoApprovalEligible,
                matchedAt: new Date(),
                matchedBy: 'auto'
            };
        }
        /**
         * Resolve matching exceptions
         */
        async resolveException(exceptionId, resolution) {
            // In production, this would update the exception record in database
            console.log(`Resolving exception ${exceptionId} with action: ${resolution.action}`);
        }
        /**
         * Get matching statistics and KPIs
         */
        async getMatchingStatistics(dateRange, filters) {
            // Mock statistics - in production, query from database
            return {
                totalMatches: 1250,
                matchedCount: 1100,
                exceptionCount: 150,
                autoApprovedCount: 950,
                averageProcessingTime: 2.3, // minutes
                topExceptionTypes: [
                    { type: 'price_variance', count: 65 },
                    { type: 'quantity_mismatch', count: 45 },
                    { type: 'quality_issue', count: 25 },
                    { type: 'missing_receipt', count: 15 }
                ],
                supplierPerformance: [
                    { supplierId: 'supplier-a', matchRate: 98, avgVariance: 0.5 },
                    { supplierId: 'supplier-b', matchRate: 95, avgVariance: 1.2 },
                    { supplierId: 'supplier-c', matchRate: 92, avgVariance: 2.1 }
                ]
            };
        }
        // Private methods
        validateMatchInputs(po, receipt, invoice) {
            if (po.id !== invoice.purchaseOrderId) {
                throw new Error('Invoice does not match purchase order');
            }
            if (receipt.header.purchaseOrderId !== po.id) {
                throw new Error('Receipt does not match purchase order');
            }
            if (receipt.header.supplierId !== invoice.supplierId) {
                throw new Error('Receipt and invoice supplier mismatch');
            }
        }
        validateTwoWayInputs(po, invoice) {
            if (po.id !== invoice.purchaseOrderId) {
                throw new Error('Invoice does not match purchase order');
            }
        }
        async matchItems(po, receipt, invoice, config) {
            const matches = [];
            for (const poItem of po.items) {
                // Find corresponding receipt item
                const receiptItem = receipt.items.find(ri => ri.purchaseOrderItemId === poItem.id);
                // Find corresponding invoice item
                const invoiceItem = invoice.items.find(ii => ii.purchaseOrderItemId === poItem.id);
                if (!invoiceItem) {
                    matches.push({
                        purchaseOrderItemId: poItem.id,
                        invoiceItemId: '',
                        quantityMatch: false,
                        priceMatch: false,
                        qualityMatch: !!receiptItem,
                        exceptions: ['Invoice item not found'],
                        varianceAmount: poItem.lineTotal
                    });
                    continue;
                }
                const quantityMatch = this.checkQuantityMatch(poItem, receiptItem, invoiceItem, config);
                const priceMatch = this.checkPriceMatch(poItem, invoiceItem, config);
                const qualityMatch = this.checkQualityMatch(receiptItem);
                const exceptions = this.identifyItemExceptions(poItem, receiptItem, invoiceItem, config);
                const varianceAmount = this.calculateVarianceAmount(poItem, invoiceItem);
                matches.push({
                    purchaseOrderItemId: poItem.id,
                    ...(receiptItem?.id && { receiptItemId: receiptItem.id }),
                    invoiceItemId: invoiceItem.purchaseOrderItemId,
                    quantityMatch,
                    priceMatch,
                    qualityMatch,
                    exceptions,
                    varianceAmount
                });
            }
            return matches;
        }
        async matchItemsTwoWay(po, invoice, config) {
            const matches = [];
            for (const poItem of po.items) {
                const invoiceItem = invoice.items.find(ii => ii.purchaseOrderItemId === poItem.id);
                if (!invoiceItem) {
                    matches.push({
                        purchaseOrderItemId: poItem.id,
                        invoiceItemId: '',
                        quantityMatch: false,
                        priceMatch: false,
                        qualityMatch: false,
                        exceptions: ['Invoice item not found'],
                        varianceAmount: poItem.lineTotal
                    });
                    continue;
                }
                const quantityMatch = this.checkQuantityMatchTwoWay(poItem, invoiceItem, config);
                const priceMatch = this.checkPriceMatch(poItem, invoiceItem, config);
                const qualityMatch = false; // No receipt for quality check
                const exceptions = this.identifyItemExceptionsTwoWay(poItem, invoiceItem, config);
                const varianceAmount = this.calculateVarianceAmount(poItem, invoiceItem);
                matches.push({
                    purchaseOrderItemId: poItem.id,
                    invoiceItemId: invoiceItem.purchaseOrderItemId,
                    quantityMatch,
                    priceMatch,
                    qualityMatch,
                    exceptions,
                    varianceAmount
                });
            }
            return matches;
        }
        checkQuantityMatch(poItem, receiptItem, invoiceItem, config) {
            if (!receiptItem)
                return false;
            const tolerance = config.tolerance.quantity / 100;
            const maxVariance = poItem.quantityOrdered * tolerance;
            const quantityVariance = Math.abs(invoiceItem.quantity - receiptItem.quantityReceived);
            return quantityVariance <= maxVariance;
        }
        checkQuantityMatchTwoWay(poItem, invoiceItem, config) {
            const tolerance = config.tolerance.quantity / 100;
            const maxVariance = poItem.quantityOrdered * tolerance;
            const quantityVariance = Math.abs(invoiceItem.quantity - poItem.quantityOrdered);
            return quantityVariance <= maxVariance;
        }
        checkPriceMatch(poItem, invoiceItem, config) {
            const tolerance = config.tolerance.price / 100;
            const maxVariance = poItem.unitPrice * tolerance;
            const priceVariance = Math.abs(invoiceItem.unitPrice - poItem.unitPrice);
            return priceVariance <= maxVariance;
        }
        checkQualityMatch(receiptItem) {
            if (!receiptItem)
                return false;
            return receiptItem.inspectionStatus === 'passed' || receiptItem.inspectionStatus === 'conditional';
        }
        identifyItemExceptions(poItem, receiptItem, invoiceItem, config) {
            const exceptions = [];
            // Quantity checks
            if (!this.checkQuantityMatch(poItem, receiptItem, invoiceItem, config)) {
                exceptions.push('Quantity mismatch between PO, receipt, and invoice');
            }
            // Price checks
            if (!this.checkPriceMatch(poItem, invoiceItem, config)) {
                exceptions.push('Price variance exceeds tolerance');
            }
            // Quality checks
            if (!this.checkQualityMatch(receiptItem)) {
                exceptions.push('Quality inspection failed');
            }
            // Date checks
            if (receiptItem && Math.abs(invoiceItem.deliveryDate?.getTime() - receiptItem.deliveryDate?.getTime()) > config.tolerance.date * 24 * 60 * 60 * 1000) {
                exceptions.push('Delivery date variance');
            }
            return exceptions;
        }
        identifyItemExceptionsTwoWay(poItem, invoiceItem, config) {
            const exceptions = [];
            if (!this.checkQuantityMatchTwoWay(poItem, invoiceItem, config)) {
                exceptions.push('Quantity mismatch between PO and invoice');
            }
            if (!this.checkPriceMatch(poItem, invoiceItem, config)) {
                exceptions.push('Price variance exceeds tolerance');
            }
            exceptions.push('No receipt available for verification');
            return exceptions;
        }
        identifyExceptions(itemMatches, config) {
            const exceptions = [];
            for (const match of itemMatches) {
                for (const exception of match.exceptions) {
                    const severity = this.determineExceptionSeverity(exception, match.varianceAmount, config);
                    exceptions.push({
                        exceptionId: this.generateExceptionId(),
                        matchId: '', // Would be set when creating match result
                        exceptionType: this.mapExceptionType(exception),
                        severity,
                        description: exception,
                        affectedItems: [match.purchaseOrderItemId],
                        suggestedResolution: this.getSuggestedResolution(exception),
                        requiresApproval: severity === 'high' || severity === 'critical',
                        approverRole: this.getApproverForSeverity(severity, config),
                        createdAt: new Date()
                    });
                }
            }
            return exceptions;
        }
        determineQuantityMatch(itemMatches) {
            const allMatched = itemMatches.every(m => m.quantityMatch);
            const anyOverInvoice = itemMatches.some(m => !m.quantityMatch && m.exceptions.some(e => e.includes('over')));
            const anyUnderInvoice = itemMatches.some(m => !m.quantityMatch && m.exceptions.some(e => e.includes('under')));
            if (allMatched)
                return 'matched';
            if (anyOverInvoice)
                return 'over_invoice';
            if (anyUnderInvoice)
                return 'under_invoice';
            return 'no_receipt';
        }
        determinePriceMatch(itemMatches, config) {
            const totalVariance = itemMatches.reduce((sum, m) => sum + Math.abs(m.varianceAmount), 0);
            const avgVariance = itemMatches.length > 0 ? totalVariance / itemMatches.length : 0;
            const tolerance = config.tolerance.price / 100;
            if (avgVariance <= tolerance)
                return 'matched';
            return 'price_variance';
        }
        determineQualityMatch(receipt) {
            const qualityMetrics = receipt.getQualityMetrics();
            if (qualityMetrics.overallPassRate >= 95)
                return 'matched';
            if (qualityMetrics.overallPassRate >= 80)
                return 'quality_issues';
            return 'quality_issues';
        }
        determineOverallStatus(quantityMatch, priceMatch, qualityMatch, exceptions) {
            const hasCriticalExceptions = exceptions.some(e => e.severity === 'critical');
            const hasHighExceptions = exceptions.some(e => e.severity === 'high');
            if (hasCriticalExceptions)
                return 'exceptions';
            if (hasHighExceptions)
                return 'exceptions';
            const allMatched = quantityMatch === 'matched' &&
                priceMatch === 'matched' &&
                qualityMatch === 'matched';
            if (allMatched && exceptions.length === 0)
                return 'matched';
            if (exceptions.length > 0)
                return 'partial_match';
            return 'exceptions';
        }
        checkAutoApprovalEligibility(overallStatus, variancePercentage, exceptions, config) {
            if (!config.autoApproval.enabled)
                return false;
            if (overallStatus === 'exceptions')
                return false;
            if (variancePercentage > config.autoApproval.maxVariancePercentage)
                return false;
            if (exceptions.some(e => e.requiresApproval))
                return false;
            return true;
        }
        calculateVarianceAmount(poItem, invoiceItem) {
            const poAmount = poItem.quantityOrdered * poItem.unitPrice;
            const invoiceAmount = invoiceItem.quantity * invoiceItem.unitPrice;
            return invoiceAmount - poAmount;
        }
        determineExceptionSeverity(exception, varianceAmount, config) {
            if (exception.includes('quality') && varianceAmount > config.tolerance.price) {
                return 'critical';
            }
            if (exception.includes('price') && Math.abs(varianceAmount) > 1000) {
                return 'high';
            }
            if (exception.includes('quantity') || exception.includes('missing')) {
                return 'medium';
            }
            return 'low';
        }
        mapExceptionType(exception) {
            if (exception.includes('quantity'))
                return 'quantity_mismatch';
            if (exception.includes('price'))
                return 'price_variance';
            if (exception.includes('quality'))
                return 'quality_issue';
            if (exception.includes('receipt'))
                return 'missing_receipt';
            if (exception.includes('tax'))
                return 'invalid_tax';
            return 'duplicate_invoice';
        }
        getSuggestedResolution(exception) {
            if (exception.includes('quantity'))
                return 'Verify delivered quantities and adjust invoice';
            if (exception.includes('price'))
                return 'Review pricing and approve variance or request correction';
            if (exception.includes('quality'))
                return 'Inspect goods and determine acceptance criteria';
            if (exception.includes('receipt'))
                return 'Obtain receipt documentation or perform 2-way match';
            return 'Review and resolve manually';
        }
        getApproverForSeverity(severity, config) {
            switch (severity) {
                case 'low': return config.escalation.lowVarianceApprover;
                case 'medium': return config.escalation.mediumVarianceApprover;
                case 'high': return config.escalation.highVarianceApprover;
                case 'critical': return config.escalation.criticalVarianceApprover;
                default: return config.escalation.mediumVarianceApprover;
            }
        }
        generateMatchId() {
            return `match_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        }
        generateExceptionId() {
            return `exc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        }
    };
    return ThreeWayMatchEngine = _classThis;
})();
exports.ThreeWayMatchEngine = ThreeWayMatchEngine;
exports.default = ThreeWayMatchEngine;
