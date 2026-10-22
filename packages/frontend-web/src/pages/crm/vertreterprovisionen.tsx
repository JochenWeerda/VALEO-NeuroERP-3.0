import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'crm/vertreterprovisionen',
  'crm-vertreterprovisionen',
  () => import('./vertreterprovisionen-legacy'),
)
