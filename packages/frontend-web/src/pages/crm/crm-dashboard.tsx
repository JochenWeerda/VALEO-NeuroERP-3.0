import { OverviewPage } from '@/components/mask-builder'
import { OverviewConfig } from '@/components/mask-builder/types'
import { useCRMDashboard } from '@/lib/api/crm'

export default function CRMDashboardPage(): JSX.Element {
  const { data, isLoading } = useCRMDashboard()

  const currentConfig: OverviewConfig = {
    title: 'CRM-Dashboard',
    subtitle: 'Kundenmanagement und Vertriebskennzahlen im Überblick',
    type: 'overview-page',
    cards: data?.kpis ?? [],
    charts: data?.charts ?? [],
    actions: [],
    api: {
      baseUrl: '/api/v1/crm/dashboard',
      endpoints: {
        list: '/api/v1/crm/dashboard'
      }
    },
    permissions: ['crm.read', 'sales.read']
  }

  return (
    <OverviewPage
      config={currentConfig}
      isLoading={isLoading}
    />
  )
}
