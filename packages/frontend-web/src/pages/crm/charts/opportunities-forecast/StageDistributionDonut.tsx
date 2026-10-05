import { SimpleDonutChart } from '@/components/charts/SimpleDonutChart'

type StageDistributionPoint = { name: string; value: number }

export default function StageDistributionDonut({ data }: { data: StageDistributionPoint[] }): JSX.Element {
  return <SimpleDonutChart data={data} valueFormatter={(value) => `${value.toLocaleString('de-DE')} EUR`} />
}
