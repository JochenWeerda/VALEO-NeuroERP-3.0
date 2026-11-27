import { createStammNativeDetailPage } from '@/components/mask-builder'

/**
 * Native Stamm + Create: ScreenDefinition finance/bankkonto mit creation-Block
 * (POST /api/v1/banken/konten). Ohne legacyImport → UniversalNativeCreatePage.
 */
export default createStammNativeDetailPage(
  'finance/bankkonto',
  'finance-bankkonten-stamm',
)
