import { createStammNativeDetailPage } from '@/components/mask-builder'

/**
 * Native Stamm + Create: ScreenDefinition einkauf/angebot mit creation-Block
 * (POST /api/v1/einkauf/angebote). Ohne legacyImport → UniversalNativeCreatePage.
 */
export default createStammNativeDetailPage(
  'einkauf/angebot',
  'einkauf-angebot-stamm',
)
