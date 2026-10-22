import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'fibu/stammdaten',
  'fibu-stammdaten',
  () => import('./fibu/stammdaten-legacy'),
)
