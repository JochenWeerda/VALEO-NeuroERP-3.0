import { SimpleDonutChart } from '@/components/charts/SimpleDonutChart'

type DistributionPoint = { name: string; value: number }

export default function CampaignTypeDistributionChart({ data }: { data: DistributionPoint[] }): JSX.Element {
  return <SimpleDonutChart data={data} />
}
