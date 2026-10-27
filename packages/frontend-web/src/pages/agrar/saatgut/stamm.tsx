import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'agrar/saatgut',
  'agrar-saatgut-stamm',
  () => import('../saatgut-stamm-legacy'),
)
