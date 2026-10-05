import { useParams } from '@/app/routing/typed-router'
import { FeedingAnalysisDetail } from '@/features/feed-advice/FeedingAnalysisDetail'

export default function GrundfutteranalyseNativePage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return <FeedingAnalysisDetail analysisId={id} />
}
