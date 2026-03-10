import { SimpleDonutChart } from '@/components/charts/SimpleDonutChart'

type DistributionPoint = { name: string; value: number }

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d']

export default function CampaignTypeDistributionChart({ data }: { data: DistributionPoint[] }): JSX.Element {
  return <SimpleDonutChart data={data.map((item, index) => ({ ...item, color: COLORS[index % COLORS.length] }))} />
}
