import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'einkauf/supplier',
  'crm-lieferanten-stamm',
  () => import('./lieferanten-stamm-legacy'),
)
