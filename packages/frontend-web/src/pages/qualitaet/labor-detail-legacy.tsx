import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'qualitaet/labor-auftrag',
  'qualitaet-labor-stamm',
  () => import('./detail-legacy'),
)
