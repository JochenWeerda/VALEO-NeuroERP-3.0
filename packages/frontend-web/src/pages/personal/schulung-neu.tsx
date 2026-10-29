import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'personal/schulung-neu',
  'personal-schulung-neu',
  () => import('./schulung-neu-legacy'),
)
