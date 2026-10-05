import { useNavigate } from '@/app/routing/typed-router'
import { CaptureScreenHost } from '@/masks/capture-screen-host'
import { logistikFrachtbriefScreen } from '@/masks/capture-screens'

/** Transportbeleg aus der ScreenDefinition `logistik/frachtbrief`. */
export default function FrachtbriefePage(): JSX.Element {
  const navigate = useNavigate()
  return (
    <CaptureScreenHost
      screenId="logistik/frachtbrief"
      fallback={logistikFrachtbriefScreen}
      loading="Frachtbriefe werden geladen…"
      error="Frachtbriefe konnten nicht geladen werden."
      onAction={async (key) => {
        if (key === 'verladung') navigate('/verladung')
      }}
    />
  )
}
