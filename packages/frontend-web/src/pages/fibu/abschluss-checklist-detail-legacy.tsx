import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'fibu/abschluss-checklist',
  'fibu-abschluss-checklist-stamm',
  () => import('./detail-legacy'),
)
