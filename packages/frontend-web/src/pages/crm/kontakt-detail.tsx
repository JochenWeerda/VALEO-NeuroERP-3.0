import { createStammNativeDetailPage } from '@/components/mask-builder'

/**
 * Native Stamm + Create: ScreenDefinition crm/kontakt mit creation-Block
 * (POST /api/v1/crm/contacts/, nested data.id).
 * Route /crm/kontakte/new und /crm/kontakt/:id nutzen dieselbe Page.
 */
export default createStammNativeDetailPage(
  'crm/kontakt',
  'crm-kontakt-detail',
)
