/**
 * Lazy-Loaded Pages für Code-Splitting
 * Reduziert Initial-Bundle-Size
 */

import { lazy } from 'react'

// Sales
export const SalesPage = lazy(() => import('./sales'))
export const ContractsPage = lazy(() => import('./contracts'))

// Inventory
export const InventoryPage = lazy(() => import('./inventory'))

// Documents
export const DocumentPage = lazy(() => import('./document'))

// Pricing
export const PricingPage = lazy(() => import('./pricing'))

// Weighing
export const WeighingPage = lazy(() => import('./weighing'))

// Public
export const VerifyPage = lazy(() => import('./public/verify'))

// Loading Component
export function PageLoader() {
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  )
}

