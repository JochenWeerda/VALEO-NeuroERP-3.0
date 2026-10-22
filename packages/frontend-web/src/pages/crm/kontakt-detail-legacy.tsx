import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'crm/kontakt',
  'crm-kontakt-stamm',
  () => import('./detail-legacy'),
)
