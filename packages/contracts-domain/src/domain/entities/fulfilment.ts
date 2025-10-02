import { z } from 'zod';

// Schema
export const FulfilmentSchema = z.object({
  contractId: z.string().uuid(),
  tenantId: z.string(),
  deliveredQty: z.number().default(0),
  pricedQty: z.number().default(0),
  invoicedQty: z.number().default(0),
  openQty: z.number(),
  avgPrice: z.number().optional(),
  timeline: z.array(z.object({
    event: z.string(),
    timestamp: z.string().datetime(),
    qty: z.number().optional(),
    price: z.number().optional(),
    notes: z.string().optional(),
  })).default([]),
  lastUpdated: z.date().optional(),
});

// Entity interface
export interface FulfilmentEntity {
  contractId: string;
  tenantId: string;
  deliveredQty: number;
  pricedQty: number;
  invoicedQty: number;
  openQty: number;
  avgPrice?: number;
  timeline: Array<{
    event: string;
    timestamp: Date;
    qty?: number;
    price?: number;
    notes?: string;
  }>;
  lastUpdated: Date;
}

// Entity implementation
export class Fulfilment implements FulfilmentEntity {
  public contractId: string;
  public tenantId: string;
  public deliveredQty: number;
  public pricedQty: number;
  public invoicedQty: number;
  public openQty: number;
  public avgPrice?: number;
  public timeline: Array<{
    event: string;
    timestamp: Date;
    qty?: number;
    price?: number;
    notes?: string;
  }>;
  public lastUpdated: Date;

  constructor(props: FulfilmentEntity) {
    this.contractId = props.contractId;
    this.tenantId = props.tenantId;
    this.deliveredQty = props.deliveredQty;
    this.pricedQty = props.pricedQty;
    this.invoicedQty = props.invoicedQty;
    this.openQty = props.openQty;
    if (props.avgPrice) this.avgPrice = props.avgPrice;
    this.timeline = props.timeline;
    this.lastUpdated = props.lastUpdated;
  }

  addDelivery(qty: number, notes?: string): void {
    this.deliveredQty += qty;
    this.openQty -= qty;
    const timelineEntry: any = {
      event: 'DELIVERY',
      timestamp: new Date(),
      qty,
    };
    if (notes) timelineEntry.notes = notes;
    this.timeline.push(timelineEntry);
    this.lastUpdated = new Date();
  }

  addPricing(qty: number, price: number, notes?: string): void {
    this.pricedQty += qty;
    const timelineEntry: any = {
      event: 'PRICING',
      timestamp: new Date(),
      qty,
      price,
    };
    if (notes) timelineEntry.notes = notes;
    this.timeline.push(timelineEntry);
    this.updateAveragePrice();
    this.lastUpdated = new Date();
  }

  addInvoicing(qty: number, notes?: string): void {
    this.invoicedQty += qty;
    const timelineEntry: any = {
      event: 'INVOICING',
      timestamp: new Date(),
      qty,
    };
    if (notes) timelineEntry.notes = notes;
    this.timeline.push(timelineEntry);
    this.lastUpdated = new Date();
  }

  private updateAveragePrice(): void {
    // Calculate weighted average price based on timeline
    const pricedEvents = this.timeline.filter(t => t.event === 'PRICING' && t.price && t.qty);
    if (pricedEvents.length === 0) return;

    const totalValue = pricedEvents.reduce((sum, event) => sum + (event.price! * event.qty!), 0);
    const totalQty = pricedEvents.reduce((sum, event) => sum + event.qty!, 0);

    this.avgPrice = totalValue / totalQty;
  }

  getFulfilmentPercentage(): number {
    const totalContracted = this.deliveredQty + this.openQty;
    return totalContracted > 0 ? (this.deliveredQty / totalContracted) * 100 : 0;
  }

  isFullyFulfilled(): boolean {
    return this.openQty === 0;
  }
}