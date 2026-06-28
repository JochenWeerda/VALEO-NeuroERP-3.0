import { lazy, Suspense } from 'react'
import { Navigate, useParams } from '@/app/routing/typed-router'
import { isRolloutPilotEnabled } from '@/features/mask-rollouts/rollout-registry'

const UniversalMaskRolloutPilotPage = lazy(
  () => import('@/pages/workflow/mask-rollout/UniversalMaskRolloutPilotPage'),
)

export default function MaskRolloutRoute(): JSX.Element {
  const { screenId, entityId } = useParams<{ screenId?: string; entityId?: string }>()
  const normalizedScreenId = screenId?.replace(/__/g, '/')

  if (!normalizedScreenId || !entityId) {
    return <Navigate to="/" replace />
  }

  if (!isRolloutPilotEnabled(normalizedScreenId)) {
    return (
      <div className="p-6 text-sm text-muted-foreground">
        Rollout Pilot deaktiviert. Setze{' '}
        <code className="rounded bg-muted px-1">VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS=true</code>.
      </div>
    )
  }

  return (
    <Suspense fallback={null}>
      <UniversalMaskRolloutPilotPage screenId={normalizedScreenId} entityId={entityId} />
    </Suspense>
  )
}
