import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'personal/schulung-neu',
  'personal-schulung-neu',
  () => import('./personal/schulung-neu-legacy'),
)
