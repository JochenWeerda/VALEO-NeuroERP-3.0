import { useParams } from '@tanstack/react-router'
import { FeedingPlanDetail } from '@/features/feed-advice/FeedingPlanDetail'

export default function FuetterungsplanNativePage(): JSX.Element {
  const { id } = useParams({ strict: false }) as { id: string }
  return <FeedingPlanDetail versionId={id} />
}
