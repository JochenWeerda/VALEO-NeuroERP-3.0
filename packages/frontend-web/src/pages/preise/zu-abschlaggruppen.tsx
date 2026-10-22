import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'preise/zu-abschlaggruppen',
  'preise-zu-abschlaggruppen',
  () => import('./zu-abschlaggruppen-legacy'),
)
