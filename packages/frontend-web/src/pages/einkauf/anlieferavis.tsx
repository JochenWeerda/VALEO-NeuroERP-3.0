import { createStammNativeDetailPage } from '@/components/mask-builder'

/**
 * Native Stamm + Create: ScreenDefinition einkauf/anlieferavis mit creation-Block
 * (POST /api/v1/einkauf/anlieferavis). Ohne legacyImport → UniversalNativeCreatePage.
 */
export default createStammNativeDetailPage(
  'einkauf/anlieferavis',
  'einkauf-anlieferavis',
)
