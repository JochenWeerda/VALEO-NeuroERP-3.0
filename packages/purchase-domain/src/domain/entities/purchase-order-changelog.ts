/**
 * Purchase Order Change Log
 * Tracks all modifications to purchase orders for audit and compliance.
 * GoBD-compliant: immutable, timestamped, user-tracked.
 */

import { randomUUID } from 'crypto';

export enum ChangeType {
  CREATED = 'CREATED',
  STATUS_CHANGED = 'STATUS_CHANGED',
  ITEMS_MODIFIED = 'ITEMS_MODIFIED',
  HEADER_MODIFIED = 'HEADER_MODIFIED',
  APPROVED = 'APPROVED',
  ORDERED = 'ORDERED',
  PARTIALLY_DELIVERED = 'PARTIALLY_DELIVERED',
  DELIVERED = 'DELIVERED',
  CANCELLED = 'CANCELLED',
  REVERTED = 'REVERTED',
}

export interface FieldChange {
  field: string;
  oldValue: string | number | null;
  newValue: string | number | null;
}

export interface ChangeLogEntry {
  readonly id: string;
  readonly purchaseOrderId: string;
  readonly purchaseOrderNumber: string;
  readonly tenantId: string;
  readonly changeType: ChangeType;
  readonly version: number;
  readonly userId: string;
  readonly userName?: string;
  readonly timestamp: Date;
  readonly reason?: string;
  readonly fieldChanges: FieldChange[];
  readonly snapshot?: Record<string, unknown>; // Full PO snapshot at this point
}

export class PurchaseOrderChangeLog {
  private entries: ChangeLogEntry[] = [];

  constructor(
    private readonly purchaseOrderId: string,
    private readonly purchaseOrderNumber: string,
    private readonly tenantId: string,
  ) {}

  public addEntry(
    changeType: ChangeType,
    version: number,
    userId: string,
    fieldChanges: FieldChange[] = [],
    reason?: string,
    snapshot?: Record<string, unknown>,
    userName?: string,
  ): ChangeLogEntry {
    const entry: ChangeLogEntry = {
      id: randomUUID(),
      purchaseOrderId: this.purchaseOrderId,
      purchaseOrderNumber: this.purchaseOrderNumber,
      tenantId: this.tenantId,
      changeType,
      version,
      userId,
      userName,
      timestamp: new Date(),
      reason,
      fieldChanges,
      snapshot,
    };
    this.entries.push(entry);
    return entry;
  }

  public getEntries(): readonly ChangeLogEntry[] {
    return [...this.entries];
  }

  public getLatestEntry(): ChangeLogEntry | undefined {
    return this.entries[this.entries.length - 1];
  }

  public loadEntries(entries: ChangeLogEntry[]): void {
    this.entries = [...entries];
  }

  /**
   * Compare two PO snapshots and return the list of field changes.
   */
  static diffSnapshots(
    before: Record<string, unknown>,
    after: Record<string, unknown>,
    fieldsToTrack: string[] = [
      'status', 'subject', 'supplierId', 'deliveryDate',
      'paymentTerms', 'currency', 'notes', 'subtotalNet',
      'totalTax', 'totalGross', 'contactPerson',
    ],
  ): FieldChange[] {
    const changes: FieldChange[] = [];
    for (const field of fieldsToTrack) {
      const oldVal = before[field] ?? null;
      const newVal = after[field] ?? null;
      if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
        changes.push({
          field,
          oldValue: oldVal as string | number | null,
          newValue: newVal as string | number | null,
        });
      }
    }
    return changes;
  }
}

