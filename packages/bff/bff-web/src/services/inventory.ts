import { type InventoryRecord, inventory } from './data';

export interface StockItem {
  sku: string;
  name: string;
  qty: number;
  uom: string;
  location?: string;
}

export async function listInventory(): Promise<StockItem[]> {
  return inventory.map((item) => ({
    sku: item.sku,
    name: item.name,
    qty: item.quantity,
    uom: item.uom,
    location: item.location,
  }));
}

export async function adjustInventoryQuantity(sku: string, delta: number): Promise<StockItem> {
  const record = inventory.find((item: InventoryRecord) => item.sku === sku);
  if (record === undefined) {
    throw new Error(`SKU ${sku} not found`);
  }

  record.quantity = Math.max(record.quantity + delta, 0);
  return {
    sku: record.sku,
    name: record.name,
    qty: record.quantity,
    uom: record.uom,
    location: record.location,
  };
}

export async function moveInventoryLocation(sku: string, toLocation: string): Promise<StockItem> {
  const record = inventory.find((item: InventoryRecord) => item.sku === sku);
  if (record === undefined) {
    throw new Error(`SKU ${sku} not found`);
  }

  record.location = toLocation;

  return {
    sku: record.sku,
    name: record.name,
    qty: record.quantity,
    uom: record.uom,
    location: record.location,
  };
}
