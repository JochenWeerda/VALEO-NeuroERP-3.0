import { useState } from 'react'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { exportActualFeedingsCsv } from '@/lib/api/feeding-actual'

export function FeedingActualPage(): JSX.Element {
  const [feedback, setFeedback] = useState<string | null>(null)

  async function exportCsv(): Promise<void> {
    setFeedback(null)
    try {
      const blob = await exportActualFeedingsCsv()
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = 'ist-fuetterung.csv'
      anchor.click()
      URL.revokeObjectURL(url)
      setFeedback('CSV-Export wurde aus den aktuell berechtigten Ist-Fuetterungen erstellt.')
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    }
  }

  return <div data-testid="feeding-actual-page" data-runtime="native">
    {feedback ? <p className="mb-3 rounded-md border bg-muted px-3 py-2 text-sm" role="status">{feedback}</p> : null}
    <UniversalNativeCockpitPage
      screenId="agrar/feeding-actuals" testId="feeding-actual-worklist"
      permissions={['futtermittel.rations.read', 'futtermittel.rations.update']}
      onAction={(key) => {
        if (key === 'export_csv') void exportCsv()
        if (key === 'open_mobile') window.location.assign('/futtermittel/fuetterungsdokumentation-mobil')
      }}
    />
  </div>
}
