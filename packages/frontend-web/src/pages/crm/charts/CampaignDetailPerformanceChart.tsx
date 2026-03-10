import { SimpleLineChart } from '@/components/charts/SimpleLineChart'

type MetricPoint = {
  date: string
  sent: number
  opened: number
  clicked: number
  converted: number
}

interface CampaignDetailPerformanceChartProps {
  chartData: MetricPoint[]
  labels: {
    sent: string
    opened: string
    clicked: string
    converted: string
  }
}

export default function CampaignDetailPerformanceChart({ chartData, labels }: CampaignDetailPerformanceChartProps): JSX.Element {
  return (
    <SimpleLineChart
      data={chartData.map((item) => ({
        label: item.date,
        sent: item.sent,
        opened: item.opened,
        clicked: item.clicked,
        converted: item.converted,
      }))}
      series={[
        { key: 'sent', color: '#8884d8', label: labels.sent },
        { key: 'opened', color: '#82ca9d', label: labels.opened },
        { key: 'clicked', color: '#ffc658', label: labels.clicked },
        { key: 'converted', color: '#ff7300', label: labels.converted },
      ]}
      height={300}
    />
  )
}
