import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'fibu/abschluss-checklist-detail',
  'fibu-abschluss-checklist-detail',
  () => import('./abschluss-checklist-detail-legacy'),
)
