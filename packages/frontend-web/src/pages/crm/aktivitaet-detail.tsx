import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'crm/aktivitaet-detail',
  'crm-aktivitaet-detail',
  () => import('./aktivitaet-detail-legacy'),
)
