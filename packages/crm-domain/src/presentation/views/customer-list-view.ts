export interface CustomerListItem {
  id: string;
  name: string;
  customerNumber: string;
  status: string;
  segment: string;
  creditLimit: number;
}

export interface CustomerListViewModel {
  title: string;
  actions: Array<{ label: string; action: string }>;
  rows: CustomerListItem[];
}

export function buildCustomerListViewModel(customers: CustomerListItem[]): CustomerListViewModel {
  return {
    title: 'Customers',
    actions: [
      { label: 'Refresh', action: 'refresh' },
      { label: 'New Customer', action: 'create' },
    ],
    rows: customers,
  };
}
