"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildCustomerListViewModel = buildCustomerListViewModel;
function buildCustomerListViewModel(customers) {
    return {
        title: 'Customers',
        actions: [
            { label: 'Refresh', action: 'refresh' },
            { label: 'New Customer', action: 'create' },
        ],
        rows: customers,
    };
}
