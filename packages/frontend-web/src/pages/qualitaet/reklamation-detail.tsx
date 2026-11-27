import { createStammNativeDetailPage } from '@/components/mask-builder'

/**
 * Native Stamm + Create: ScreenDefinition qualitaet/reklamation mit creation-Block
 * (POST /api/v1/reklamationen, responseIdKey=reklamation_id).
 */
export default createStammNativeDetailPage(
  'qualitaet/reklamation',
  'qualitaet-reklamation-detail',
)
