"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Contract = exports.ContractSchema = exports.DeliveryTermsSchema = exports.PricingTermsSchema = exports.TitleTransferType = exports.ShipmentType = exports.PricingMode = exports.ContractStatus = exports.CommodityType = exports.ContractType = void 0;
const zod_1 = require("zod");
exports.ContractType = {
    BUY: 'Buy',
    SELL: 'Sell',
};
exports.CommodityType = {
    WHEAT: 'WHEAT',
    BARLEY: 'BARLEY',
    RAPESEED: 'RAPESEED',
    SOYMEAL: 'SOYMEAL',
    COMPOUND_FEED: 'COMPOUND_FEED',
    FERTILIZER: 'FERTILIZER',
};
exports.ContractStatus = {
    DRAFT: 'Draft',
    ACTIVE: 'Active',
    PARTIALLY_FULFILLED: 'PartiallyFulfilled',
    FULFILLED: 'Fulfilled',
    CANCELLED: 'Cancelled',
    DEFAULTED: 'Defaulted',
};
exports.PricingMode = {
    FORWARD_CASH: 'FORWARD_CASH',
    BASIS: 'BASIS',
    HTA: 'HTA',
    DEFERRED: 'DEFERRED',
    MIN_PRICE: 'MIN_PRICE',
    FIXED: 'FIXED',
    INDEXED: 'INDEXED',
};
exports.ShipmentType = {
    SPOT: 'Spot',
    WINDOW: 'Window',
    CALL_OFF: 'CallOff',
};
exports.TitleTransferType = {
    AT_DELIVERY: 'AtDelivery',
    AT_STORAGE: 'AtStorage',
    AT_PRICING: 'AtPricing',
};
exports.PricingTermsSchema = zod_1.z.object({
    mode: zod_1.z.enum([exports.PricingMode.FORWARD_CASH, exports.PricingMode.BASIS, exports.PricingMode.HTA, exports.PricingMode.DEFERRED, exports.PricingMode.MIN_PRICE, exports.PricingMode.FIXED, exports.PricingMode.INDEXED]),
    referenceMarket: zod_1.z.enum(['CME', 'EURONEXT', 'CASH_INDEX']).optional(),
    futuresMonth: zod_1.z.string().optional(),
    basis: zod_1.z.number().optional(),
    fees: zod_1.z.object({
        elevator: zod_1.z.number().optional(),
        optionPremium: zod_1.z.number().optional(),
    }).optional(),
    fx: zod_1.z.object({
        pair: zod_1.z.string(),
        method: zod_1.z.enum(['SPOT', 'FIXING']),
    }).optional(),
    lastFixingAt: zod_1.z.string().datetime().optional(),
});
exports.DeliveryTermsSchema = zod_1.z.object({
    shipmentType: zod_1.z.enum([exports.ShipmentType.SPOT, exports.ShipmentType.WINDOW, exports.ShipmentType.CALL_OFF]),
    parity: zod_1.z.string().optional(),
    storage: zod_1.z.object({
        allowed: zod_1.z.boolean(),
        tariff: zod_1.z.number().optional(),
        titleTransfer: zod_1.z.enum([exports.TitleTransferType.AT_DELIVERY, exports.TitleTransferType.AT_STORAGE, exports.TitleTransferType.AT_PRICING]).optional(),
    }).optional(),
    qualitySpecs: zod_1.z.record(zod_1.z.string(), zod_1.z.any()).optional(),
});
exports.ContractSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    tenantId: zod_1.z.string(),
    contractNo: zod_1.z.string(),
    type: zod_1.z.enum([exports.ContractType.BUY, exports.ContractType.SELL]),
    commodity: zod_1.z.enum([exports.CommodityType.WHEAT, exports.CommodityType.BARLEY, exports.CommodityType.RAPESEED, exports.CommodityType.SOYMEAL, exports.CommodityType.COMPOUND_FEED, exports.CommodityType.FERTILIZER]),
    counterpartyId: zod_1.z.string(),
    incoterm: zod_1.z.string().optional(),
    deliveryWindow: zod_1.z.object({
        from: zod_1.z.string().datetime(),
        to: zod_1.z.string().datetime(),
    }),
    qty: zod_1.z.object({
        unit: zod_1.z.enum(['t', 'mt']),
        contracted: zod_1.z.number().positive(),
        tolerance: zod_1.z.number().min(0).max(20).optional(),
    }),
    pricing: exports.PricingTermsSchema,
    delivery: exports.DeliveryTermsSchema,
    status: zod_1.z.enum([exports.ContractStatus.DRAFT, exports.ContractStatus.ACTIVE, exports.ContractStatus.PARTIALLY_FULFILLED, exports.ContractStatus.FULFILLED, exports.ContractStatus.CANCELLED, exports.ContractStatus.DEFAULTED]).default(exports.ContractStatus.DRAFT),
    createdAt: zod_1.z.date().optional(),
    updatedAt: zod_1.z.date().optional(),
    version: zod_1.z.number().default(1),
});
class Contract {
    id;
    tenantId;
    contractNo;
    type;
    commodity;
    counterpartyId;
    incoterm;
    deliveryWindow;
    qty;
    pricing;
    delivery;
    status;
    documentId;
    createdAt;
    updatedAt;
    version;
    constructor(props) {
        this.id = props.id;
        this.tenantId = props.tenantId;
        this.contractNo = props.contractNo;
        this.type = props.type;
        this.commodity = props.commodity;
        this.counterpartyId = props.counterpartyId;
        if (props.incoterm)
            this.incoterm = props.incoterm;
        this.deliveryWindow = props.deliveryWindow;
        this.qty = props.qty;
        this.pricing = props.pricing;
        this.delivery = props.delivery;
        this.status = props.status;
        if (props.documentId)
            this.documentId = props.documentId;
        this.createdAt = props.createdAt;
        this.updatedAt = props.updatedAt;
        this.version = props.version;
    }
    activate() {
        if (this.status !== exports.ContractStatus.DRAFT) {
            throw new Error('Only draft contracts can be activated');
        }
        this.status = exports.ContractStatus.ACTIVE;
        this.updatedAt = new Date();
        this.version++;
    }
    cancel() {
        if (this.status === exports.ContractStatus.FULFILLED || this.status === exports.ContractStatus.CANCELLED) {
            throw new Error('Contract cannot be cancelled in current status');
        }
        this.status = exports.ContractStatus.CANCELLED;
        this.updatedAt = new Date();
        this.version++;
    }
    canBeAmended() {
        const amendableStatuses = [exports.ContractStatus.DRAFT, exports.ContractStatus.ACTIVE, exports.ContractStatus.PARTIALLY_FULFILLED];
        return amendableStatuses.includes(this.status);
    }
    isExpired() {
        return new Date() > this.deliveryWindow.to;
    }
    getOpenQuantity() {
        return this.qty.contracted;
    }
}
exports.Contract = Contract;
//# sourceMappingURL=contract.js.map