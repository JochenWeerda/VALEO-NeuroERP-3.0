import { createStammNativeDetailPage } from '@/components/mask-builder'

/**
 * Native Stamm + Create: ScreenDefinition finance/kreditor mit creation-Block
 * (POST /api/v1/finance/creditors). Ohne legacyImport → UniversalNativeCreatePage.
 */
export default createStammNativeDetailPage(
  'finance/kreditor',
  'finance-kreditoren-stamm',
)
