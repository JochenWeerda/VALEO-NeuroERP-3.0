import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'stammdaten/individuelle-artikelnummern',
  'stammdaten-individuelle-artikelnummern',
  () => import('./individuelle-artikelnummern-legacy'),
)
