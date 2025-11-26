import { z } from 'zod';
export declare const ContractType: {
    readonly BUY: "Buy";
    readonly SELL: "Sell";
};
export declare const CommodityType: {
    readonly WHEAT: "WHEAT";
    readonly BARLEY: "BARLEY";
    readonly RAPESEED: "RAPESEED";
    readonly SOYMEAL: "SOYMEAL";
    readonly COMPOUND_FEED: "COMPOUND_FEED";
    readonly FERTILIZER: "FERTILIZER";
};
export declare const ContractStatus: {
    readonly DRAFT: "Draft";
    readonly ACTIVE: "Active";
    readonly PARTIALLY_FULFILLED: "PartiallyFulfilled";
    readonly FULFILLED: "Fulfilled";
    readonly CANCELLED: "Cancelled";
    readonly DEFAULTED: "Defaulted";
};
export declare const PricingMode: {
    readonly FORWARD_CASH: "FORWARD_CASH";
    readonly BASIS: "BASIS";
    readonly HTA: "HTA";
    readonly DEFERRED: "DEFERRED";
    readonly MIN_PRICE: "MIN_PRICE";
    readonly FIXED: "FIXED";
    readonly INDEXED: "INDEXED";
};
export declare const ShipmentType: {
    readonly SPOT: "Spot";
    readonly WINDOW: "Window";
    readonly CALL_OFF: "CallOff";
};
export declare const TitleTransferType: {
    readonly AT_DELIVERY: "AtDelivery";
    readonly AT_STORAGE: "AtStorage";
    readonly AT_PRICING: "AtPricing";
};
export type ContractTypeValue = typeof ContractType[keyof typeof ContractType];
export type CommodityTypeValue = typeof CommodityType[keyof typeof CommodityType];
export type ContractStatusValue = typeof ContractStatus[keyof typeof ContractStatus];
export type PricingModeValue = typeof PricingMode[keyof typeof PricingMode];
export type ShipmentTypeValue = typeof ShipmentType[keyof typeof ShipmentType];
export type TitleTransferTypeValue = typeof TitleTransferType[keyof typeof TitleTransferType];
export declare const PricingTermsSchema: z.ZodObject<{
    mode: z.ZodEnum<["FORWARD_CASH", "BASIS", "HTA", "DEFERRED", "MIN_PRICE", "FIXED", "INDEXED"]>;
    referenceMarket: z.ZodOptional<z.ZodEnum<["CME", "EURONEXT", "CASH_INDEX"]>>;
    futuresMonth: z.ZodOptional<z.ZodString>;
    basis: z.ZodOptional<z.ZodNumber>;
    fees: z.ZodOptional<z.ZodObject<{
        elevator: z.ZodOptional<z.ZodNumber>;
        optionPremium: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        elevator?: number | undefined;
        optionPremium?: number | undefined;
    }, {
        elevator?: number | undefined;
        optionPremium?: number | undefined;
    }>>;
    fx: z.ZodOptional<z.ZodObject<{
        pair: z.ZodString;
        method: z.ZodEnum<["SPOT", "FIXING"]>;
    }, "strip", z.ZodTypeAny, {
        pair: string;
        method: "SPOT" | "FIXING";
    }, {
        pair: string;
        method: "SPOT" | "FIXING";
    }>>;
    lastFixingAt: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    mode: "FORWARD_CASH" | "BASIS" | "HTA" | "DEFERRED" | "MIN_PRICE" | "FIXED" | "INDEXED";
    referenceMarket?: "CME" | "EURONEXT" | "CASH_INDEX" | undefined;
    futuresMonth?: string | undefined;
    basis?: number | undefined;
    fees?: {
        elevator?: number | undefined;
        optionPremium?: number | undefined;
    } | undefined;
    fx?: {
        pair: string;
        method: "SPOT" | "FIXING";
    } | undefined;
    lastFixingAt?: string | undefined;
}, {
    mode: "FORWARD_CASH" | "BASIS" | "HTA" | "DEFERRED" | "MIN_PRICE" | "FIXED" | "INDEXED";
    referenceMarket?: "CME" | "EURONEXT" | "CASH_INDEX" | undefined;
    futuresMonth?: string | undefined;
    basis?: number | undefined;
    fees?: {
        elevator?: number | undefined;
        optionPremium?: number | undefined;
    } | undefined;
    fx?: {
        pair: string;
        method: "SPOT" | "FIXING";
    } | undefined;
    lastFixingAt?: string | undefined;
}>;
export declare const DeliveryTermsSchema: z.ZodObject<{
    shipmentType: z.ZodEnum<["Spot", "Window", "CallOff"]>;
    parity: z.ZodOptional<z.ZodString>;
    storage: z.ZodOptional<z.ZodObject<{
        allowed: z.ZodBoolean;
        tariff: z.ZodOptional<z.ZodNumber>;
        titleTransfer: z.ZodOptional<z.ZodEnum<["AtDelivery", "AtStorage", "AtPricing"]>>;
    }, "strip", z.ZodTypeAny, {
        allowed: boolean;
        tariff?: number | undefined;
        titleTransfer?: "AtDelivery" | "AtStorage" | "AtPricing" | undefined;
    }, {
        allowed: boolean;
        tariff?: number | undefined;
        titleTransfer?: "AtDelivery" | "AtStorage" | "AtPricing" | undefined;
    }>>;
    qualitySpecs: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
}, "strip", z.ZodTypeAny, {
    shipmentType: "Spot" | "Window" | "CallOff";
    parity?: string | undefined;
    storage?: {
        allowed: boolean;
        tariff?: number | undefined;
        titleTransfer?: "AtDelivery" | "AtStorage" | "AtPricing" | undefined;
    } | undefined;
    qualitySpecs?: Record<string, any> | undefined;
}, {
    shipmentType: "Spot" | "Window" | "CallOff";
    parity?: string | undefined;
    storage?: {
        allowed: boolean;
        tariff?: number | undefined;
        titleTransfer?: "AtDelivery" | "AtStorage" | "AtPricing" | undefined;
    } | undefined;
    qualitySpecs?: Record<string, any> | undefined;
}>;
export declare const ContractSchema: z.ZodObject<{
    id: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodString;
    contractNo: z.ZodString;
    type: z.ZodEnum<["Buy", "Sell"]>;
    commodity: z.ZodEnum<["WHEAT", "BARLEY", "RAPESEED", "SOYMEAL", "COMPOUND_FEED", "FERTILIZER"]>;
    counterpartyId: z.ZodString;
    incoterm: z.ZodOptional<z.ZodString>;
    deliveryWindow: z.ZodObject<{
        from: z.ZodString;
        to: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        from: string;
        to: string;
    }, {
        from: string;
        to: string;
    }>;
    qty: z.ZodObject<{
        unit: z.ZodEnum<["t", "mt"]>;
        contracted: z.ZodNumber;
        tolerance: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        unit: "t" | "mt";
        contracted: number;
        tolerance?: number | undefined;
    }, {
        unit: "t" | "mt";
        contracted: number;
        tolerance?: number | undefined;
    }>;
    pricing: z.ZodObject<{
        mode: z.ZodEnum<["FORWARD_CASH", "BASIS", "HTA", "DEFERRED", "MIN_PRICE", "FIXED", "INDEXED"]>;
        referenceMarket: z.ZodOptional<z.ZodEnum<["CME", "EURONEXT", "CASH_INDEX"]>>;
        futuresMonth: z.ZodOptional<z.ZodString>;
        basis: z.ZodOptional<z.ZodNumber>;
        fees: z.ZodOptional<z.ZodObject<{
            elevator: z.ZodOptional<z.ZodNumber>;
            optionPremium: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            elevator?: number | undefined;
            optionPremium?: number | undefined;
        }, {
            elevator?: number | undefined;
            optionPremium?: number | undefined;
        }>>;
        fx: z.ZodOptional<z.ZodObject<{
            pair: z.ZodString;
            method: z.ZodEnum<["SPOT", "FIXING"]>;
        }, "strip", z.ZodTypeAny, {
            pair: string;
            method: "SPOT" | "FIXING";
        }, {
            pair: string;
            method: "SPOT" | "FIXING";
        }>>;
        lastFixingAt: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        mode: "FORWARD_CASH" | "BASIS" | "HTA" | "DEFERRED" | "MIN_PRICE" | "FIXED" | "INDEXED";
        referenceMarket?: "CME" | "EURONEXT" | "CASH_INDEX" | undefined;
        futuresMonth?: string | undefined;
        basis?: number | undefined;
        fees?: {
            elevator?: number | undefined;
            optionPremium?: number | undefined;
        } | undefined;
        fx?: {
            pair: string;
            method: "SPOT" | "FIXING";
        } | undefined;
        lastFixingAt?: string | undefined;
    }, {
        mode: "FORWARD_CASH" | "BASIS" | "HTA" | "DEFERRED" | "MIN_PRICE" | "FIXED" | "INDEXED";
        referenceMarket?: "CME" | "EURONEXT" | "CASH_INDEX" | undefined;
        futuresMonth?: string | undefined;
        basis?: number | undefined;
        fees?: {
            elevator?: number | undefined;
            optionPremium?: number | undefined;
        } | undefined;
        fx?: {
            pair: string;
            method: "SPOT" | "FIXING";
        } | undefined;
        lastFixingAt?: string | undefined;
    }>;
    delivery: z.ZodObject<{
        shipmentType: z.ZodEnum<["Spot", "Window", "CallOff"]>;
        parity: z.ZodOptional<z.ZodString>;
        storage: z.ZodOptional<z.ZodObject<{
            allowed: z.ZodBoolean;
            tariff: z.ZodOptional<z.ZodNumber>;
            titleTransfer: z.ZodOptional<z.ZodEnum<["AtDelivery", "AtStorage", "AtPricing"]>>;
        }, "strip", z.ZodTypeAny, {
            allowed: boolean;
            tariff?: number | undefined;
            titleTransfer?: "AtDelivery" | "AtStorage" | "AtPricing" | undefined;
        }, {
            allowed: boolean;
            tariff?: number | undefined;
            titleTransfer?: "AtDelivery" | "AtStorage" | "AtPricing" | undefined;
        }>>;
        qualitySpecs: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
    }, "strip", z.ZodTypeAny, {
        shipmentType: "Spot" | "Window" | "CallOff";
        parity?: string | undefined;
        storage?: {
            allowed: boolean;
            tariff?: number | undefined;
            titleTransfer?: "AtDelivery" | "AtStorage" | "AtPricing" | undefined;
        } | undefined;
        qualitySpecs?: Record<string, any> | undefined;
    }, {
        shipmentType: "Spot" | "Window" | "CallOff";
        parity?: string | undefined;
        storage?: {
            allowed: boolean;
            tariff?: number | undefined;
            titleTransfer?: "AtDelivery" | "AtStorage" | "AtPricing" | undefined;
        } | undefined;
        qualitySpecs?: Record<string, any> | undefined;
    }>;
    status: z.ZodDefault<z.ZodEnum<["Draft", "Active", "PartiallyFulfilled", "Fulfilled", "Cancelled", "Defaulted"]>>;
    createdAt: z.ZodOptional<z.ZodDate>;
    updatedAt: z.ZodOptional<z.ZodDate>;
    version: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    status: "Draft" | "Active" | "PartiallyFulfilled" | "Fulfilled" | "Cancelled" | "Defaulted";
    type: "Buy" | "Sell";
    tenantId: string;
    contractNo: string;
    commodity: "WHEAT" | "BARLEY" | "RAPESEED" | "SOYMEAL" | "COMPOUND_FEED" | "FERTILIZER";
    counterpartyId: string;
    deliveryWindow: {
        from: string;
        to: string;
    };
    qty: {
        unit: "t" | "mt";
        contracted: number;
        tolerance?: number | undefined;
    };
    pricing: {
        mode: "FORWARD_CASH" | "BASIS" | "HTA" | "DEFERRED" | "MIN_PRICE" | "FIXED" | "INDEXED";
        referenceMarket?: "CME" | "EURONEXT" | "CASH_INDEX" | undefined;
        futuresMonth?: string | undefined;
        basis?: number | undefined;
        fees?: {
            elevator?: number | undefined;
            optionPremium?: number | undefined;
        } | undefined;
        fx?: {
            pair: string;
            method: "SPOT" | "FIXING";
        } | undefined;
        lastFixingAt?: string | undefined;
    };
    delivery: {
        shipmentType: "Spot" | "Window" | "CallOff";
        parity?: string | undefined;
        storage?: {
            allowed: boolean;
            tariff?: number | undefined;
            titleTransfer?: "AtDelivery" | "AtStorage" | "AtPricing" | undefined;
        } | undefined;
        qualitySpecs?: Record<string, any> | undefined;
    };
    version: number;
    id?: string | undefined;
    incoterm?: string | undefined;
    createdAt?: Date | undefined;
    updatedAt?: Date | undefined;
}, {
    type: "Buy" | "Sell";
    tenantId: string;
    contractNo: string;
    commodity: "WHEAT" | "BARLEY" | "RAPESEED" | "SOYMEAL" | "COMPOUND_FEED" | "FERTILIZER";
    counterpartyId: string;
    deliveryWindow: {
        from: string;
        to: string;
    };
    qty: {
        unit: "t" | "mt";
        contracted: number;
        tolerance?: number | undefined;
    };
    pricing: {
        mode: "FORWARD_CASH" | "BASIS" | "HTA" | "DEFERRED" | "MIN_PRICE" | "FIXED" | "INDEXED";
        referenceMarket?: "CME" | "EURONEXT" | "CASH_INDEX" | undefined;
        futuresMonth?: string | undefined;
        basis?: number | undefined;
        fees?: {
            elevator?: number | undefined;
            optionPremium?: number | undefined;
        } | undefined;
        fx?: {
            pair: string;
            method: "SPOT" | "FIXING";
        } | undefined;
        lastFixingAt?: string | undefined;
    };
    delivery: {
        shipmentType: "Spot" | "Window" | "CallOff";
        parity?: string | undefined;
        storage?: {
            allowed: boolean;
            tariff?: number | undefined;
            titleTransfer?: "AtDelivery" | "AtStorage" | "AtPricing" | undefined;
        } | undefined;
        qualitySpecs?: Record<string, any> | undefined;
    };
    status?: "Draft" | "Active" | "PartiallyFulfilled" | "Fulfilled" | "Cancelled" | "Defaulted" | undefined;
    id?: string | undefined;
    incoterm?: string | undefined;
    createdAt?: Date | undefined;
    updatedAt?: Date | undefined;
    version?: number | undefined;
}>;
export interface PricingTerms {
    mode: PricingModeValue;
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
    lastFixingAt?: Date;
}
export interface DeliveryTerms {
    shipmentType: ShipmentTypeValue;
    parity?: string;
    storage?: {
        allowed: boolean;
        tariff?: number;
        titleTransfer?: TitleTransferTypeValue;
    };
    qualitySpecs?: Record<string, any>;
}
export interface ContractEntity {
    id: string;
    tenantId: string;
    contractNo: string;
    type: ContractTypeValue;
    commodity: CommodityTypeValue;
    counterpartyId: string;
    incoterm?: string | undefined;
    deliveryWindow: {
        from: Date;
        to: Date;
    };
    qty: {
        unit: 't' | 'mt';
        contracted: number;
        tolerance?: number | undefined;
    };
    pricing: PricingTerms;
    delivery: DeliveryTerms;
    status: ContractStatusValue;
    documentId?: string | undefined;
    createdAt: Date;
    updatedAt: Date;
    version: number;
}
export declare class Contract implements ContractEntity {
    id: string;
    tenantId: string;
    contractNo: string;
    type: ContractTypeValue;
    commodity: CommodityTypeValue;
    counterpartyId: string;
    incoterm?: string;
    deliveryWindow: {
        from: Date;
        to: Date;
    };
    qty: {
        unit: 't' | 'mt';
        contracted: number;
        tolerance?: number | undefined;
    };
    pricing: PricingTerms;
    delivery: DeliveryTerms;
    status: ContractStatusValue;
    documentId?: string;
    createdAt: Date;
    updatedAt: Date;
    version: number;
    constructor(props: ContractEntity);
    activate(): void;
    cancel(): void;
    canBeAmended(): boolean;
    isExpired(): boolean;
    getOpenQuantity(): number;
}
//# sourceMappingURL=contract.d.ts.map