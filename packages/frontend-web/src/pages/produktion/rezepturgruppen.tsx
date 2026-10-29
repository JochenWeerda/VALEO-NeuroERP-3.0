import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'produktion/rezepturgruppen',
  'produktion-rezepturgruppen',
  () => import('./rezepturgruppen-legacy'),
)
