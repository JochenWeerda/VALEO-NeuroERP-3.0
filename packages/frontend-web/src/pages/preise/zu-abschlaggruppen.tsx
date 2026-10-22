import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'preise/zu-abschlaggruppen',
  'preise-zu-abschlaggruppen',
  () => import('./preise/zu-abschlaggruppen-legacy'),
)
