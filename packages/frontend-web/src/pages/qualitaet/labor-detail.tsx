import { createStammNativeDetailPage } from '@/components/mask-builder'

/**
 * Native Stamm + Create: ScreenDefinition qualitaet/labor-detail mit creation-Block
 * (POST /api/v1/qualitaet/labor-auftraege). Listen-ID qualitaet/labor-auftrag bleibt Liste.
 */
export default createStammNativeDetailPage(
  'qualitaet/labor-detail',
  'qualitaet-labor-detail',
)
