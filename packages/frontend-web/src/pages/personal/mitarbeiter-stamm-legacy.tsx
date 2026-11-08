import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'personal/mitarbeiter',
  'personal-mitarbeiter-stamm',
  () => import('./stamm-legacy'),
)
