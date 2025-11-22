import { z } from 'zod';
export declare const ContractTypeEnum: z.ZodEnum<["Buy", "Sell"]>;
export declare const CommodityTypeEnum: z.ZodEnum<["WHEAT", "BARLEY", "RAPESEED", "SOYMEAL", "COMPOUND_FEED", "FERTILIZER"]>;
export declare const ContractStatusEnum: z.ZodEnum<["Draft", "Active", "PartiallyFulfilled", "Fulfilled", "Cancelled", "Defaulted"]>;
export declare const PricingModeEnum: z.ZodEnum<["FORWARD_CASH", "BASIS", "HTA", "DEFERRED", "MIN_PRICE", "FIXED", "INDEXED"]>;
export declare const ShipmentTypeEnum: z.ZodEnum<["Spot", "Window", "CallOff"]>;
export declare const TitleTransferTypeEnum: z.ZodEnum<["AtDelivery", "AtStorage", "AtPricing"]>;
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
export declare const CreateContractSchema: z.ZodObject<{
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
}, "strip", z.ZodTypeAny, {
    type: "Buy" | "Sell";
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
    incoterm?: string | undefined;
}, {
    type: "Buy" | "Sell";
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
    incoterm?: string | undefined;
}>;
export declare const UpdateContractSchema: z.ZodObject<{
    incoterm: z.ZodOptional<z.ZodString>;
    deliveryWindow: z.ZodOptional<z.ZodObject<{
        from: z.ZodString;
        to: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        from: string;
        to: string;
    }, {
        from: string;
        to: string;
    }>>;
    qty: z.ZodOptional<z.ZodObject<{
        contracted: z.ZodOptional<z.ZodNumber>;
        tolerance: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        contracted?: number | undefined;
        tolerance?: number | undefined;
    }, {
        contracted?: number | undefined;
        tolerance?: number | undefined;
    }>>;
    pricing: z.ZodOptional<z.ZodObject<{
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
    }>>;
    delivery: z.ZodOptional<z.ZodObject<{
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
    }>>;
}, "strip", z.ZodTypeAny, {
    incoterm?: string | undefined;
    deliveryWindow?: {
        from: string;
        to: string;
    } | undefined;
    qty?: {
        contracted?: number | undefined;
        tolerance?: number | undefined;
    } | undefined;
    pricing?: {
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
    } | undefined;
    delivery?: {
        shipmentType: "Spot" | "Window" | "CallOff";
        parity?: string | undefined;
        storage?: {
            allowed: boolean;
            tariff?: number | undefined;
            titleTransfer?: "AtDelivery" | "AtStorage" | "AtPricing" | undefined;
        } | undefined;
        qualitySpecs?: Record<string, any> | undefined;
    } | undefined;
}, {
    incoterm?: string | undefined;
    deliveryWindow?: {
        from: string;
        to: string;
    } | undefined;
    qty?: {
        contracted?: number | undefined;
        tolerance?: number | undefined;
    } | undefined;
    pricing?: {
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
    } | undefined;
    delivery?: {
        shipmentType: "Spot" | "Window" | "CallOff";
        parity?: string | undefined;
        storage?: {
            allowed: boolean;
            tariff?: number | undefined;
            titleTransfer?: "AtDelivery" | "AtStorage" | "AtPricing" | undefined;
        } | undefined;
        qualitySpecs?: Record<string, any> | undefined;
    } | undefined;
}>;
export declare const ContractResponseSchema: z.ZodObject<{
    id: z.ZodString;
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
    status: z.ZodEnum<["Draft", "Active", "PartiallyFulfilled", "Fulfilled", "Cancelled", "Defaulted"]>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    version: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    status: "Draft" | "Active" | "PartiallyFulfilled" | "Fulfilled" | "Cancelled" | "Defaulted";
    type: "Buy" | "Sell";
    id: string;
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
    createdAt: string;
    updatedAt: string;
    version: number;
    incoterm?: string | undefined;
}, {
    status: "Draft" | "Active" | "PartiallyFulfilled" | "Fulfilled" | "Cancelled" | "Defaulted";
    type: "Buy" | "Sell";
    id: string;
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
    createdAt: string;
    updatedAt: string;
    version: number;
    incoterm?: string | undefined;
}>;
export declare const ContractListQuerySchema: z.ZodObject<{
    type: z.ZodOptional<z.ZodEnum<["Buy", "Sell"]>>;
    commodity: z.ZodOptional<z.ZodEnum<["WHEAT", "BARLEY", "RAPESEED", "SOYMEAL", "COMPOUND_FEED", "FERTILIZER"]>>;
    status: z.ZodOptional<z.ZodEnum<["Draft", "Active", "PartiallyFulfilled", "Fulfilled", "Cancelled", "Defaulted"]>>;
    counterpartyId: z.ZodOptional<z.ZodString>;
    deliveryFrom: z.ZodOptional<z.ZodString>;
    deliveryTo: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodNumber>;
    pageSize: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    page: number;
    pageSize: number;
    status?: "Draft" | "Active" | "PartiallyFulfilled" | "Fulfilled" | "Cancelled" | "Defaulted" | undefined;
    type?: "Buy" | "Sell" | undefined;
    commodity?: "WHEAT" | "BARLEY" | "RAPESEED" | "SOYMEAL" | "COMPOUND_FEED" | "FERTILIZER" | undefined;
    counterpartyId?: string | undefined;
    deliveryFrom?: string | undefined;
    deliveryTo?: string | undefined;
}, {
    status?: "Draft" | "Active" | "PartiallyFulfilled" | "Fulfilled" | "Cancelled" | "Defaulted" | undefined;
    type?: "Buy" | "Sell" | undefined;
    commodity?: "WHEAT" | "BARLEY" | "RAPESEED" | "SOYMEAL" | "COMPOUND_FEED" | "FERTILIZER" | undefined;
    counterpartyId?: string | undefined;
    page?: number | undefined;
    pageSize?: number | undefined;
    deliveryFrom?: string | undefined;
    deliveryTo?: string | undefined;
}>;
export declare const ContractListResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
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
        status: z.ZodEnum<["Draft", "Active", "PartiallyFulfilled", "Fulfilled", "Cancelled", "Defaulted"]>;
        createdAt: z.ZodString;
        updatedAt: z.ZodString;
        version: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        status: "Draft" | "Active" | "PartiallyFulfilled" | "Fulfilled" | "Cancelled" | "Defaulted";
        type: "Buy" | "Sell";
        id: string;
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
        createdAt: string;
        updatedAt: string;
        version: number;
        incoterm?: string | undefined;
    }, {
        status: "Draft" | "Active" | "PartiallyFulfilled" | "Fulfilled" | "Cancelled" | "Defaulted";
        type: "Buy" | "Sell";
        id: string;
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
        createdAt: string;
        updatedAt: string;
        version: number;
        incoterm?: string | undefined;
    }>, "many">;
    pagination: z.ZodObject<{
        page: z.ZodNumber;
        pageSize: z.ZodNumber;
        total: z.ZodNumber;
        totalPages: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        total: number;
        page: number;
        pageSize: number;
        totalPages: number;
    }, {
        total: number;
        page: number;
        pageSize: number;
        totalPages: number;
    }>;
}, "strip", z.ZodTypeAny, {
    data: {
        status: "Draft" | "Active" | "PartiallyFulfilled" | "Fulfilled" | "Cancelled" | "Defaulted";
        type: "Buy" | "Sell";
        id: string;
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
        createdAt: string;
        updatedAt: string;
        version: number;
        incoterm?: string | undefined;
    }[];
    pagination: {
        total: number;
        page: number;
        pageSize: number;
        totalPages: number;
    };
}, {
    data: {
        status: "Draft" | "Active" | "PartiallyFulfilled" | "Fulfilled" | "Cancelled" | "Defaulted";
        type: "Buy" | "Sell";
        id: string;
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
        createdAt: string;
        updatedAt: string;
        version: number;
        incoterm?: string | undefined;
    }[];
    pagination: {
        total: number;
        page: number;
        pageSize: number;
        totalPages: number;
    };
}>;
export declare const ActivateContractSchema: z.ZodObject<{
    notes: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    notes?: string | undefined;
}, {
    notes?: string | undefined;
}>;
export declare const CancelContractSchema: z.ZodObject<{
    reason: z.ZodString;
    notes: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    reason: string;
    notes?: string | undefined;
}, {
    reason: string;
    notes?: string | undefined;
}>;
export type CreateContract = z.infer<typeof CreateContractSchema>;
export type UpdateContract = z.infer<typeof UpdateContractSchema>;
export type ContractResponse = z.infer<typeof ContractResponseSchema>;
export type ContractListQuery = z.infer<typeof ContractListQuerySchema>;
export type ContractListResponse = z.infer<typeof ContractListResponseSchema>;
export type ActivateContract = z.infer<typeof ActivateContractSchema>;
export type CancelContract = z.infer<typeof CancelContractSchema>;
//# sourceMappingURL=contract-contracts.d.ts.map