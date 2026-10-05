import { useNavigate } from '@/app/routing/typed-router'
import { CaptureScreenHost } from '@/masks/capture-screen-host'
import { logistikVerladungScreen } from '@/masks/capture-screens'

/** Verladung aus der ScreenDefinition `logistik/verladung`. */
export default function VerladungListePage(): JSX.Element {
  const navigate = useNavigate()
  return (
    <CaptureScreenHost
      screenId="logistik/verladung"
      fallback={logistikVerladungScreen}
      loading="Verladungen werden geladen…"
      error="Verladungen konnten nicht geladen werden."
      onAction={async (key) => {
        if (key === 'neu') navigate('/verladung/lkw-beladung')
      }}
    />
  )
}
