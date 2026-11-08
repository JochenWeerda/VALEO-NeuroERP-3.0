/**
 * Kunden-Stamm Modern
 * Schalter: native Maske (UniversalMaskRuntime) vor Mask-Builder-Formular vor Legacy.
 */

import { lazy, Suspense } from 'react'
import {
  ENABLE_CUSTOMER_MASK_BUILDER_FORM,
  ENABLE_UNIVERSAL_MASK_CUSTOMER,
} from '@/features/crm-masks/customer-mask-support'

const CustomerMaskEditPage = lazy(() => import('./kunden-stamm-modern/CustomerMaskEditPage'))
const LegacyKundenStammModern = lazy(() => import('./kunden-stamm-modern/LegacyKundenStammModern'))
const Customer360NativePage = lazy(() => import('./customer-360-native'))

export default function KundenStammModern(): JSX.Element {
  const PageComponent = ENABLE_UNIVERSAL_MASK_CUSTOMER
    ? Customer360NativePage
    : ENABLE_CUSTOMER_MASK_BUILDER_FORM
    ? CustomerMaskEditPage
    : LegacyKundenStammModern

  return (
    <Suspense fallback={null}>
      <PageComponent />
    </Suspense>
  )
}
