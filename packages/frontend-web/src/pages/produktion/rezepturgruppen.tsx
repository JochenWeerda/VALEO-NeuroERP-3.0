import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'produktion/rezepturgruppen',
  'produktion-rezepturgruppen',
  () => import('./produktion/rezepturgruppen-legacy'),
)
