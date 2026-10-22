import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'qualitaet/labor-detail',
  'qualitaet-labor-detail',
  () => import('./qualitaet/labor-detail-legacy'),
)
