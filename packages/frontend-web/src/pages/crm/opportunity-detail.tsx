import { createStammNativeDetailPage } from '@/components/mask-builder'

/**
 * Native Stamm + Create: ScreenDefinition crm/opportunity mit creation-Block
 * (POST /api/v1/crm/opportunities/). Ohne legacyImport → UniversalNativeCreatePage.
 */
export default createStammNativeDetailPage(
  'crm/opportunity',
  'crm-opportunity-detail',
)
