import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'crm/vertreterstamm',
  'crm-vertreterstamm',
  () => import('./crm/vertreterstamm-legacy'),
)
