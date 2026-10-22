import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'lager/permanente-inventur',
  'lager-permanente-inventur',
  () => import('./lager/permanente-inventur-legacy'),
)
