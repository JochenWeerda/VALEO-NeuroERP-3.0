import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'agrar/duenger',
  'agrar-duenger-stamm',
  () => import('../duenger-stamm-legacy'),
)
