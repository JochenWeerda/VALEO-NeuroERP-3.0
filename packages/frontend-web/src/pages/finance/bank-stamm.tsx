import { createStammNativeDetailPage } from '@/components/mask-builder'

/**
 * Alias-Route: gleiche Native-Create-Paritaet wie bankkonten-stamm
 * (ScreenDefinition finance/bankkonto → POST /api/v1/banken/konten).
 */
export default createStammNativeDetailPage(
  'finance/bankkonto',
  'finance-bank-stamm',
)
