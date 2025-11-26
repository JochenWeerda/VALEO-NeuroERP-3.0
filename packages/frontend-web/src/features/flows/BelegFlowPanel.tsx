import { useTranslation } from 'react-i18next'
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

type Node = {
  id: string
  type: string
  number: string
  status: string
}

type NextType = {
  to: string
  label: string
}

type Props = {
  current: Node
  nextTypes: NextType[]
  onCreateFollowUp: (_toType: string) => void
}

/**
 * BelegFlowPanel - Visualisiert Dokumenten-Flow und Folgebeleg-Aktionen
 */
export function BelegFlowPanel({
  current,
  nextTypes,
  onCreateFollowUp,
}: Props): JSX.Element {
  const { t } = useTranslation()
  return (
    <Card className="p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm opacity-70">{t('crud.fields.document')}</div>
          <div className="font-medium">
            {current.type} #{current.number}
          </div>
          <div className="text-sm opacity-70">{t('crud.fields.status')}: {current.status}</div>
        </div>
        <div className="flex gap-2">
          {nextTypes.map(
            (n): JSX.Element => (
              <Button
                key={n.to}
                variant="secondary"
                onClick={(): void => {
                  onCreateFollowUp(n.to)
                }}
              >
                → {n.label}
              </Button>
            )
          )}
        </div>
      </div>
    </Card>
  )
}

