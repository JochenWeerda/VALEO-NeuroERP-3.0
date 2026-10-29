import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'agribusiness/field-service-tasks/neu',
  'agribusiness-field-service-tasks-neu',
  () => import('./field-service-task-neu-legacy'),
)
