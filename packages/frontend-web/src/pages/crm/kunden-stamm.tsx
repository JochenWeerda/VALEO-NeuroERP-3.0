import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'crm/customer-360',
  'crm-kunden-stamm',
  () => import('./kunden-stamm-legacy'),
)
