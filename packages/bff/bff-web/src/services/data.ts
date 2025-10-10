export interface AnalyticsDailySummary {
  date: string;
  revenue: number;
  orders: number;
  returnRate: number;
  stockAvailability: number;
  inventoryLevel: number;
}

export interface ContractRecord {
  id: string;
  title: string;
  status: 'active' | 'closed' | 'draft';
  customer: string;
  amount: number;
  startDate: string;
  endDate: string;
}

export interface InventoryRecord {
  sku: string;
  name: string;
  quantity: number;
  reserved: number;
  location: string;
  category: string;
  unitCost: number;
  uom: string;
}

export interface PriceListItem {
  sku: string;
  name: string;
  currency: string;
  unit: string;
  baseNet: number;
  tiers: Array<{ minQty: number; net: number }>;
}

export interface SalesOrder {
  id: string;
  customer: string;
  status: 'confirmed' | 'draft' | 'shipped';
  total: number;
  createdAt: string;
  fulfillmentEta: string;
  currency: string;
}

export interface WeighingTicket {
  id: string;
  vehicle: string;
  gross: number;
  tare: number;
  net: number;
  material: string;
  ts: string;
  status: 'completed' | 'pending';
}

export const analyticsDailySummary: AnalyticsDailySummary[] = [
  { date: '2024-09-01', revenue: 118_000, orders: 462, returnRate: 0.026, stockAvailability: 95.1, inventoryLevel: 4_600 },
  { date: '2024-09-08', revenue: 121_500, orders: 474, returnRate: 0.024, stockAvailability: 95.6, inventoryLevel: 4_700 },
  { date: '2024-09-15', revenue: 124_300, orders: 481, returnRate: 0.023, stockAvailability: 96.2, inventoryLevel: 4_780 },
  { date: '2024-09-22', revenue: 126_800, orders: 489, returnRate: 0.022, stockAvailability: 96.6, inventoryLevel: 4_850 },
  { date: '2024-09-29', revenue: 129_200, orders: 501, returnRate: 0.019, stockAvailability: 97.0, inventoryLevel: 4_900 },
];

export const contracts: ContractRecord[] = [
  {
    id: 'C-2045',
    title: 'Logistics Services 2024',
    status: 'active',
    customer: 'Valeo Logistics',
    amount: 425_000,
    startDate: '2024-01-01',
    endDate: '2024-12-31',
  },
  {
    id: 'C-2046',
    title: 'Maintenance Agreement',
    status: 'draft',
    customer: 'Alpine Manufacturing',
    amount: 152_000,
    startDate: '2024-03-01',
    endDate: '2025-02-28',
  },
  {
    id: 'C-2047',
    title: 'Cross-Docking Pilot',
    status: 'closed',
    customer: 'Neuro Distribution',
    amount: 96_500,
    startDate: '2023-10-01',
    endDate: '2024-04-30',
  },
];

export const inventory: InventoryRecord[] = [
  {
    sku: 'SKU-1001',
    name: 'Aluminium Housing',
    quantity: 820,
    reserved: 120,
    location: 'A1-01',
    category: 'Chassis',
    unitCost: 42.8,
    uom: 'pcs',
  },
  {
    sku: 'SKU-1002',
    name: 'Servo Motor',
    quantity: 240,
    reserved: 60,
    location: 'B2-14',
    category: 'Drives',
    unitCost: 115.6,
    uom: 'pcs',
  },
  {
    sku: 'SKU-1015',
    name: 'Hydraulic Valve',
    quantity: 640,
    reserved: 80,
    location: 'C3-07',
    category: 'Hydraulics',
    unitCost: 68.2,
    uom: 'pcs',
  },
  {
    sku: 'SKU-1032',
    name: 'Control Unit',
    quantity: 155,
    reserved: 34,
    location: 'E1-02',
    category: 'Electronics',
    unitCost: 482.0,
    uom: 'pcs',
  },
];

export const priceList: PriceListItem[] = [
  {
    sku: 'SKU-1001',
    name: 'Aluminium Housing',
    currency: 'EUR',
    unit: 'pcs',
    baseNet: 89.5,
    tiers: [
      { minQty: 1, net: 89.5 },
      { minQty: 50, net: 84.2 },
      { minQty: 250, net: 79.9 },
    ],
  },
  {
    sku: 'SKU-1002',
    name: 'Servo Motor',
    currency: 'EUR',
    unit: 'pcs',
    baseNet: 129.9,
    tiers: [
      { minQty: 1, net: 129.9 },
      { minQty: 20, net: 123.4 },
      { minQty: 100, net: 118.7 },
    ],
  },
  {
    sku: 'SKU-1032',
    name: 'Control Unit',
    currency: 'EUR',
    unit: 'pcs',
    baseNet: 512.0,
    tiers: [
      { minQty: 1, net: 512.0 },
      { minQty: 10, net: 498.5 },
    ],
  },
];

export const salesOrders: SalesOrder[] = [
  {
    id: 'SO-9821',
    customer: 'Valeo Logistics',
    status: 'confirmed',
    total: 18_250,
    createdAt: '2024-09-22',
    fulfillmentEta: '2024-10-05',
    currency: 'EUR',
  },
  {
    id: 'SO-9822',
    customer: 'Neuro Manufacturing',
    status: 'shipped',
    total: 9_320,
    createdAt: '2024-09-19',
    fulfillmentEta: '2024-09-26',
    currency: 'EUR',
  },
  {
    id: 'SO-9823',
    customer: 'Alpine Rail',
    status: 'confirmed',
    total: 14_780,
    createdAt: '2024-09-25',
    fulfillmentEta: '2024-10-03',
    currency: 'EUR',
  },
  {
    id: 'SO-9824',
    customer: 'Nordic Energy',
    status: 'draft',
    total: 7_650,
    createdAt: '2024-09-28',
    fulfillmentEta: '2024-10-10',
    currency: 'EUR',
  },
];

export const weighingTickets: WeighingTicket[] = [
  {
    id: 'WT-5512',
    vehicle: 'NE-TR-104',
    gross: 42_180,
    tare: 28_960,
    net: 13_220,
    material: 'Steel Coil',
    status: 'completed',
    ts: '2024-09-29T09:45:00Z',
  },
  {
    id: 'WT-5513',
    vehicle: 'VE-NR-881',
    gross: 35_420,
    tare: 26_540,
    net: 8_880,
    material: 'Copper Wire',
    status: 'pending',
    ts: '2024-09-29T10:12:00Z',
  },
  {
    id: 'WT-5514',
    vehicle: 'AG-PL-623',
    gross: 39_760,
    tare: 28_560,
    net: 11_200,
    material: 'Aluminium Blocks',
    status: 'completed',
    ts: '2024-09-28T17:05:00Z',
  },
];
