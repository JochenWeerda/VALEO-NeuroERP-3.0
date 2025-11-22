import { z } from 'zod';

// Enums
export const ContractType = {
  BUY: 'Buy',
  SELL: 'Sell',
} as const;

export const CommodityType = {
  WHEAT: 'WHEAT',
  BARLEY: 'BARLEY',
  RAPESEED: 'RAPESEED',
  SOYMEAL: 'SOYMEAL',
  COMPOUND_FEED: 'COMPOUND_FEED',
  FERTILIZER: 'FERTILIZER',
} as const;

export const ContractStatus = {
  DRAFT: 'Draft',
  ACTIVE: 'Active',
  PARTIALLY_FULFILLED: 'PartiallyFulfilled',
  FULFILLED: 'Fulfilled',
  CANCELLED: 'Cancelled',
  DEFAULTED: 'Defaulted',
} as const;

export const PricingMode = {
  FORWARD_CASH: 'FORWARD_CASH',
  BASIS: 'BASIS',
  HTA: 'HTA',
  DEFERRED: 'DEFERRED',
  MIN_PRICE: 'MIN_PRICE',
  FIXED: 'FIXED',
  INDEXED: 'INDEXED',
} as const;

export const ShipmentType = {
  SPOT: 'Spot',
  WINDOW: 'Window',
  CALL_OFF: 'CallOff',
} as const;

export const TitleTransferType = {
  AT_DELIVERY: 'AtDelivery',
  AT_STORAGE: 'AtStorage',
  AT_PRICING: 'AtPricing',
} as const;

// Types
export type ContractTypeValue = typeof ContractType[keyof typeof ContractType];
export type CommodityTypeValue = typeof CommodityType[keyof typeof CommodityType];
export type ContractStatusValue = typeof ContractStatus[keyof typeof ContractStatus];
export type PricingModeValue = typeof PricingMode[keyof typeof PricingMode];
export type ShipmentTypeValue = typeof ShipmentType[keyof typeof ShipmentType];
export type TitleTransferTypeValue = typeof TitleTransferType[keyof typeof TitleTransferType];

// Schemas
export const PricingTermsSchema = z.object({
  mode: z.enum([PricingMode.FORWARD_CASH, PricingMode.BASIS, PricingMode.HTA, PricingMode.DEFERRED, PricingMode.MIN_PRICE, PricingMode.FIXED, PricingMode.INDEXED]),
  referenceMarket: z.enum(['CME', 'EURONEXT', 'CASH_INDEX']).optional(),
  futuresMonth: z.string().optional(),
  basis: z.number().optional(),
  fees: z.object({
    elevator: z.number().optional(),
    optionPremium: z.number().optional(),
  }).optional(),
  fx: z.object({
    pair: z.string(),
    method: z.enum(['SPOT', 'FIXING']),
  }).optional(),
  lastFixingAt: z.string().datetime().optional(),
});

export const DeliveryTermsSchema = z.object({
  shipmentType: z.enum([ShipmentType.SPOT, ShipmentType.WINDOW, ShipmentType.CALL_OFF]),
  parity: z.string().optional(),
  storage: z.object({
    allowed: z.boolean(),
    tariff: z.number().optional(),
    titleTransfer: z.enum([TitleTransferType.AT_DELIVERY, TitleTransferType.AT_STORAGE, TitleTransferType.AT_PRICING]).optional(),
  }).optional(),
  qualitySpecs: z.record(z.string(), z.any()).optional(),
});

export const ContractSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string(),
  contractNo: z.string(),
  type: z.enum([ContractType.BUY, ContractType.SELL]),
  commodity: z.enum([CommodityType.WHEAT, CommodityType.BARLEY, CommodityType.RAPESEED, CommodityType.SOYMEAL, CommodityType.COMPOUND_FEED, CommodityType.FERTILIZER]),
  counterpartyId: z.string(),
  incoterm: z.string().optional(),
  deliveryWindow: z.object({
    from: z.string().datetime(),
    to: z.string().datetime(),
  }),
  qty: z.object({
    unit: z.enum(['t', 'mt']),
    contracted: z.number().positive(),
    tolerance: z.number().min(0).max(20).optional(),
  }),
  pricing: PricingTermsSchema,
  delivery: DeliveryTermsSchema,
  status: z.enum([ContractStatus.DRAFT, ContractStatus.ACTIVE, ContractStatus.PARTIALLY_FULFILLED, ContractStatus.FULFILLED, ContractStatus.CANCELLED, ContractStatus.DEFAULTED]).default(ContractStatus.DRAFT),
  createdAt: z.date().optional(),
  updatedAt: z.date().optional(),
  version: z.number().default(1),
});

// Entity interfaces
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
  documentId?: string | undefined; // Reference to generated contract document
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

// Entity implementation
export class Contract implements ContractEntity {
  public id: string;
  public tenantId: string;
  public contractNo: string;
  public type: ContractTypeValue;
  public commodity: CommodityTypeValue;
  public counterpartyId: string;
  public incoterm?: string;
  public deliveryWindow: { from: Date; to: Date; };
  public qty: { unit: 't' | 'mt'; contracted: number; tolerance?: number | undefined; };
  public pricing: PricingTerms;
  public delivery: DeliveryTerms;
  public status: ContractStatusValue;
  public documentId?: string;
  public createdAt: Date;
  public updatedAt: Date;
  public version: number;

  constructor(props: ContractEntity) {
    this.id = props.id;
    this.tenantId = props.tenantId;
    this.contractNo = props.contractNo;
    this.type = props.type;
    this.commodity = props.commodity;
    this.counterpartyId = props.counterpartyId;
    if (props.incoterm) this.incoterm = props.incoterm;
    this.deliveryWindow = props.deliveryWindow;
    this.qty = props.qty;
    this.pricing = props.pricing;
    this.delivery = props.delivery;
    this.status = props.status;
    if (props.documentId) this.documentId = props.documentId;
    this.createdAt = props.createdAt;
    this.updatedAt = props.updatedAt;
    this.version = props.version;
  }

  activate(): void {
    if (this.status !== ContractStatus.DRAFT) {
      throw new Error('Only draft contracts can be activated');
    }
    this.status = ContractStatus.ACTIVE;
    this.updatedAt = new Date();
    this.version++;
  }

  cancel(): void {
    if (this.status === ContractStatus.FULFILLED || this.status === ContractStatus.CANCELLED) {
      throw new Error('Contract cannot be cancelled in current status');
    }
    this.status = ContractStatus.CANCELLED;
    this.updatedAt = new Date();
    this.version++;
  }

  canBeAmended(): boolean {
    const amendableStatuses: ContractStatusValue[] = [ContractStatus.DRAFT, ContractStatus.ACTIVE, ContractStatus.PARTIALLY_FULFILLED];
    return amendableStatuses.includes(this.status);
  }

  isExpired(): boolean {
    return new Date() > this.deliveryWindow.to;
  }

  getOpenQuantity(): number {
    // This would need to be calculated based on fulfilment data
    // For now, return contracted quantity
    return this.qty.contracted;
  }
}