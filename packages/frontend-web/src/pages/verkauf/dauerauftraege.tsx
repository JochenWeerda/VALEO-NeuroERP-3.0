import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'verkauf/dauerauftraege',
  'verkauf-dauerauftraege',
  () => import('./verkauf/dauerauftraege-legacy'),
)
