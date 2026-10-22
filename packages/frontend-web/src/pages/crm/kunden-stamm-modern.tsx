import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'crm/kunden-stamm-modern',
  'crm-kunden-stamm-modern',
  () => import('./crm/kunden-stamm-modern-legacy'),
)
