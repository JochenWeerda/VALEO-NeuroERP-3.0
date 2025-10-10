import { type PriceListItem, priceList } from './data';

export async function listPriceItems(): Promise<PriceListItem[]> {
  return priceList;
}

export async function updatePriceItem(updated: PriceListItem): Promise<PriceListItem> {
  const index = priceList.findIndex((item) => item.sku === updated.sku);
  if (index === -1) {
    throw new Error(`Price item ${updated.sku} not found`);
  }

  priceList[index] = {
    ...updated,
    tiers: [...updated.tiers],
  };

  return priceList[index];
}
