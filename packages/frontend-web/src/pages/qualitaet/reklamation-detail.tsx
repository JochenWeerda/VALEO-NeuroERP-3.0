import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'qualitaet/reklamation',
  'qualitaet-reklamation-detail',
  () => import('./reklamation-detail-legacy'),
)
