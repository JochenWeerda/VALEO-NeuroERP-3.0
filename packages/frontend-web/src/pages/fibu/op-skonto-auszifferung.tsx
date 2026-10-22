import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'fibu/op-skonto-auszifferung',
  'fibu-op-skonto-auszifferung',
  () => import('./fibu/op-skonto-auszifferung-legacy'),
)
