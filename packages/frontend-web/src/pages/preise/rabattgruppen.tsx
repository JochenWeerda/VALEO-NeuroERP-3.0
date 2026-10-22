import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'preise/rabattgruppen',
  'preise-rabattgruppen',
  () => import('./preise/rabattgruppen-legacy'),
)
