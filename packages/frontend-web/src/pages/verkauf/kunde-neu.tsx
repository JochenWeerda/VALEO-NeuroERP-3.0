import { lazy, Suspense } from 'react'
import { Navigate } from 'react-router-dom'
import { ENABLE_CUSTOMER_MASK_BUILDER_FORM } from '@/features/crm-masks/customer-mask-support'

const KundeNeuMaskBuilderPage = lazy(() => import('./kunde-neu/KundeNeuMaskBuilderPage'))

/**
 * Ohne Mask-Builder-Flag: kanonische Neuanlage unter /verkauf/kunde/neu (Kundenstamm).
 * Mit VITE_ENABLE_MASK_BUILDER_CUSTOMER_FORM=true: experimentelle CRM-Maske unter dieser URL.
 */
export default function KundeNeuPage(): JSX.Element {
  if (!ENABLE_CUSTOMER_MASK_BUILDER_FORM) {
    return <Navigate to="/verkauf/kunde/neu" replace />
  }
  return (
    <Suspense fallback={null}>
      <KundeNeuMaskBuilderPage />
    </Suspense>
  )
}
