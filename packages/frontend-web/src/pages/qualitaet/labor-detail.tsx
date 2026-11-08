import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'qualitaet/labor-detail',
  'qualitaet-labor-detail',
  () => import('./labor-detail-legacy'),
)
