import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider, createBrowserRouter } from 'react-router-dom'
import AppLayout from './layouts/DashboardLayout'
import AnalyticsDashboard from './pages/analytics'
import ContractsPanel from './pages/contracts'
import PricingPanel from './pages/pricing.tsx'
import InventoryPanel from './pages/inventory.tsx'
import WeighingPanel from './pages/weighing.tsx'
import SalesPanel from './pages/sales.tsx'
import DocumentPanel from './pages/document.tsx'
import PolicyManagerPage from './pages/policy-manager'
import SalesOrderEditorPage from './pages/sales/order-editor'
import SalesDeliveryEditorPage from './pages/sales/delivery-editor'
import SalesInvoiceEditorPage from './pages/sales/invoice-editor'
import { ToastProvider } from '@/components/ui/toast-provider'
import './index.css'

const queryClient = new QueryClient()

const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <AnalyticsDashboard /> },
      { path: 'analytics', element: <AnalyticsDashboard /> },
      { path: 'contracts', element: <ContractsPanel /> },
      { path: 'pricing', element: <PricingPanel /> },
      { path: 'inventory', element: <InventoryPanel /> },
      { path: 'weighing', element: <WeighingPanel /> },
      { path: 'sales', element: <SalesPanel /> },
      { path: 'document', element: <DocumentPanel /> },
      { path: 'policies', element: <PolicyManagerPage /> },
      { path: 'sales/order', element: <SalesOrderEditorPage /> },
      { path: 'sales/delivery', element: <SalesDeliveryEditorPage /> },
      { path: 'sales/invoice', element: <SalesInvoiceEditorPage /> },
    ],
  },
])

if (typeof document !== 'undefined') {
  const rootElement = document.getElementById('root')
  if (rootElement) {
    ReactDOM.createRoot(rootElement).render(
      <React.StrictMode>
        <QueryClientProvider client={queryClient}>
          <ToastProvider>
            <RouterProvider router={router} />
          </ToastProvider>
        </QueryClientProvider>
      </React.StrictMode>,
    )
  }
}