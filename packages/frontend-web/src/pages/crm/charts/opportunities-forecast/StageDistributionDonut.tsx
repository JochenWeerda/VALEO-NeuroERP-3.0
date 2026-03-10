import { SimpleDonutChart } from '@/components/charts/SimpleDonutChart'

type StageDistributionPoint = { name: string; value: number }

export default function StageDistributionDonut({ data, colors }: { data: StageDistributionPoint[]; colors: string[] }): JSX.Element {
  return <SimpleDonutChart data={data.map((item, index) => ({ ...item, color: colors[index % colors.length] }))} valueFormatter={(value) => `${value.toLocaleString('de-DE')} EUR`} />
}
