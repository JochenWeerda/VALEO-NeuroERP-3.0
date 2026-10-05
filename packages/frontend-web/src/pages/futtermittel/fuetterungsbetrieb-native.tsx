import { useParams } from '@tanstack/react-router'
import { FeedingBusinessDetail } from '@/features/feed-advice/FeedingBusinessDetail'

export default function FuetterungsbetriebNativePage(): JSX.Element {
  const { id } = useParams({ strict: false }) as { id: string }
  return <FeedingBusinessDetail businessId={id} />
}
