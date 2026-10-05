import { useMemo } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { createScreenContext } from '@/components/mask-builder/governance/screen-context'
import { CaptureScreenHost } from '@/masks/capture-screen-host'
import { fuhrparkFahrzeugeScreen } from '@/masks/capture-screens'

/** Fahrzeugbestand aus der ScreenDefinition `fuhrpark/fahrzeuge`. */
export default function FahrzeugePage(): JSX.Element {
  const navigate = useNavigate()
  const screenContext = useMemo(() => createScreenContext({
    data: {},
    permissions: { granted: [] },
    state: { values: {}, policies: {} },
    actions: {
      'vehicle.create': () => navigate('/fuhrpark/fahrzeug/neu'),
    },
    navigation: { push: (route) => navigate(route) },
  }), [navigate])
  return (
    <CaptureScreenHost
      screenId="fuhrpark/fahrzeuge"
      fallback={fuhrparkFahrzeugeScreen}
      loading="Fahrzeuge werden geladen…"
      error="Fahrzeuge konnten nicht geladen werden."
      screenContext={screenContext}
      onAction={async (key) => {
        if (key === 'neu') navigate('/fuhrpark/fahrzeug/neu')
      }}
    />
  )
}
