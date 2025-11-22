import { z } from 'zod';

// Enhanced schema with quality and delivery tracking
export const FulfilmentSchema = z.object({
  contractId: z.string().uuid(),
  tenantId: z.string(),
  deliveredQty: z.number().default(0),
  pricedQty: z.number().default(0),
  invoicedQty: z.number().default(0),
  openQty: z.number(),
  avgPrice: z.number().optional(),
  qualityScore: z.number().min(0).max(100).optional(), // Overall quality rating
  onTimeDeliveryRate: z.number().min(0).max(100).optional(), // Percentage of on-time deliveries
  deliverySchedule: z.array(z.object({
    plannedDate: z.string().datetime(),
    actualDate: z.string().datetime().optional(),
    qty: z.number(),
    status: z.enum(['PENDING', 'DELIVERED', 'DELAYED', 'CANCELLED']),
    qualityCheck: z.object({
      passed: z.boolean(),
      score: z.number().min(0).max(100).optional(),
      notes: z.string().optional(),
      inspector: z.string().optional(),
      inspectionDate: z.string().datetime().optional(),
    }).optional(),
  })).default([]),
  timeline: z.array(z.object({
    event: z.string(),
    timestamp: z.string().datetime(),
    qty: z.number().optional(),
    price: z.number().optional(),
    notes: z.string().optional(),
    qualityData: z.object({
      score: z.number().optional(),
      issues: z.array(z.string()).optional(),
    }).optional(),
    deliveryData: z.object({
      deliveryNote: z.string().optional(),
      batchNumbers: z.array(z.string()).optional(),
      storageLocation: z.string().optional(),
    }).optional(),
  })).default([]),
  lastUpdated: z.date().optional(),
});

// Enhanced entity interface
export interface FulfilmentEntity {
  contractId: string;
  tenantId: string;
  deliveredQty: number;
  pricedQty: number;
  invoicedQty: number;
  openQty: number;
  avgPrice?: number;
  qualityScore?: number;
  onTimeDeliveryRate?: number;
  deliverySchedule: Array<{
    plannedDate: Date;
    actualDate?: Date;
    qty: number;
    status: 'PENDING' | 'DELIVERED' | 'DELAYED' | 'CANCELLED';
    qualityCheck?: {
      passed: boolean;
      score?: number;
      notes?: string;
      inspector?: string;
      inspectionDate?: Date;
    };
  }>;
  timeline: Array<{
    event: string;
    timestamp: Date;
    qty?: number;
    price?: number;
    notes?: string;
    qualityData?: {
      score?: number;
      issues?: string[];
    };
    deliveryData?: {
      deliveryNote?: string;
      batchNumbers?: string[];
      storageLocation?: string;
    };
  }>;
  lastUpdated: Date;
}

// Enhanced entity implementation
export class Fulfilment implements FulfilmentEntity {
  public contractId: string;
  public tenantId: string;
  public deliveredQty: number;
  public pricedQty: number;
  public invoicedQty: number;
  public openQty: number;
  public avgPrice?: number;
  public qualityScore?: number;
  public onTimeDeliveryRate?: number;
  public deliverySchedule: Array<{
    plannedDate: Date;
    actualDate?: Date;
    qty: number;
    status: 'PENDING' | 'DELIVERED' | 'DELAYED' | 'CANCELLED';
    qualityCheck?: {
      passed: boolean;
      score?: number;
      notes?: string;
      inspector?: string;
      inspectionDate?: Date;
    };
  }>;
  public timeline: Array<{
    event: string;
    timestamp: Date;
    qty?: number;
    price?: number;
    notes?: string;
    qualityData?: {
      score?: number;
      issues?: string[];
    };
    deliveryData?: {
      deliveryNote?: string;
      batchNumbers?: string[];
      storageLocation?: string;
    };
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
    if (props.qualityScore) this.qualityScore = props.qualityScore;
    if (props.onTimeDeliveryRate) this.onTimeDeliveryRate = props.onTimeDeliveryRate;
    this.deliverySchedule = props.deliverySchedule;
    this.timeline = props.timeline;
    this.lastUpdated = props.lastUpdated;
  }

  addDelivery(qty: number, deliveryData?: {
    deliveryNote?: string;
    batchNumbers?: string[];
    storageLocation?: string;
    qualityData?: {
      score?: number;
      issues?: string[];
    };
  }, notes?: string): void {
    this.deliveredQty += qty;
    this.openQty -= qty;

    const timelineEntry: any = {
      event: 'DELIVERY',
      timestamp: new Date(),
      qty,
    };

    if (deliveryData) {
      timelineEntry.deliveryData = deliveryData;
      if (deliveryData.qualityData) {
        timelineEntry.qualityData = deliveryData.qualityData;
        this.updateQualityScore();
      }
    }

    if (notes) timelineEntry.notes = notes;
    this.timeline.push(timelineEntry);
    this.updateDeliveryMetrics();
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

  private updateQualityScore(): void {
    // Calculate overall quality score based on delivery quality checks
    const qualityEvents = this.timeline.filter(t => t.qualityData?.score !== undefined);
    if (qualityEvents.length === 0) return;

    const totalScore = qualityEvents.reduce((sum, event) => sum + (event.qualityData!.score || 0), 0);
    this.qualityScore = totalScore / qualityEvents.length;
  }

  private updateDeliveryMetrics(): void {
    // Calculate on-time delivery rate based on delivery schedule
    const completedDeliveries = this.deliverySchedule.filter(d => d.status === 'DELIVERED');
    if (completedDeliveries.length === 0) return;

    const onTimeDeliveries = completedDeliveries.filter(delivery => {
      if (!delivery.actualDate) return false;
      return delivery.actualDate <= delivery.plannedDate;
    });

    this.onTimeDeliveryRate = (onTimeDeliveries.length / completedDeliveries.length) * 100;
  }

  getFulfilmentPercentage(): number {
    const totalContracted = this.deliveredQty + this.openQty;
    return totalContracted > 0 ? (this.deliveredQty / totalContracted) * 100 : 0;
  }

  isFullyFulfilled(): boolean {
    return this.openQty === 0;
  }

  // Enhanced methods for delivery schedule management
  addDeliveryScheduleItem(plannedDate: Date, qty: number): void {
    this.deliverySchedule.push({
      plannedDate,
      qty,
      status: 'PENDING'
    });
    this.lastUpdated = new Date();
  }

  updateDeliveryStatus(index: number, status: 'PENDING' | 'DELIVERED' | 'DELAYED' | 'CANCELLED', actualDate?: Date): void {
    if (index >= 0 && index < this.deliverySchedule.length) {
      const delivery = this.deliverySchedule[index];
      if (delivery) {
        delivery.status = status;
        if (actualDate) {
          delivery.actualDate = actualDate;
        }
        this.updateDeliveryMetrics();
        this.lastUpdated = new Date();
      }
    }
  }

  addQualityCheck(deliveryIndex: number, qualityCheck: {
    passed: boolean;
    score?: number;
    notes?: string;
    inspector?: string;
  }): void {
    if (deliveryIndex >= 0 && deliveryIndex < this.deliverySchedule.length) {
      const delivery = this.deliverySchedule[deliveryIndex];
      if (delivery) {
        delivery.qualityCheck = {
          ...qualityCheck,
          inspectionDate: new Date()
        };
        this.updateQualityScore();
        this.lastUpdated = new Date();
      }
    }
  }

  getDelayedDeliveries(): Array<{ plannedDate: Date; delayDays: number }> {
    return this.deliverySchedule
      .filter(d => d.status === 'DELAYED' && d.actualDate && d.plannedDate)
      .map(d => ({
        plannedDate: d.plannedDate,
        delayDays: Math.ceil((d.actualDate!.getTime() - d.plannedDate.getTime()) / (1000 * 60 * 60 * 24))
      }));
  }

  getUpcomingDeliveries(daysAhead: number = 7): Array<{ plannedDate: Date; qty: number }> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() + daysAhead);

    return this.deliverySchedule
      .filter(d => d.status === 'PENDING' && d.plannedDate <= cutoffDate)
      .map(d => ({
        plannedDate: d.plannedDate,
        qty: d.qty
      }))
      .sort((a, b) => a.plannedDate.getTime() - b.plannedDate.getTime());
  }

  getFulfilmentSummary(): {
    totalContracted: number;
    delivered: number;
    remaining: number;
    fulfilmentRate: number;
    qualityScore?: number | undefined;
    onTimeDeliveryRate?: number | undefined;
    nextDelivery?: Date | undefined;
  } {
    const totalContracted = this.deliveredQty + this.openQty;
    const fulfilmentRate = totalContracted > 0 ? (this.deliveredQty / totalContracted) * 100 : 0;

    const nextDelivery = this.deliverySchedule
      .filter(d => d.status === 'PENDING')
      .sort((a, b) => a.plannedDate.getTime() - b.plannedDate.getTime())[0]?.plannedDate;

    return {
      totalContracted,
      delivered: this.deliveredQty,
      remaining: this.openQty,
      fulfilmentRate,
      qualityScore: this.qualityScore,
      onTimeDeliveryRate: this.onTimeDeliveryRate,
      nextDelivery
    };
  }
}