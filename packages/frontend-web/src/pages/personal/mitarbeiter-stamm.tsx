import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'personal/mitarbeiter/neu',
  'personal-mitarbeiter-neu',
  () => import('./mitarbeiter-stamm-legacy'),
)
