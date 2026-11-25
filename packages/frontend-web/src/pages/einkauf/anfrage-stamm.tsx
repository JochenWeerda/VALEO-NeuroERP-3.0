import { createStammNativeDetailPage } from '@/components/mask-builder'

/**
 * Native Stamm + Create: ScreenDefinition einkauf/anfrage mit creation-Block
 * (POST /api/v1/einkauf/anfragen). Ohne legacyImport → UniversalNativeCreatePage.
 */
export default createStammNativeDetailPage(
  'einkauf/anfrage',
  'einkauf-anfrage-stamm',
)
