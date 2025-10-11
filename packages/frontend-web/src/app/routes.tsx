import { type ComponentType, Suspense, lazy } from 'react'
import { type RouteObject, createBrowserRouter } from 'react-router-dom'
import AppLayout from '@/layouts/DashboardLayout'
import { ErrorBoundary } from '@/shared/errors/ErrorBoundary'
import { PageLoader } from '@/app/PageLoader'

const createLazyRoute = (
  factory: () => Promise<{ default: ComponentType<unknown> }>,
): (() => JSX.Element) => {
  const Component = lazy(factory)
  return function LazyRoute(): JSX.Element {
    return (
      <ErrorBoundary>
        <Suspense fallback={<PageLoader />}>
          <Component />
        </Suspense>
      </ErrorBoundary>
    )
  }
}

const AnalyticsRoute = createLazyRoute(() => import('@/pages/analytics'))
const ContractsRoute = createLazyRoute(() => import('@/pages/contracts'))
const PricingRoute = createLazyRoute(() => import('@/pages/pricing'))
const InventoryRoute = createLazyRoute(() => import('@/pages/inventory'))
const WeighingRoute = createLazyRoute(() => import('@/pages/weighing'))
const SalesRoute = createLazyRoute(() => import('@/pages/sales'))
const DocumentRoute = createLazyRoute(() => import('@/pages/document'))
const PolicyManagerRoute = createLazyRoute(() => import('@/pages/policy-manager'))
const SalesOrderEditorRoute = createLazyRoute(() => import('@/pages/sales/order-editor'))
const SalesDeliveryEditorRoute = createLazyRoute(() => import('@/pages/sales/delivery-editor'))
const SalesInvoiceEditorRoute = createLazyRoute(() => import('@/pages/sales/invoice-editor'))
const SeedListRoute = createLazyRoute(() => import('@/pages/agrar/saatgut/liste'))
const SeedMasterRoute = createLazyRoute(() => import('@/pages/agrar/saatgut/stamm'))
const SeedOrderWizardRoute = createLazyRoute(() => import('@/pages/agrar/saatgut/bestellung'))
const FertilizerListRoute = createLazyRoute(() => import('@/pages/agrar/duenger/liste'))
const FertilizerMasterRoute = createLazyRoute(() => import('@/pages/agrar/duenger/stamm'))

const routeConfig: RouteObject[] = [
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <AnalyticsRoute /> },
      { path: 'analytics', element: <AnalyticsRoute /> },
      { path: 'contracts', element: <ContractsRoute /> },
      { path: 'pricing', element: <PricingRoute /> },
      { path: 'inventory', element: <InventoryRoute /> },
      { path: 'weighing', element: <WeighingRoute /> },
      { path: 'sales', element: <SalesRoute /> },
      { path: 'document', element: <DocumentRoute /> },
      { path: 'policies', element: <PolicyManagerRoute /> },
      { path: 'sales/order', element: <SalesOrderEditorRoute /> },
      { path: 'sales/delivery', element: <SalesDeliveryEditorRoute /> },
      { path: 'sales/invoice', element: <SalesInvoiceEditorRoute /> },
      { path: 'agrar/saatgut', element: <SeedListRoute /> },
      { path: 'agrar/saatgut/stamm', element: <SeedMasterRoute /> },
      { path: 'agrar/saatgut/bestellung', element: <SeedOrderWizardRoute /> },
      { path: 'agrar/duenger', element: <FertilizerListRoute /> },
      { path: 'agrar/duenger/stamm', element: <FertilizerMasterRoute /> },
    ],
  },
]

export const router = createBrowserRouter(routeConfig)

export const routes = routeConfig
