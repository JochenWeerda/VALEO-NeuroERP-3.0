import { type SalesOrder, salesOrders } from './data';

export async function listSalesOrders(): Promise<SalesOrder[]> {
  return salesOrders;
}
