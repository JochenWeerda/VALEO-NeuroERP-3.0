/**
 * Kunden-Stamm Modern
 * Nutzt die L3 Mask-Builder Konfiguration mit responsive UI und AI-Features
 */

import { lazy, Suspense } from 'react'
import {
  ENABLE_CUSTOMER_MASK_BUILDER_FORM,
  ENABLE_UNIVERSAL_MASK_CUSTOMER,
} from '@/features/crm-masks/customer-mask-support'

const CustomerMaskEditPage = lazy(() => import('./kunden-stamm-modern/CustomerMaskEditPage'))
const LegacyKundenStammModern = lazy(() => import('./kunden-stamm-modern/LegacyKundenStammModern'))
const UniversalCustomerMaskPilotPage = lazy(() => import('./kunden-stamm-modern/UniversalCustomerMaskPilotPage'))

export default function KundenStammModern(): JSX.Element {
  const PageComponent = ENABLE_UNIVERSAL_MASK_CUSTOMER
    ? UniversalCustomerMaskPilotPage
    : ENABLE_CUSTOMER_MASK_BUILDER_FORM
    ? CustomerMaskEditPage
    : LegacyKundenStammModern

  return (
    <Suspense fallback={null}>
      <PageComponent />
    </Suspense>
  )
}
