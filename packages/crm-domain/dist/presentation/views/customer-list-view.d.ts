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
    actions: Array<{
        label: string;
        action: string;
    }>;
    rows: CustomerListItem[];
}
export declare function buildCustomerListViewModel(customers: CustomerListItem[]): CustomerListViewModel;
//# sourceMappingURL=customer-list-view.d.ts.map