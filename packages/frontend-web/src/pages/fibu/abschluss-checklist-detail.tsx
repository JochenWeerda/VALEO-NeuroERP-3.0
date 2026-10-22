import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'fibu/abschluss-checklist-detail',
  'fibu-abschluss-checklist-detail',
  () => import('./fibu/abschluss-checklist-detail-legacy'),
)
