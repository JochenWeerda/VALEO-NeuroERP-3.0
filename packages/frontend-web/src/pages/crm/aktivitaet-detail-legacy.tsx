import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'crm/aktivitaet',
  'crm-aktivitaet-stamm',
  () => import('./detail-legacy'),
)
